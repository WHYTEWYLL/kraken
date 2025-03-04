import os
import json
import sqlite3
import time
from web3 import Web3
from datetime import datetime
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

# Validate and load Ethereum RPC URL
ETH_RPC_URL = os.getenv("ETH_RPC_URL")
if not ETH_RPC_URL:
    raise ValueError("ETH_RPC_URL is missing or not set correctly.")

# Polygon StakeManager contract address
STAKE_MANAGER_ADDRESS = "0xa59c847bd5ac0172ff4fe912c5d29e5a71a7512b"
NFT_CONTRACT_ADDRESS = "0x47cbe25bbdb40a774cc37e1da92d10c2c7ec897f"

# Database path from environment variable
DB_PATH = os.getenv("DB_PATH", "polygon_rewards.db")

# Load ABI files
with open("./abi/stake_manager_abi.json", "r") as abi_file:
    STAKE_MANAGER_ABI = json.load(abi_file)
with open("./abi/nft.json", "r") as nft_abi_file:
    NFT_MANAGER_ABI = json.load(nft_abi_file)


def retry(exceptions, tries=3, delay=1, backoff=2):
    """Retry decorator to handle network errors."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < tries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"Error: {e}, retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= backoff
                    attempt += 1
            return None

        return wrapper

    return decorator


def get_web3_instance():
    """Establish a Web3 connection."""
    w3 = Web3(Web3.HTTPProvider(ETH_RPC_URL))
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Ethereum node")
    return w3


def setup_database():
    """Initialize SQLite database and create necessary tables."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reward_claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL,
                validator_id REAL,
                amount TEXT,
                total TEXT,
                event TEXT,
                transaction_hash TEXT UNIQUE,
                block_number REAL,
                inserted_at TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nft_owners (
                token_id INTEGER PRIMARY KEY,
                owner_address TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_nft_owner ON nft_owners (owner_address)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_reward_tx ON reward_claims (transaction_hash)"
        )
        conn.commit()


def check_existing_owners():
    """Check if the nft_owners table has data and return a random owner if it does."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM nft_owners")
        count = cursor.fetchone()[0]

        if count > 0:
            cursor.execute(
                "SELECT owner_address FROM nft_owners ORDER BY RANDOM() LIMIT 1"
            )
            return cursor.fetchone()[0]
        return None


@retry(Exception, tries=3, delay=2)
def get_all_owners(collection_size=127):
    """Fetch all NFT owners from the contract and store in the database efficiently."""
    w3 = get_web3_instance()
    token_contract = w3.eth.contract(
        address=w3.to_checksum_address(NFT_CONTRACT_ADDRESS), abi=NFT_MANAGER_ABI
    )
    owners = []

    for token_id in range(1, collection_size + 1):
        try:
            owner = token_contract.functions.ownerOf(token_id).call()
            owners.append((token_id, owner))
        except Exception as e:
            print(f"Error fetching owner for token {token_id}: {e}")

    with sqlite3.connect("polygon_rewards.db") as conn:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO nft_owners (token_id, owner_address) VALUES (?, ?)", owners
        )
        conn.commit()

    return {token_id: owner for token_id, owner in owners}


def get_validator_id(owner_address):
    """Fetch validator ID for a given owner address."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT token_id FROM nft_owners WHERE owner_address = ?", (owner_address,)
        )
        result = cursor.fetchone()
        if result:
            return result[0]
        print(f"Validator ID not found for owner {owner_address} in database.")
    return None


def store_rewards(address, rewards):
    """Store reward claim history in the database."""

    with sqlite3.connect("polygon_rewards.db") as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT OR IGNORE  INTO reward_claims (address, validator_id, amount, total, event, transaction_hash, block_number, inserted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    address,
                    r["validator_id"],
                    r["amount"],
                    r["total"],
                    r["event"],
                    r["transaction_hash"],
                    r["block_number"],
                    r["inserted_at"],
                )
                for r in rewards
            ],
        )
        conn.commit()

        # Retrieve count of inserted records
        cursor.execute("SELECT COUNT(*) FROM reward_claims")
        total_records = cursor.fetchone()[0]

        print(
            f"Inserted {len(rewards)} new reward claims for {address}. Total records in database: {total_records}"
        )


@retry(Exception, tries=3, delay=2)
def get_reward_claim_history(validator_id, start_block=0, end_block=None):
    """Fetch reward claim events from StakeManager."""
    w3 = get_web3_instance()
    contract = w3.eth.contract(
        address=w3.to_checksum_address(STAKE_MANAGER_ADDRESS), abi=STAKE_MANAGER_ABI
    )

    latest_block = w3.eth.block_number
    end_block = end_block or latest_block

    try:
        logs = contract.events.ClaimRewards.get_logs(
            argument_filters={"validatorId": validator_id},
            from_block=start_block,
            to_block=end_block,
        )

        return [
            {
                "validator_id": log.args.validatorId,
                "amount": str(log.args.amount),
                "total": str(log.args.totalAmount),
                "event": log.event,
                "transaction_hash": log.transactionHash.hex(),
                "block_number": log.blockNumber,
                "inserted_at": datetime.now().isoformat(),
            }
            for log in logs
        ]
    except Exception as e:
        print(f"Error fetching reward claim history: {e}")
        return []


def main():
    setup_database()
    selected_owner = check_existing_owners()

    if not selected_owner:
        print("No NFT owners found in the database. Fetching from blockchain...")
        owners = get_all_owners()
        if not owners:
            print("Failed to fetch NFT owners.")
            return
        selected_owner = list(owners.values())[0]

    print(f"Selected Owner: {selected_owner}")
    validator_id = get_validator_id(selected_owner)

    if validator_id:
        rewards = get_reward_claim_history(validator_id)
        if rewards:
            store_rewards(selected_owner, rewards)
            print(f"Stored {len(rewards)} reward claims for {selected_owner}.")
        else:
            print("No rewards found.")
    else:
        print("Validator ID not found.")


if __name__ == "__main__":
    main()
