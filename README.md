# Burnaby Verification Dashboard

Standalone Streamlit deployment package for the Burnaby zoning verification
dashboard.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run dashboard/streamlit_app.py
```

## Streamlit Cloud

Use:

```text
Main file path: dashboard/streamlit_app.py
```

The dashboard is read-only. It loads verifier output JSON from:

```text
outputs/burnaby_r1_slim_pipeline5_registry/
```
