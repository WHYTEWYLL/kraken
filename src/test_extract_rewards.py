import os
import sqlite3
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from extract_rewards import setup_database, store_rewards

# Set up a test database
DB_PATH = "polygon_rewards.db"


class TestPolygonRewards(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Runs once before all tests. Creates a fresh test database."""
        setup_database()

    def test_unique_transaction_hash_constraint(self):
        """Test that inserting duplicate transaction hashes does not create duplicates."""
        address = "0x1234567890abcdef"
        rewards = [
            {
                "validator_id": 1,
                "amount": "100",
                "total": "1000",
                "event": "ClaimRewards",
                "transaction_hash": "0xabc123",
                "block_number": 100000,
                "inserted_at": datetime.now().isoformat(),
            }
        ]

        # Insert the same reward twice
        store_rewards(address, rewards)
        store_rewards(address, rewards)

        # Check that only one entry exists
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM reward_claims WHERE transaction_hash = ?",
                ("0xabc123",),
            )
            count = cursor.fetchone()[0]

        self.assertEqual(
            count, 1, "Duplicate transaction hashes should not be inserted."
        )


if __name__ == "__main__":
    unittest.main()
