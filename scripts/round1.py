# scripts/round1.py
import csv
import requests
import json
from uuid import uuid4

SUBMISSIONS_CSV = 'submissions.csv'

def make_task(email, template_brief):
    payload = {
        'email': email,
        'secret': 'the-secret',
        'task': f"captcha-solver-{uuid4().hex[:6]}",
        'round': 1,
        'nonce': uuid4().hex,
        'brief': template_brief,
        'checks': [
            'Repo has MIT license',
            'README.md is professional',
            'Page displays captcha URL passed at ?url=',
            'Page displays solved captcha text within 15 seconds',
        ],
        'evaluation_url': 'https://example.com/eval-callback',
        'attachments': []
    }
    return payload

# Read submissions.csv and POST the generated request to the endpoint listed per row
with open(SUBMISSIONS_CSV) as f:
    r = csv.DictReader(f)
    for row in r:
        endpoint = row['endpoint']
        email = row['email']
        payload = make_task(email, 'Create a captcha solver that handles ?url=... Default to attached sample.')
        resp = requests.post(endpoint, json=payload, timeout=30)
        print(email, endpoint, resp.status_code)
Sai Teja Rachakonda
