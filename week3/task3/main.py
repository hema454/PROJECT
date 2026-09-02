import asyncio
import logging

import legacy_chain
import langchain_chain
from config import settings

logging.basicConfig(level=logging.INFO)

TEXT = (
    "John Doe placed an order for 3 units of Product A on 2026-08-15. "
    "Email: john.doe@example.com. Total: $149.99."
)
SCHEMA = (
    "customer_name (string), email (string), order_date (date), "
    "items (list of {product, quantity}), total_amount (number)"
)
REQUIRED_FIELDS = ["customer_name", "email", "order_date", "items", "total_amount"]


async def main() -> None:
    # Equivalence strategy: temperature=0 for determinism, then compare
    # required fields/output between both chains.
    settings.temperature = 0

    legacy_data, legacy_repaired = await legacy_chain.extract(TEXT, SCHEMA)
    lc_data, lc_repaired = await langchain_chain.extract(TEXT, SCHEMA)
    #lc_data["customer_name"] = "Wrong Name"#
    

    print("legacy_chain result   :", legacy_data, "repaired=", legacy_repaired)
    print("langchain_chain result:", lc_data, "repaired=", lc_repaired)

    missing = [f for f in REQUIRED_FIELDS if f not in legacy_data or f not in lc_data]
    if missing:
        raise SystemExit(f"required field(s) missing from one or both outputs: {missing}")

    mismatches = [
        (field, legacy_data[field], lc_data[field])
        for field in REQUIRED_FIELDS
        if legacy_data[field] != lc_data[field]
    ]

    if mismatches:
        print("\nMISMATCH on required fields:")
        for field, legacy_val, lc_val in mismatches:
            print(f"  {field}: legacy={legacy_val!r} langchain={lc_val!r}")
        raise SystemExit(1)

    print(f"\nEquivalence check passed: required fields match — {REQUIRED_FIELDS}")


if __name__ == "__main__":
    asyncio.run(main())