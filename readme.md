# Polygon Reward Extractor

A Python application that extracts Polygon staking reward claim history from Ethereum contracts and stores it in a SQLite database. Built to run in a Docker container with unit tests included.

## Features

- Queries Polygon StakeManager contract on Ethereum
- Stores reward claim history in SQLite
- Containerized with Docker
- Includes unit tests

## Prerequisites

- Docker
- An Ethereum RPC URL (e.g., from Infura or Alchemy)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd polygon-reward-extractor
   ```

## Task

```
2. Polygon is an L2 built from Ethereum. We can track polygon staking activity by reading from contracts on the Eth chain. Write some code in Python to extract the reward claim history for any one arbitrary address by reading the data from the relevant polygon contracts on Eth. Store the results in sqlite or any sql db.
a. Should build and run in a docker
b. Bonus points for good comments and unit tests.
c. You may find these references useful:
i. https://docs.polygon.technology/pos/reference/contracts/genesis-contract s/#parent-chain-ethereum-mainnet
ii. https://github.com/0xPolygon/polygon-docs/blob/main/docs/pos/reference/ contracts/stakingmanager.md
iii. https://github.com/0xPolygon/pos-contracts/blob/main/docs/autogen/src/c ontracts/staking/StakingInfo.sol/contract.StakingInfo.md
```
