# Polygon Reward Extractor

A Python application that extracts Polygon staking reward claim history from Ethereum contracts and stores it in a SQLite database. Built to run in a Docker container with unit tests included.

## Task

```
2. Polygon is an L2 built from Ethereum. We can track Polygon staking activity by reading from contracts on the Ethereum chain. Write some Python code to extract the reward claim history for any arbitrary address by reading the data from the relevant Polygon contracts on Ethereum. Store the results in SQLite or any SQL database.

a. Should build and run in a Docker container.
b. Bonus points for good comments and unit tests.
c. You may find these references useful:
   i. https://docs.polygon.technology/pos/reference/contracts/genesis-contracts/#parent-chain-ethereum-mainnet
   ii. https://github.com/0xPolygon/polygon-docs/blob/main/docs/pos/reference/contracts/stakingmanager.md
   iii. https://github.com/0xPolygon/pos-contracts/blob/main/docs/autogen/src/contracts/staking/StakingInfo.sol/contract.StakingInfo.md
```

## Prerequisites

- Docker
- An Ethereum RPC URL (e.g., from Infura or Alchemy)

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd polygon-reward-extractor
```

### 2. Environment Variables

Ensure you have an `.env` file in the project root with the following:

```ini
ETH_RPC_URL=<your_ethereum_rpc_url>
```

### 3. Build and Run

To build and run the container:

```bash
docker-compose up --build
```

It is recommended to run the container multiple times to verify full functionality.

To stop the container:

```bash
docker-compose down
```

### 4. Running Tests

To execute unit tests:

```bash
docker-compose run polygon-reward-extractor python -m unittest discover -s test -v
```
