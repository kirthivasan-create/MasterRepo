# Offer Verifier

This small utility is intended for operations teams to verify that every active
offer is being recommended by the application (based on the daily REST
service response).

## Features

* Loads a list of active offers from a CSV file
* Loads a recommendation list from a JSON file returned by the service
* Compares the two and prints counts
* Optionally emails business/ops team when any active offers are *not*
  recommended

## Usage

```sh
python offer_verifier.py \
    --offers active_offers.csv \
    --response service_response.json \
    --email-config smtp.yml \
    --notify-to ops@example.com,biz@example.com
```

If `--skip-email` is supplied the script will only print results and will not
try to send an email.

### File formats

* **active_offers.csv** – CSV where each row contains a single offer ID. The
  first column is used; a header row is optional.
* **service_response.json** – JSON ``list`` of offer IDs, or an object with an
  ``offers`` key holding the list.
* **smtp.yml** – YAML or JSON file with SMTP settings (server, port,
  username/password, `from` address, etc.).

Example SMTP file (YAML):

```yaml
server: smtp.internal.company.local
port: 587
use_tls: true
username: notifier
password: secret
from: "noreply@company.com"
```

## Scheduling

On Windows you can use Task Scheduler to call the script once per day, or you
can wrap it with your existing orchestration framework.  The basic command is
shown above; make sure to provide absolute paths when scheduling.

## Extensibility

* Adapt parsers if your data source is a database or a different format
* Add logging, metrics, or attach to monitoring as needed
* Hook the notification section into your corporate e-mail or ticketing system

---

This project is intentionally minimal; it can be extended later based on
feedback from business or the application team.