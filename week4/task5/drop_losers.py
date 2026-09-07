import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "task4"))

from db_variants import drop_table  # noqa: E402

if __name__ == "__main__":
    for table in ["chunks_a", "chunks_b"]:
        drop_table(table)
        print(f"dropped {table}")
    print("kept: chunks_c")