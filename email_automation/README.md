# Email Automation

Sends personalized bulk emails using a CSV of recipients + a template with
`{placeholder}` fields. Defaults to a safe dry-run preview — nothing sends
until you explicitly pass `--send`.

![demo](../assets/demos/email_automation.gif)

## Why
Sending personalized emails one by one (or copy-pasting into a mail client)
doesn't scale. This mail-merges a CSV against a template and sends each
recipient a personalized email in one command.

## Setup

Credentials are read from environment variables — **never hardcoded** in the
script:

```bash
export EMAIL_SENDER="you@gmail.com"
export EMAIL_PASSWORD="your-app-password"   # use an app password, not your real password
export SMTP_SERVER="smtp.gmail.com"          # optional, this is the default
export SMTP_PORT="587"                        # optional, this is the default
```

## Template format

First line is the subject, rest is the body. Any CSV column can be used as a
`{placeholder}`:

```
Subject: Hello {name}, quick update from {company}

Hi {name},

Thanks for being a valued partner at {company}.
```

## Usage

```bash
# Preview what would be sent (default — safe, no emails sent)
python send_emails.py --recipients recipients.csv --template template.txt

# Actually send
python send_emails.py --recipients recipients.csv --template template.txt --send

# With an attachment
python send_emails.py --recipients recipients.csv --template template.txt --send --attachment invoice.pdf
```

## Run tests

```bash
python -m pytest tests/
```


Tests never make real network/SMTP calls — they test template rendering,
message building, and the dry-run path directly.
cd email_automation
pip3 install -r requirements.txt
python3 send_emails.py --recipients sample_data/recipients.csv --template sample_data/template.txt

cqbcstzlxevueyif

export EMAIL_SENDER="gaurmayank871@gmail.com" export EMAIL_PASSWORD="cqbcstzlxevueyif"
(.venv) ➜  email_automation echo $EMAIL_SENDER echo $EMAIL_PASSWORD
gaurmayank871@gmail.com echo cqbcstzlxevueyif
(.venv) ➜  email_automation python3 send_emails.py --recipients sample_data/recipients.csv --template sample_data/template.txt --send
Sent to gaurmayank781@gmail.com
Sent to priya@example.com
Sent to amit@example.com

Total recipients: 3
Sent: 3