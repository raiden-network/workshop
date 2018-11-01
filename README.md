# Raiden Network hands-on workshop @ devcon4

This is the repo for the Devcon4 Raiden workshop.
Below you'll find a list of links and information needed to interactively participate in the workshop.

### Prerequisites:
- Access to an Ethereum Kovan RPC endpoint
    - For example through [Infura](https://infura.io/login)
- A Kovan account and KETH. We've created a small script that generates an account and sends KETH and tokens to it with just one simple command. Please see the onboarding script below for instructions.
    - You can also request KETH from a [faucet](https://faucet.kovan.network/)
- [Raiden MacOS binaries](https://raiden-nightlies.ams3.digitaloceanspaces.com/raiden-nightly-2018-10-31T06-43-08-v0.15.1.dev7%2Bg29188326-macOS.zip)
- [Linux Raiden binaries](https://raiden-nightlies.ams3.digitaloceanspaces.com/raiden-nightly-2018-10-31T06-32-56-v0.15.1.dev7%2Bg29188326-linux.tar.gz)
- If you're on Windows we recommend that you install Raiden for Windows Subsystem for Linux (WSL)
    - Once the binaries are downloaded follow [this guide](https://raiden-network.readthedocs.io/en/latest/overview_and_guide.html#installation) to install them.
- We will use [gitter](https://gitter.im/raiden-network/devcon4-workshop) for communicating addresses etc. during the workshop

### On boarding:
We've created a simple script that generates an address and sends KETH and Devcon4TestTokens to the generated address. Follow these simple steps:

#### macOS instructions:
- Download the [binary file](https://raiden-nightlies.ams3.digitaloceanspaces.com/onboarder-macOS.zip)
- Unzip the file:
```
unzip onboarder-macOS.zip
```
- And run it:
```
./onboarder
```

#### Linux instructions:
- Download the [binary file](https://raiden-nightlies.ams3.digitaloceanspaces.com/onboarder-linux.tar.gz)
- Unzip the file:
```
tar -xvzf onboarder-linux.tar.gz
```
- And run it:
```
./onboarder
```

### Running Raiden:
Once Raiden is installed it's time to fire it up. This is done with the following command:
```
./raiden-binary --eth-rpc-endpoint YOUR_RPC_ENDPOINT \
    --keystore-path keystore --network-id kovan \
    --environment-type development
```

With Raiden now up and running, you can check out the WebUI at [localhost:5001](localhost:5001).
You can now either `join` the [Devcon4TestTokens](https://kovan.etherscan.io/address/0x396764f15ed1467883a9a5b7d42acfb788cd1826#code) network or open a channel with somebody else from the workshop who also posted their address in the [gitter](https://gitter.im/raiden-network/devcon4-workshop).

### API commands:

#### Open channels
To start with we want to open channels with four already existing nodes. Run the following four commands to open four channels:

**Node 1**
```
curl -i -X PUT http://localhost:5001/api/1/channels \
    -H 'Content-Type: application/json' --data-raw \
    '{"partner_address": "0xFa047E7e2Dbc605CE1047d67468371a7bf67E461", \
    "token_address": "0x396764f15ed1467883A9a5B7D42AcFb788CD1826", \
    "total_deposit": 10000000000000000000}'
```

**Node 2**
```
curl -i -X PUT http://localhost:5001/api/1/channels \
    -H 'Content-Type: application/json' --data-raw \
    '{"partner_address": "0x8d5b7238925d9C934681430D22A1566dc4d0f9e7", \
    "token_address": "0x396764f15ed1467883A9a5B7D42AcFb788CD1826", \
    "total_deposit": 10000000000000000000}'
```

**Node 3**
```
curl -i -X PUT http://localhost:5001/api/1/channels \
    -H 'Content-Type: application/json' --data-raw \
    '{"partner_address": "0x13c0b391A87c1f3eAC9a5a7C17FaC6DFff83b84f", \
    "token_address": "0x396764f15ed1467883A9a5B7D42AcFb788CD1826", \
    "total_deposit": 10000000000000000000}'
```

**Node 4**
```
curl -i -X PUT http://localhost:5001/api/1/channels \
    -H 'Content-Type: application/json' --data-raw \
    '{"partner_address": "0x7A96aeA5a95FF6bCDbB7B591f2A7B36faDA4a7e3", \
    "token_address": "0x396764f15ed1467883A9a5B7D42AcFb788CD1826", \
    "total_deposit": 10000000000000000000}'
```

#### Deposit
If you ever need to top up a channel, you can use the following command:
```
curl -i -X PATCH http://localhost:5001/api/1/channels/ \
0x396764f15ed1467883A9a5B7D42AcFb788CD1826/ADDRESS_OF_PARTNER \
-H 'Content-Type: application/json' \
--data-raw '{"total_deposit": 15000000000000000000}'
```

#### Make payments
To make payments, choose any of the above addresses that you opened a channel with and do the following:
```
curl -i -X POST http://localhost:5001/api/1/payments/ \
0x396764f15ed1467883A9a5B7D42AcFb788CD1826/ADDRESS_OF_RECEIVER \
-H 'Content-Type: application/json' --data-raw '{"amount": 100000}'
```

Feel free to change the amounts of the payments.

### Other resources
- [API documentation](https://raiden-network.readthedocs.io/en/latest/rest_api.html)
- [Getting Started with Raiden API](https://raiden-network.readthedocs.io/en/latest/api_walkthrough.html)
