import sys
import time
import httpx
from config import settings
from models import PublicHoliday


def _request_with_retry(client: httpx.Client, url: str) -> httpx.Response:
    last_exc = None

    for attempt in range(settings.max_retries):
        try:
            print(f"Attempt {attempt + 1}: GET {url}")

            response = client.get(url)

            if response.status_code == 429 or response.status_code >= 500:
                raise httpx.HTTPStatusError(
                    f"Retryable status {response.status_code}",
                    request=response.request,
                    response=response,
                )

            response.raise_for_status()
            return response

        except (httpx.HTTPStatusError, httpx.TransportError) as exc:
            last_exc = exc
            wait = 2 ** attempt

            print(
                f"  Request failed ({exc}), "
                f"retrying in {wait}s..."
            )

            time.sleep(wait)

    raise RuntimeError(
        f"Request failed after {settings.max_retries} attempts. "
        f"Last error: {last_exc}"
    ) from last_exc


def get_public_holidays(
    client: httpx.Client,
    year: int,
    country_code: str
) -> list[PublicHoliday]:

    url = (
        f"{settings.nager_base_url}/"
        f"PublicHolidays/{year}/{country_code}"
    )

    response = _request_with_retry(client, url)

    return [
        PublicHoliday.model_validate(item)
        for item in response.json()
    ]


def main(year: int, country_code: str):
    with httpx.Client(
        timeout=settings.request_timeout_seconds
    ) as client:

        print(
            f"Fetching {year} public holidays "
            f"for {country_code}...\n"
        )

        holidays = get_public_holidays(
            client,
            year,
            country_code
        )

        if not holidays:
            print(
                f"No holiday data found for "
                f"{country_code} in {year}."
            )
            return

        for h in holidays:
            print(f"{h.date}  {h.localName} ({h.name})")

        print(
            f"\nTotal: {len(holidays)} public holidays"
        )


if __name__ == "__main__":
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    country_code = sys.argv[2] if len(sys.argv) > 2 else "US"

    main(year, country_code)