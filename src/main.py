"""ELT demo: deduplicate interactions and build a SQL popularity baseline."""

import argparse
import csv
import sqlite3
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "raw" / "sample_interactions.csv"
DEFAULT_DB = ROOT / "data" / "recommendations.sqlite"


def build_recommendations(input_path: Path, database: Path, top_n: int = 2) -> int:
    if top_n <= 0:
        raise ValueError("top_n must be positive")
    database.parent.mkdir(parents=True, exist_ok=True)
    with input_path.open(newline="", encoding="utf-8") as source:
        interactions = list(csv.DictReader(source))
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS raw_interactions (
                user_id TEXT NOT NULL, item_id TEXT NOT NULL,
                rating REAL NOT NULL, event_time TEXT NOT NULL,
                PRIMARY KEY (user_id, item_id)
            );
            CREATE TABLE IF NOT EXISTS recommendations (
                user_id TEXT NOT NULL, rank INTEGER NOT NULL,
                item_id TEXT NOT NULL, score REAL NOT NULL,
                PRIMARY KEY (user_id, rank)
            );
            """
        )
        connection.executemany(
            """
            INSERT INTO raw_interactions VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, item_id) DO UPDATE SET
                rating = excluded.rating, event_time = excluded.event_time
            WHERE excluded.event_time > raw_interactions.event_time
            """,
            (
                (r["user_id"], r["item_id"], float(r["rating"]), r["event_time"])
                for r in interactions
            ),
        )
        connection.executescript(
            """
            CREATE TEMP TABLE item_popularity AS
            SELECT item_id, AVG(rating) AS score, COUNT(*) AS interactions
            FROM raw_interactions
            GROUP BY item_id;
            """
        )
        connection.execute("DELETE FROM recommendations")
        connection.execute(
            """
            INSERT INTO recommendations
            WITH ranked_candidates AS (
                SELECT users.user_id, popularity.item_id, popularity.score,
                       ROW_NUMBER() OVER (
                           PARTITION BY users.user_id
                           ORDER BY popularity.score DESC, popularity.interactions DESC,
                                    popularity.item_id
                       ) AS rank
                FROM (SELECT DISTINCT user_id FROM raw_interactions) AS users
                CROSS JOIN item_popularity AS popularity
                WHERE NOT EXISTS (
                    SELECT 1 FROM raw_interactions AS seen
                    WHERE seen.user_id = users.user_id AND seen.item_id = popularity.item_id
                )
            )
            SELECT user_id, rank, item_id, score
            FROM ranked_candidates
            WHERE rank <= ?
            """,
            (top_n,),
        )
        return connection.execute("SELECT COUNT(*) FROM recommendations").fetchone()[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--top-n", type=int, default=2)
    args = parser.parse_args()
    count = build_recommendations(args.input, args.database, args.top_n)
    print(f"Built {count} user-item recommendations in {args.database}")


if __name__ == "__main__":
    main()
