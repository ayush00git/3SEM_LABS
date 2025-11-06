# Program: Using Python with Internet Services
# Demonstrates sending email and reading news headlines.

import smtplib
from email.mime.text import MIMEText
import requests

# ---------- Sending Email ----------
def send_email():
    sender = "youremail@gmail.com"
    password = "yourpassword"       # Use App Password if using Gmail with 2FA
    receiver = "receiveremail@gmail.com"

    # Create the email content
    msg = MIMEText("Hello! This is a test email sent using Python.")
    msg["Subject"] = "Test Email from Python"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        # Connect to Gmail’s SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        server.login(sender, password)
        server.send_message(msg)
        print("✅ Email sent successfully!")
        server.quit()
    except Exception as e:
        print("❌ Error sending email:", e)


# ---------- Reading News ----------
def read_news():
    print("\n📰 Latest News Headlines:")
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=demo"  # demo API key
    try:
        response = requests.get(url)
        data = response.json()
        articles = data.get("articles", [])
        for article in articles[:5]:  # show first 5 headlines
            print("-", article["title"])
    except Exception as e:
        print("❌ Error reading news:", e)


# ---------- Main Program ----------
if __name__ == "__main__":
    print("Using Python with Internet Services:\n")
    send_email()
    read_news()
