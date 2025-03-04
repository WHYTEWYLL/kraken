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
