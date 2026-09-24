import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from send_emails import load_recipients, load_template, render, build_message, send_emails


def _write(path: Path, content: str):
    path.write_text(content)


def test_load_recipients_requires_email_column(tmp_path):
    _write(tmp_path / "r.csv", "name,phone\nRahul,12345\n")
    with pytest.raises(ValueError):
        load_recipients(tmp_path / "r.csv")


def test_load_template_parses_subject_and_body(tmp_path):
    _write(tmp_path / "t.txt", "Subject: Hi {name}\n\nBody text here")
    subject, body = load_template(tmp_path / "t.txt")
    assert subject == "Hi {name}"
    assert body == "Body text here"


def test_load_template_requires_subject_line(tmp_path):
    _write(tmp_path / "t.txt", "No subject line here")
    with pytest.raises(ValueError):
        load_template(tmp_path / "t.txt")


def test_render_fills_placeholders():
    result = render("Hello {name} from {company}", {"name": "Rahul", "company": "Acme"})
    assert result == "Hello Rahul from Acme"


def test_render_missing_field_raises_error():
    with pytest.raises(ValueError):
        render("Hello {missing_field}", {"name": "Rahul"})


def test_build_message_sets_headers_and_body():
    msg = build_message("me@example.com", "you@example.com", "Subject line", "Body text")
    assert msg["From"] == "me@example.com"
    assert msg["To"] == "you@example.com"
    assert msg["Subject"] == "Subject line"
    assert "Body text" in msg.get_content()


def test_dry_run_does_not_require_credentials(tmp_path, monkeypatch):
    monkeypatch.delenv("EMAIL_SENDER", raising=False)
    monkeypatch.delenv("EMAIL_PASSWORD", raising=False)
    _write(tmp_path / "r.csv", "name,email\nRahul,rahul@example.com\n")
    _write(tmp_path / "t.txt", "Subject: Hi {name}\n\nHello {name}")

    summary = send_emails(tmp_path / "r.csv", tmp_path / "t.txt", dry_run=True)

    assert summary["total_recipients"] == 1
    assert summary["sent"] == 1


def test_send_without_credentials_raises_error(tmp_path, monkeypatch):
    monkeypatch.delenv("EMAIL_SENDER", raising=False)
    monkeypatch.delenv("EMAIL_PASSWORD", raising=False)
    _write(tmp_path / "r.csv", "name,email\nRahul,rahul@example.com\n")
    _write(tmp_path / "t.txt", "Subject: Hi {name}\n\nHello {name}")

    with pytest.raises(ValueError):
        send_emails(tmp_path / "r.csv", tmp_path / "t.txt", dry_run=False)


def test_missing_recipients_file_raises_error(tmp_path):
    _write(tmp_path / "t.txt", "Subject: Hi\n\nBody")
    with pytest.raises(FileNotFoundError):
        send_emails(tmp_path / "does_not_exist.csv", tmp_path / "t.txt", dry_run=True)
