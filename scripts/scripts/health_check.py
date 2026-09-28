#!/usr/bin/env python3
"""Check an HTTP(S) endpoint; exit 0 for a 2xx response, 1 otherwise."""
import argparse
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def check(url, timeout):
    try:
        with urlopen(Request(url, headers={"User-Agent": "wisecow-healthcheck/1.0"}),
                     timeout=timeout) as response:
            status = response.status
            return 200 <= status < 300, f"HTTP {status}"
    except HTTPError as error:
        return False, f"HTTP {error.code}"
    except (URLError, TimeoutError, OSError) as error:
        return False, f"connection error: {error}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Full http:// or https:// URL, ideally a readiness endpoint")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()
    if not args.url.startswith(("http://", "https://")) or args.timeout <= 0:
        parser.error("use an HTTP(S) URL and a positive timeout")
    healthy, detail = check(args.url, args.timeout)
    print(f"{'UP' if healthy else 'DOWN'}: {detail} - {args.url}")
    return 0 if healthy else 1


if __name__ == "__main__":
    sys.exit(main())
