# scripts/evaluate.py
# For each repo entry, run checks and write results
import requests
import subprocess
import time

# Example: Playwright check via `npx playwright test` or use playwright python bindings


def check_pages_url(pages_url):
    # simple http check
    r = requests.get(pages_url, timeout=10)
    return r.status_code == 200
