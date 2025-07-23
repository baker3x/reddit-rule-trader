import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import List

# Load Gmail credentials from environment variables
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
RECIPIENT = os.getenv("EMAIL_TO")  # your email

def send_trade_alert(tickers: List[str], hold_days: int = 3):
    if not tickers:
        return

    subject = "[Trade Alert] Buy Signal Detected"
    body = f"Trade Date: Today\n\nHold Period: {hold_days} trading 
days\n\nTickers:\n"
    for t in tickers:
        body += f"- {t}\n"
    body += "\nStrategy: Fixed window, no stop-loss or TP"

    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as 
server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, RECIPIENT, msg.as_string())

if __name__ == "__main__":
    send_trade_alert(["AAPL", "TSLA", "PLTR"])


