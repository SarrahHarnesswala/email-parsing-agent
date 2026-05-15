"""
Gmail IMAP client for fetching unread emails.

Uses Python's built-in imaplib to connect to Gmail via IMAP and fetch unread
emails from the inbox. Emails are returned as raw RFC 2822 strings ready for
parsing by the EmailParserAgent.
"""

import imaplib
import email
import email.policy
import ssl
import sys
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class RawEmail:
    """
    Transport object for raw email data fetched from IMAP.

    This is an internal data structure — the public contract is EmailData
    (from email_parser.py) which is produced after parsing.
    """
    uid: str
    raw_text: str          # Full RFC 2822 message (headers + body)
    imap_date: Optional[str]
    imap_from: Optional[str]


class GmailClient:
    """
    IMAP client for Gmail inbox.

    Connects via TLS (port 993) using app-specific passwords.
    Does not call connect() automatically — explicitly call connect() before
    fetch operations, or use the context manager syntax.
    """

    IMAP_PORT = 993  # Gmail TLS port

    def __init__(
        self,
        gmail_user: Optional[str] = None,
        app_password: Optional[str] = None,
        imap_host: Optional[str] = None,
    ):
        """
        Initialize Gmail IMAP client (not connected yet).

        Reads credentials from environment variables if not supplied:
        - GMAIL_USER (required)
        - GMAIL_APP_PASSWORD (required)
        - IMAP_HOST (optional, defaults to "imap.gmail.com")

        Args:
            gmail_user: Gmail address, or None to read from GMAIL_USER env var
            app_password: App password, or None to read from GMAIL_APP_PASSWORD env var
            imap_host: IMAP hostname, or None to read from IMAP_HOST or default to Gmail

        Raises:
            KeyError: If GMAIL_USER or GMAIL_APP_PASSWORD are not in environment
        """
        self.gmail_user = gmail_user or os.environ["GMAIL_USER"]
        self.app_password = app_password or os.environ["GMAIL_APP_PASSWORD"]
        self.imap_host = imap_host or os.getenv("IMAP_HOST", "imap.gmail.com")
        self._connection: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> None:
        """
        Open TLS connection to Gmail IMAP and authenticate.

        Creates an IMAP4_SSL connection on port 993 and logs in with
        the app-specific password.

        Raises:
            imaplib.IMAP4.error: On authentication failure
            OSError / socket.gaierror: On network failure
        """
        context = ssl.create_default_context()
        self._connection = imaplib.IMAP4_SSL(self.imap_host, self.IMAP_PORT, ssl_context=context)
        self._connection.login(self.gmail_user, self.app_password)

    def disconnect(self) -> None:
        """
        Gracefully close the IMAP connection.

        Safe to call even if not connected or already disconnected.
        """
        if self._connection is not None:
            try:
                self._connection.close()
                self._connection.logout()
            except Exception:
                pass
            self._connection = None

    def fetch_unread_emails(self, limit: int = 10) -> list[RawEmail]:
        """
        Fetch the N most recent unread emails from INBOX.

        Process:
        1. Selects INBOX in readonly mode (does not mark emails as read)
        2. Searches for UNSEEN messages
        3. Takes the last min(limit, 50) UIDs (most recent first)
        4. For each UID: fetches RFC822 body and parses headers/body
        5. Builds a plain-text representation for the LLM
        6. Returns list of RawEmail objects, most recent first

        Args:
            limit: Maximum number of unread emails to return (default 10).
                   Clamped to 50 to prevent accidental full-inbox dumps.

        Returns:
            List of RawEmail objects, most recent first.
            Returns empty list if no unread emails.

        Raises:
            RuntimeError: If called before connect()
            imaplib.IMAP4.error: On IMAP protocol error (e.g., select fails)
        """
        if self._connection is None:
            raise RuntimeError("Not connected. Call connect() first.")

        limit = min(limit, 50)  # Clamp to prevent accidents

        self._connection.select("INBOX", readonly=True)

        _, data = self._connection.search(None, "UNSEEN")
        uid_list = data[0].split()  # List of bytes

        if not uid_list:
            return []

        selected_uids = uid_list[-limit:]  # Last N UIDs (most recent)
        selected_uids.reverse()  # Reverse to most-recent-first

        results = []
        for uid_bytes in selected_uids:
            try:
                uid_str = uid_bytes.decode()
                _, msg_data = self._connection.fetch(uid_bytes, "(RFC822)")

                if not msg_data or not msg_data[0]:
                    continue

                raw_bytes = msg_data[0][1]
                msg = email.message_from_bytes(raw_bytes, policy=email.policy.default)

                from_header = msg.get("From", "")
                date_header = msg.get("Date", "")
                subject_header = msg.get("Subject", "")

                parts = [
                    f"From: {from_header}",
                    f"To: {msg.get('To', '')}",
                    f"Subject: {subject_header}",
                    f"Date: {date_header}",
                    "",
                ]

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            parts.append(part.get_content())
                            break
                else:
                    parts.append(msg.get_content())

                raw_text = "\n".join(parts)

                results.append(RawEmail(
                    uid=uid_str,
                    raw_text=raw_text,
                    imap_date=date_header,
                    imap_from=from_header,
                ))
            except UnicodeDecodeError as e:
                sys.stderr.write(f"[warn] Failed to decode email UID {uid_bytes.decode() if uid_bytes else '?'}: {e}\n")
                continue
            except Exception as e:
                sys.stderr.write(f"[warn] Failed to parse email UID {uid_bytes.decode() if uid_bytes else '?'}: {type(e).__name__}: {e}\n")
                continue

        return results

    def __enter__(self) -> "GmailClient":
        """Context manager entry: connect."""
        self.connect()
        return self

    def __exit__(self, *_) -> None:
        """Context manager exit: disconnect."""
        self.disconnect()
