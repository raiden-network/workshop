from gevent.monkey import patch_all  # isort:skip # noqa
patch_all()  # isort:skip # noqa

import json
import os
import time
from datetime import datetime
from typing import Set, Union

import click
import structlog
from eth_utils import encode_hex, is_address, to_checksum_address
from flask import Flask, Response, request
from gunicorn.app.base import BaseApplication
from redis import StrictRedis
from web3 import HTTPProvider, Web3
from web3.gas_strategies.time_based import fast_gas_price_strategy

from raiden.accounts import Account
from raiden.log_config import configure_logging
from raiden.network.rpc.client import JSONRPCClient, check_address_has_code
from raiden.network.rpc.smartcontract_proxy import ContractProxy
from raiden.utils.typing import TransactionHash
from raiden_contracts.constants import CONTRACT_CUSTOM_TOKEN
from raiden_contracts.contract_manager import ContractManager, contracts_precompiled_path

REDIS_KEY_KNOWN_ADDR = 'onboarding:known_addr'
REDIS_KEY_KNOWN_CLIENT = 'onboarding:known_client'
log = structlog.get_logger('onboarding_server')


class GunicornApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            if key not in self.cfg.settings or value is None:
                continue
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def _get_token_ctr(client, token_address) -> ContractProxy:
    token_contract = ContractManager(contracts_precompiled_path()).get_contract(CONTRACT_CUSTOM_TOKEN)
    check_address_has_code(client, token_address, 'Token')
    return client.new_contract_proxy(token_contract['abi'], token_address)


def wait_for_txs(
        client_or_web3: Union[Web3, JSONRPCClient],
        txhashes: Set[TransactionHash],
        timeout: int = 360,
):
    if isinstance(client_or_web3, Web3):
        web3 = client_or_web3
    else:
        web3 = client_or_web3.web3
    start = time.monotonic()
    outstanding = False
    txhashes = set(txhashes)
    while txhashes and time.monotonic() - start < timeout:
        remaining_timeout = timeout - (time.monotonic() - start)
        if outstanding != len(txhashes) or int(remaining_timeout) % 10 == 0:
            outstanding = len(txhashes)
            log.debug(
                "Waiting for tx confirmations",
                outstanding=outstanding,
                timeout_remaining=int(remaining_timeout),
            )
        for txhash in txhashes.copy():
            tx = web3.eth.getTransactionReceipt(txhash)
            if tx and tx['blockNumber'] is not None:
                status = tx.get('status')
                if status is not None and status == 0:
                    raise RuntimeError(f"Transaction {encode_hex(txhash)} failed.")
                txhashes.remove(txhash)
            time.sleep(.1)
        time.sleep(1)
    if len(txhashes):
        txhashes_str = ', '.join(encode_hex(txhash) for txhash in txhashes)
        raise RuntimeError(
            f"Timeout waiting for txhashes: {txhashes_str}",
        )


