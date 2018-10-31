# Raiden Network hands-on workshop @ devcon4

This is the repo for the Devcon4 Raiden workshop.
Below you'll find a list of links and information needed to interactively participate in the workshop.

### Prerequisites:
- Access to an Ethereum Kovan RPC endpoint
    - I.e. through [Infura](https://infura.io/login)
- A Kovan account and KETH. Use our [simple script](TODO) for this.
    - You can also request KETH from a [faucet](https://faucet.kovan.network/)
- [Raiden binaries](TODO)
    - Once the binaries are downloaded follow [this guide](https://raiden-network.readthedocs.io/en/latest/overview_and_guide.html#installation) to install them.
- We will use [gitter](https://gitter.im/raiden-network/devcon4-workshop) for communicating addresses etc. during the workshop
- Optionally mint some [Devcon4TestTokens](https://kovan.etherscan.io/address/0x396764f15ed1467883a9a5b7d42acfb788cd1826#code)


### Running Raiden:
Once Raiden is installed it's time to fire it up. This is done with the following command:
```
./raiden-binary --eth-rpc-endpoint YOUR_RPC_ENDPOINT --keystore-path keystore --network-id kovan
```

With Raiden now up and running, you can check out the WebUI at [localhost:5001](localhost:5001).
You can now either `join` the [Devcon4TestTokens](https://kovan.etherscan.io/address/0x396764f15ed1467883a9a5b7d42acfb788cd1826#code) network or open a channel with somebody else from the workshop who also posted their address in the [gitter](https://gitter.im/raiden-network/devcon4-workshop).
