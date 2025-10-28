import os
import sys
from sqlalchemy import text

# Ensure project root is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.database_config import sync_engine


def reset_alembic_version() -> None:
    with sync_engine.begin() as connection:
        try:
            connection.execute(text("DELETE FROM alembic_version"))
        except Exception:
            # If table doesn't exist yet, ignore
            pass


if __name__ == "__main__":
    reset_alembic_version()
    print("alembic_version cleared (if existed)")