@click.command()
@click.option('--keystore-file', required=True, type=click.Path(exists=True, dir_okay=False))
@click.password_option('--password', envvar='ACCOUNT_PASSWORD', required=True)
@click.option('--eth-rpc-url', required=True)
@click.option('--token-address', required=True)
@click.option('--bind-addr', default='127.0.0.1:8088', show_default=True)
@click.option('--public-url')
@click.option('--redis-host', default='localhost', show_default=True)
@click.option('--redis-port', default=6379, show_default=True)
@click.option('--faucet-amount-eth', default=1 * 10 ** 17, show_default=True)
@click.option('--faucet-amount-tokens', default=1000 * 10 ** 18, show_default=True)
@click.option('--faucet-timeout', default=60 * 60 * 24 * 7, show_default=True)
@click.option(
    '--log-path',
    default=os.getcwd(),
    type=click.Path(file_okay=False, dir_okay=True, exists=True),
)
@click.option('--tx-timeout', default=360, show_default=True)
def main(
    keystore_file,
    password,
    eth_rpc_url,
    token_address,
    bind_addr,
    public_url,
    redis_host,
    redis_port,
    faucet_amount_eth,
    faucet_amount_tokens,
    faucet_timeout,
    log_path,
    tx_timeout,
):
    log_file_name = f'onboarding-server.{datetime.now().isoformat()}.log'
    log_file_name = os.path.join(log_path, log_file_name)
    click.secho(f'Writing log to {log_file_name}', fg='yellow')
    configure_logging(
        {'': 'INFO', 'raiden': 'DEBUG', 'onboarding_server': 'DEBUG'},
        debug_log_file_name=log_file_name,
        _first_party_packages=frozenset(['raiden', 'onboarding_server']),
    )

    with open(keystore_file, 'r') as keystore:
        account = Account(json.load(keystore), password, keystore_file)
        log.info("Using account", account=to_checksum_address(account.address))
    client = JSONRPCClient(
        Web3(HTTPProvider(eth_rpc_url)),
        privkey=account.privkey,
        gas_price_strategy=fast_gas_price_strategy,
    )

    token_ctr = _get_token_ctr(client, token_address)

    if public_url is None:
        public_url = f'http://{bind_addr}/'

    redis = StrictRedis(redis_host, redis_port)

    app = Flask(__name__)

    @app.route('/', methods=['GET'])
    def index():
        return f'''
            <html>
            <body style=" background: linear-gradient(90deg, #fca09a, #fcccd3, #ffcc9d, #98ddad, #81d7ec, #a0aaed);">
            <div style="float:left; width: 80%">
                <h1>Raiden Hands on Workshop @ devcon iv</h1>
                <h2>Kovan ETH & {token_ctr.contract.call().name()} faucet</h2>
            </div>
            <div style="float:right; width: 20%">
                <img src="https://raiden.network/assets/logo-black.png" />
            </div> 
            <p style="clear: both; overflow: hidden;">
                To request KETH and tokens send a <code>POST</code> request to <code>{public_url}</code> with a JSON body
                containing <code>{{"address": "&lt;eth-address&gt;", "client_hash": "&lt;client-auth-hash&gt;"}}</code>.
            </p>
        '''

    @app.route('/', methods=['POST'])
    def faucet():
        if not request.json:
            log.info('Invlid request', remote=request.remote_addr)
            return Response(
                '{"result": "error", "error": "Invalid request"}',
                status=406,
                content_type='application/json',
            )
        address = request.json.get('address')
        client_hash = request.json.get('client_hash')
        if not address or not is_address(address) or not client_hash:
            log.info('Invlid request.', remote=request.remote_addr, address=address, client_hash=client_hash)
            return Response(
                '{"result": "error", "error": "Invalid request. address or client_hash missing."}',
                status=406,
                content_type='application/json',
            )
        address = to_checksum_address(address)
        address_key = f'{REDIS_KEY_KNOWN_ADDR}:{address}'
        client_key = f'{REDIS_KEY_KNOWN_CLIENT}:{client_hash}'
        if redis.get(address_key) is not None or redis.get(client_key) is not None:
            log.info('Quota exceeded', address=address, client_hash=client_hash)
            return Response(
                '{"result": "error", "error": "quota exceeded"}',
                status=429,
                content_type='application/json',
            )
        log.info('Fauceting', target=address)
        txhashes = {
            client.send_transaction(address, faucet_amount_eth),
            token_ctr.transact('mintFor', faucet_amount_tokens, address)
        }
        try:
            wait_for_txs(client, txhashes, timeout=tx_timeout)
        except RuntimeError as ex:
            return Response(
                json.dumps({'result': 'error', 'error': str(ex)}),
                status=503,
                content_type='application/json',
            )
        log.info('Successfully fauceted', address=address)
        redis.set(address_key, '1', ex=faucet_timeout)
        redis.set(client_key, '1', ex=faucet_timeout)
        return Response('{"result": "success"}', content_type='application/json')

    GunicornApplication(app, {'bind': bind_addr, 'worker_class': 'gevent'}).run()


if __name__ == "__main__":
    main()
