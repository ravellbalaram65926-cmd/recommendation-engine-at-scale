import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.main import DEFAULT_INPUT, build_recommendations


class RecommendationPipelineTests(unittest.TestCase):
    def test_incremental_load_is_repeatable_and_excludes_consumed_items(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "recommendations.sqlite"
            self.assertEqual(build_recommendations(DEFAULT_INPUT, database), 3)
            self.assertEqual(build_recommendations(DEFAULT_INPUT, database), 3)
            connection = sqlite3.connect(database)
            try:
                pairs = connection.execute("SELECT user_id, item_id FROM recommendations").fetchall()
                interactions = connection.execute(
                    "SELECT user_id, item_id FROM raw_interactions"
                ).fetchall()
            finally:
                connection.close()
            self.assertTrue(set(pairs).isdisjoint(interactions))


if __name__ == "__main__":
    unittest.main()
