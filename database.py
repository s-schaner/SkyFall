import sqlite3
from typing import List, Dict


def init_db(path: str = "skyfall.db") -> None:
    """Create database and tables if they don't exist."""
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            lat REAL,
            lon REAL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS targets (
            node_id TEXT,
            mac TEXT,
            rssi INTEGER,
            freq INTEGER,
            timestamp INTEGER,
            FOREIGN KEY(node_id) REFERENCES nodes(id)
        )
        """
    )
    conn.commit()
    conn.close()


def get_nodes_with_targets(path: str = "skyfall.db") -> List[Dict]:
    """Return nodes and their associated targets."""
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT id, lat, lon FROM nodes")
    nodes = []
    for node_id, lat, lon in cur.fetchall():
        cur.execute(
            "SELECT mac, rssi, freq, timestamp FROM targets WHERE node_id=?",
            (node_id,),
        )
        targets = [
            {
                "mac": mac,
                "rssi": rssi,
                "freq": freq,
                "timestamp": ts,
            }
            for mac, rssi, freq, ts in cur.fetchall()
        ]
        nodes.append({
            "node_id": node_id,
            "gps": {"lat": lat, "lon": lon},
            "targets": targets,
        })
    conn.close()
    return nodes


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage SkyFall database")
    parser.add_argument("--init", action="store_true", help="Initialize database")
    parser.add_argument("--db", default="skyfall.db", help="Path to database")
    args = parser.parse_args()

    if args.init:
        init_db(args.db)
        print(f"Database initialized at {args.db}")

