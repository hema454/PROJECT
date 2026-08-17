import asyncio
import sys

import httpx

from config import settings
from models import ExchangeRateResponse, ConversionResult

MAX_RETRIES = 5
BASE_DELAY_SECONDS = 1.0  # doubles each retry: 1, 2, 4, 8, 16...


async def fetch_rates(client: httpx.AsyncClient, base_currency: str) -> ExchangeRateResponse:
    """
    Fetch latest exchange rates for a base currency, with exponential
    backoff retry on transient failures (timeouts, 5xx, network errors).
    """
    url = f"{settings.exchange_rate_base_url}/latest/{base_currency.upper()}"

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = await client.get(url, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()

            if data.get("result") != "success":
                raise ValueError(f"API returned non-success result: {data.get('result')}")

            return ExchangeRateResponse(**data)

        except (httpx.HTTPStatusError, httpx.TransportError, ValueError) as e:
            last_error = e
            if attempt == MAX_RETRIES:
                break
            delay = BASE_DELAY_SECONDS * (2 ** (attempt - 1))
            print(f"[retry] attempt {attempt}/{MAX_RETRIES} failed ({e}), waiting {delay:.1f}s...")
            await asyncio.sleep(delay)

    raise RuntimeError(f"Failed to fetch exchange rates after {MAX_RETRIES} attempts: {last_error}")


def convert(rates_response: ExchangeRateResponse, target_currency: str, amount: float) -> ConversionResult:
    """Do the actual conversion math using the fetched rates."""
    target_currency = target_currency.upper()

    if target_currency not in rates_response.rates:
        raise ValueError(f"'{target_currency}' not found in available rates.")

    rate = rates_response.rates[target_currency]
    converted = amount * rate

    return ConversionResult(
        base_currency=rates_response.base_code,
        target_currency=target_currency,
        rate=rate,
        amount=amount,
        converted_amount=round(converted, 4),
        last_updated_utc=rates_response.time_last_update_utc,
    )


async def main():
    # Simple CLI usage: python main.py USD INR 100
    # Falls back to sensible defaults if not provided.
    args = sys.argv[1:]
    base = args[0] if len(args) > 0 else "USD"
    target = args[1] if len(args) > 1 else "INR"
    amount = float(args[2]) if len(args) > 2 else 1.0

    async with httpx.AsyncClient() as client:
        print(f"Fetching latest rates for base currency: {base.upper()}...")
        rates_response = await fetch_rates(client, base)

        result = convert(rates_response, target, amount)

        print("\n=== Conversion Result ===")
        print(f"{result.amount} {result.base_currency} = {result.converted_amount} {result.target_currency}")
        print(f"(rate: 1 {result.base_currency} = {result.rate} {result.target_currency})")
        print(f"Last updated (UTC): {result.last_updated_utc}")


if __name__ == "__main__":
    asyncio.run(main())