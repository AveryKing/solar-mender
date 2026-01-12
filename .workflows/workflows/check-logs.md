---
description: Retrieve the most recent logs from the Cloud Run service to debug issues or verify execution.
---

# Check Cloud Run Logs

Use this workflow to see what "Phantom Apollo" is doing in production.

## 1. Fetch Recent Logs
Run the following `gcloud` command to get the last 50 log entries, focusing on application output (stdout/stderr):

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=phantom-apollo" \
  --limit 50 \
  --format="table(timestamp, textPayload, jsonPayload.message)" \
  --order desc
```

## 2. Interpret Common Patterns
- **"Server listening on port 8080"**: Normal cold start.
- **"POST /interactions 200"**: Discord successfully hit the endpoint.
- **"Application did not respond" (Discord UI)** + **No Logs**: Cold start timeout or URL verification failure.
- **"Hunt Failed"**: Internal agent crash (check the stack trace in the log).

## 3. Filter for Errors
If the noise is too high, run this to see only CRITICAL/ERROR logs:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=phantom-apollo AND severity>=ERROR" --limit 20
```
