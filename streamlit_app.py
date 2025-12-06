import streamlit as st
import imaplib
import smtplib
import ssl
from email.message import EmailMessage
from email import message_from_bytes
from typing import List, Tuple


# ========================
# Helper functions
# ========================

def fetch_recent_emails(
    imap_host: str,
    imap_port: int,
    email_address: str,
    password: str,
    mailbox: str = "INBOX",
    limit: int = 10,
) -> List[Tuple[str, str, str, str]]:
    """
    Fetch recent emails from an IMAP server.

    Returns a list of tuples: (uid, from, subject, date, snippet)
    """
    mails = []
    imap = None
    try:
        imap = imaplib.IMAP4_SSL(imap_host, imap_port)
        imap.login(email_address, password)
        imap.select(mailbox)

        status, data = imap.search(None, "ALL")
        if status != "OK":
            raise Exception("Failed to search mailbox")

        all_uids = data[0].split()
        if not all_uids:
            return []

        # Get last N UIDs
        recent_uids = all_uids[-limit:]

        for uid in reversed(recent_uids):  # reverse to show newest first
            status, msg_data = imap.fetch(uid, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = message_from_bytes(raw_email)

            from_ = msg.get("From", "(no From)")
            subject = msg.get("Subject", "(no Subject)")
            date = msg.get("Date", "(no Date)")

            # Get a text snippet
            snippet = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition") or "")
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            snippet = part.get_payload(decode=True).decode(
                                part.get_content_charset() or "utf-8",
                                errors="ignore",
                            )
                        except Exception:
                            snippet = ""
                        break
            else:
                try:
                    snippet = msg.get_payload(decode=True).decode(
                        msg.get_content_charset() or "utf-8",
                        errors="ignore",
                    )
                except Exception:
                    snippet = ""

            snippet = (snippet or "").strip().replace("\r", "").replace("\n", " ")
            if len(snippet) > 300:
                snippet = snippet[:300] + "..."

            mails.append((uid.decode(), from_, subject, date, snippet))

    finally:
        if imap is not None:
            try:
                imap.close()
            except Exception:
                pass
            imap.logout()

    return mails


def send_email_smtp(
    smtp_host: str,
    smtp_port: int,
    email_address: str,
    password: str,
    to_address: str,
    subject: str,
    body: str,
    use_ssl: bool = True,
    use_starttls: bool = False,
):
    """
    Send an email via SMTP.
    """
    msg = EmailMessage()
    msg["From"] = email_address
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(body)

    if use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
            server.login(email_address, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if use_starttls:
                context = ssl.create_default_context()
                server.starttls(context=context)
            server.login(email_address, password)
            server.send_message(msg)


# ========================
# Streamlit UI
# ========================

st.set_page_config(page_title="IMAP/SMTP Mail Client", page_icon="📧", layout="centered")

st.title("📧 Simple IMAP/SMTP Mail Client")

st.markdown(
    """
This app lets you:

- Log into an **IMAP** server to read recent emails  
- Use an **SMTP** server to send emails  

> **Gmail note:** Use an **App Password** or OAuth2.  
> Regular Gmail passwords are blocked for IMAP/SMTP.
"""
)

# Sidebar: provider presets
st.sidebar.header("Email Provider")
provider = st.sidebar.selectbox("Preset", ["Custom", "Gmail"])

if provider == "Gmail":
    default_imap_host = "imap.gmail.com"
    default_imap_port = 993
    default_smtp_host = "smtp.gmail.com"
    default_smtp_port_ssl = 465
    default_smtp_port_tls = 587
else:
    default_imap_host = ""
    default_imap_port = 993
    default_smtp_host = ""
    default_smtp_port_ssl = 465
    default_smtp_port_tls = 587

tabs = st.tabs(["IMAP - Read Mail", "SMTP - Send Mail"])

# ========================
# IMAP TAB
# ========================
with tabs[0]:
    st.subheader("IMAP Login & Read Emails")

    with st.form("imap_form"):
        col1, col2 = st.columns(2)
        with col1:
            imap_host = st.text_input("IMAP Host", value=default_imap_host, placeholder="imap.example.com")
            imap_port = st.number_input("IMAP Port", value=default_imap_port, step=1)
        with col2:
            email_address_imap = st.text_input("Email Address", placeholder="you@example.com")
            password_imap = st.text_input("Password / App Password", type="password")

        mailbox = st.text_input("Mailbox", value="INBOX")
        limit = st.number_input("Number of recent emails", min_value=1, max_value=100, value=10, step=1)

        submitted_imap = st.form_submit_button("Connect & Fetch Emails")

    if submitted_imap:
        if not all([imap_host, imap_port, email_address_imap, password_imap]):
            st.error("Please fill in all required IMAP fields.")
        else:
            with st.spinner("Connecting to IMAP and fetching emails..."):
                try:
                    emails = fetch_recent_emails(
                        imap_host=str(imap_host).strip(),
                        imap_port=int(imap_port),
                        email_address=email_address_imap.strip(),
                        password=password_imap,
                        mailbox=mailbox.strip() or "INBOX",
                        limit=int(limit),
                    )

                    if not emails:
                        st.info("No emails found in this mailbox.")
                    else:
                        st.success(f"Fetched {len(emails)} messages.")
                        for uid, from_, subject, date, snippet in emails:
                            with st.expander(f"{subject}  |  {from_}"):
                                st.write(f"**UID:** `{uid}`")
                                st.write(f"**From:** {from_}")
                                st.write(f"**Date:** {date}")
                                st.write("---")
                                st.write(snippet or "_No preview available_")
                except Exception as e:
                    st.error(f"Error fetching emails: {e}")

# ========================
# SMTP TAB
# ========================
with tabs[1]:
    st.subheader("SMTP Login & Send Email")

    with st.form("smtp_form"):
        col1, col2 = st.columns(2)
        with col1:
            smtp_host = st.text_input("SMTP Host", value=default_smtp_host, placeholder="smtp.example.com")
            security = st.selectbox("Security", ["SSL (recommended)", "STARTTLS", "None"])
        with col2:
            if security == "SSL (recommended)":
                smtp_port = st.number_input("SMTP Port", value=default_smtp_port_ssl, step=1)
            elif security == "STARTTLS":
                smtp_port = st.number_input("SMTP Port", value=default_smtp_port_tls, step=1)
            else:
                smtp_port = st.number_input("SMTP Port", value=25, step=1)

        email_address_smtp = st.text_input("Email Address (From)", placeholder="you@example.com")
        password_smtp = st.text_input("Password / App Password", type="password")

        to_address = st.text_input("To", placeholder="recipient@example.com")
        subject = st.text_input("Subject")
        body = st.text_area("Body", height=200)

        submitted_smtp = st.form_submit_button("Send Email")

    if submitted_smtp:
        if not all([smtp_host, smtp_port, email_address_smtp, password_smtp, to_address]):
            st.error("Please fill in all required SMTP fields (host, port, email, password, to).")
        else:
            use_ssl = security == "SSL (recommended)"
            use_starttls = security == "STARTTLS"

            with st.spinner("Sending email..."):
                try:
                    send_email_smtp(
                        smtp_host=str(smtp_host).strip(),
                        smtp_port=int(smtp_port),
                        email_address=email_address_smtp.strip(),
                        password=password_smtp,
                        to_address=to_address.strip(),
                        subject=subject.strip() or "(no subject)",
                        body=body,
                        use_ssl=use_ssl,
                        use_starttls=use_starttls,
                    )
                    st.success("Email sent successfully ✅")
                except Exception as e:
                    st.error(f"Error sending email: {e}")
                    st.info(
                        "If you're using Gmail, make sure:\n"
                        "- 2FA is enabled, and\n"
                        "- You're using an App Password (not your normal password)."
                    )
