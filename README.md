# Market Opportunity OSINT

![tests](https://github.com/<ORG>/<REPO>/actions/workflows/tests.yml/badge.svg)

Evidence-first internal analyst tool for screening export markets using open-source intelligence (OSINT).

## What it does

- Builds a subject-driven research plan (products, signals, risks, HS codes).
- Collects open-source signals (macro, trade, policy, news, tenders).
- Produces deterministic scores with confidence and evidence packs.
- Exports HTML/PDF reports and comparison CSVs.

## Tech Stack

- **App UI**: Streamlit (Python)
- **Backend**: Python services
- **AI**: Gemini (optional, for legacy analysis routes)

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Tests

Micro tests (fast, no network):

```bash
cd backend
pytest -q
```

Integration tests (require external APIs and keys):

```bash
cd backend
RUN_INTEGRATION=1 pytest -q
```
