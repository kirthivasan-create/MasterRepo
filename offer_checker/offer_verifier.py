"""
Simple tool for operations team to compare active offers with application recommendations.

Usage example:
    python offer_verifier.py \
        --offers active_offers.csv \
        --response app_response.json \
        --email-config smtp.yml \
        --notify-to ops@example.com,biz@example.com

The script prints summary counts and will email the business team if any active offers
were not recommended by the application.

Input formats:
  * offers CSV: each line contains an offer ID (header optional). Only first column is used.
  * response JSON: expected to be a list of offer IDs (strings) or an object with
    an "offers" array.

The SMTP configuration file (YAML or JSON) should contain keys such as:

    server: smtp.example.com
    port: 587
    use_tls: true
    username: myuser
    password: mypass
    from: notifier@example.com

"""

import csv
import json
import argparse
import smtplib
from email.message import EmailMessage
from typing import List, Dict


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def load_offers(file_path: str) -> List[str]:
    """Load active offer ids from a CSV file."""
    offers: List[str] = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row:
                continue
            offers.append(str(row[0]).strip())
    return offers


def load_response(file_path: str) -> List[str]:
    """Load recommendation result from a JSON file returned by the REST service."""
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict):
        # e.g. {"offers": ["O1","O2"]}
        data = data.get("offers", [])

    # flatten and cast to str for comparison
    return [str(item) for item in data]


# ---------------------------------------------------------------------------
# Comparison logic
# ---------------------------------------------------------------------------

def compare_offers(active: List[str], recommended: List[str]) -> Dict[str, object]:
    """Return summary of comparison between the active list and recommendations."""
    active_set = set(active)
    recommended_set = set(recommended)

    returned = {
        "total_active": len(active_set),
        "recommended_count": len(active_set & recommended_set),
        "not_recommended": sorted(list(active_set - recommended_set)),
        "extra_recommended": sorted(list(recommended_set - active_set)),
    }
    return returned


# ---------------------------------------------------------------------------
# Notification helpers
# ---------------------------------------------------------------------------

def send_email(smtp_conf: dict, subject: str, body: str, to_addrs: List[str]) -> None:
    """Send a simple text email using SMTP settings from configuration dict."""
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_conf.get("from")
    msg["To"] = ", ".join(to_addrs)
    msg.set_content(body)

    server = smtp_conf.get("server")
    port = smtp_conf.get("port", 25)
    use_tls = smtp_conf.get("use_tls", False)
    username = smtp_conf.get("username")
    password = smtp_conf.get("password")

    with smtplib.SMTP(server, port) as smtp:
        if use_tls:
            smtp.starttls()
        if username and password:
            smtp.login(username, password)
        smtp.send_message(msg)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify that active offers were recommended by the application."
    )
    parser.add_argument(
        "--offers", required=True, help="Path to CSV file containing active offer IDs."
    )
    parser.add_argument(
        "--response",
        required=True,
        help="Path to JSON file returned by REST service with recommended offers.",
    )
    parser.add_argument(
        "--email-config",
        help="YAML or JSON file containing SMTP configuration for notifications.",
    )
    parser.add_argument(
        "--notify-to",
        help="Comma-separated list of email addresses to notify when there are failures.",
    )
    parser.add_argument(
        "--skip-email",
        action="store_true",
        help="Print results but do not attempt to send an email even if there are failures.",
    )

    args = parser.parse_args()

    active_offers = load_offers(args.offers)
    recommended = load_response(args.response)

    summary = compare_offers(active_offers, recommended)

    print(f"Total active offers: {summary['total_active']}")
    print(f"Total recommended offers: {summary['recommended_count']}")
    print(
        f"Not recommended ({len(summary['not_recommended'])}): {summary['not_recommended']}"
    )

    if summary["not_recommended"] and not args.skip_email:
        if args.email_config and args.notify_to:
            try:
                import yaml

                with open(args.email_config, encoding="utf-8") as f:
                    smtp_conf = yaml.safe_load(f)
            except ModuleNotFoundError:  # fallback to JSON if PyYAML not installed
                with open(args.email_config, encoding="utf-8") as f:
                    smtp_conf = json.load(f)

            send_email(
                smtp_conf,
                subject="Unrecommended offer alert",
                body="The following active offers were not recommended by the application:\n"
                + "\n".join(summary["not_recommended"]),
                to_addrs=[addr.strip() for addr in args.notify_to.split(",")],
            )
            print("Notification email sent.")
        else:
            print("No email configuration or recipients provided; skipping notification.")


if __name__ == "__main__":
    main()
