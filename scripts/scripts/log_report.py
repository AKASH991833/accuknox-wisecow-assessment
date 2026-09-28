#!/usr/bin/env python3
"""Report request totals, 404 count, popular paths and IPs from combined access logs."""
import argparse
from collections import Counter
import re

LINE = re.compile(r'^(\S+) \S+ \S+ \[[^]]+\] "(?:\S+) (\S+) [^\"]+" (\d{3}) (?:\S+)(?: .*)?$')


def summarize(lines):
    paths, ips = Counter(), Counter()
    total = errors_404 = skipped = 0
    for line in lines:
        match = LINE.match(line.rstrip("\n"))
        if not match:
            skipped += 1
            continue
        ip, path, status = match.groups()
        total += 1
        paths[path] += 1
        ips[ip] += 1
        errors_404 += status == "404"
    return total, errors_404, skipped, paths, ips


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", help="Combined-format Apache/Nginx access log")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()
    if args.top < 1:
        parser.error("--top must be positive")
    with open(args.log, encoding="utf-8", errors="replace") as stream:
        total, missing, skipped, paths, ips = summarize(stream)
    print(f"Requests: {total}\n404 responses: {missing}\nSkipped malformed lines: {skipped}")
    for label, values in (("Paths", paths), ("IPs", ips)):
        print(f"Top {label}:")
        for value, count in values.most_common(args.top):
            print(f"  {count:>5} {value}")


if __name__ == "__main__":
    main()
