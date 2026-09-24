"""
Email Automation
-----------------
Sends personalized emails to a list of recipients using a template with
{placeholder} fields filled in from a CSV file. Defaults to --dry-run so
nothing sends until you explicitly opt in.

Template file format (first line is the subject):
    Subject: Hello {name}!

    Hi {name}, thanks for being a customer at {company}.

Usage:
    python send_emails.py --recipients recipients.csv --template template.txt --dry-run
    python send_emails.py --recipients recipients.csv --template template.txt --send

SMTP credentials are read from environment variables (never hardcode these):
    EMAIL_SENDER, EMAIL_PASSWORD, SMTP_SERVER (default: smtp.gmail.com), SMTP_PORT (default: 587)
"""

import argparse
import logging
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def load_recipients(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Recipients file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    if "email" not in df.columns:
        raise ValueError("Recipients CSV must have an 'email' column")
    return df


def load_template(template_path: Path) -> tuple[str, str]:
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    text = template_path.read_text()
    lines = text.split("\n", 1)
    if not lines[0].startswith("Subject:"):
        raise ValueError("Template must start with a 'Subject: ...' line")

    subject = lines[0].removeprefix("Subject:").strip()
    body = lines[1].strip() if len(lines) > 1 else ""
    return subject, body


def render(text: str, fields: dict) -> str:
    try:
        return text.format(**fields)
    except KeyError as e:
        raise ValueError(f"Template uses placeholder {e} which is missing from a recipient row") from e


def build_message(sender: str, recipient_email: str, subject: str, body: str, attachment: Path = None) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.set_content(body)

    if attachment:
        data = attachment.read_bytes()
        msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=attachment.name)

    return msg


def send_emails(recipients_path: Path, template_path: Path, dry_run: bool = True, attachment: Path = None) -> dict:
    """
    Send (or preview) personalized emails to every recipient in the CSV.

    Returns a summary dict: total recipients, sent count, failed recipients.
    """
    recipients = load_recipients(recipients_path)
    subject_template, body_template = load_template(template_path)

    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))

    if not dry_run and (not sender or not password):
        raise ValueError("EMAIL_SENDER and EMAIL_PASSWORD environment variables must be set to actually send")

    sent, failed = 0, []
    connection = None
    if not dry_run:
        connection = smtplib.SMTP(smtp_server, smtp_port)
        connection.starttls()
        connection.login(sender, password)

    try:
        for _, row in recipients.iterrows():
            fields = row.to_dict()
            subject = render(subject_template, fields)
            body = render(body_template, fields)

            if dry_run:
                log.info("[DRY RUN] To: %s | Subject: %s", fields["email"], subject)
            else:
                msg = build_message(sender, fields["email"], subject, body, attachment)
                try:
                    connection.send_message(msg)
                    log.info("Sent to %s", fields["email"])
                    sent += 1
                except Exception as e:
                    log.error("Failed to send to %s: %s", fields["email"], e)
                    failed.append(fields["email"])
    finally:
        if connection:
            connection.quit()

    return {
        "total_recipients": len(recipients),
        "sent": sent if not dry_run else len(recipients),
        "failed": failed,
    }


def main():
    parser = argparse.ArgumentParser(description="Send personalized bulk emails from a CSV + template.")
    parser.add_argument("--recipients", required=True, help="CSV file with an 'email' column plus any template fields")
    parser.add_argument("--template", required=True, help="Text file: first line 'Subject: ...', rest is the body")
    parser.add_argument("--attachment", default=None, help="Optional file to attach to every email")
    parser.add_argument("--send", action="store_true", help="Actually send emails (default is dry-run preview)")
    args = parser.parse_args()

    try:
        attachment = Path(args.attachment) if args.attachment else None
        summary = send_emails(Path(args.recipients), Path(args.template), dry_run=not args.send, attachment=attachment)
        log.info("\nTotal recipients: %d", summary["total_recipients"])
        if args.send:
            log.info("Sent: %d", summary["sent"])
            if summary["failed"]:
                log.info("Failed: %s", ", ".join(summary["failed"]))
        else:
            log.info("(Dry run - no emails were sent. Use --send to actually send.)")
    except (FileNotFoundError, ValueError) as e:
        log.error("Error: %s", e)
    except Exception as e:
        log.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
