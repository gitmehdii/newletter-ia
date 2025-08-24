import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yfinance as yf
import feedparser
import requests

# ------------------------------
# Étape 1 : Récupération des données financières
# ------------------------------
def fetch_market_data():
    tickers = ["TSLA", "AAPL", "^GSPC"]  # Tesla, Apple, S&P500
    data = {}
    for t in tickers:
        stock = yf.Ticker(t)
        hist = stock.history(period="5d")  # Dernière semaine
        if not hist.empty:
            last_close = hist["Close"].iloc[-1]
            data[t] = round(last_close, 2)
    return data

# ------------------------------
# Étape 2 : Récupération des news
# ------------------------------
def fetch_news():
    url = "https://www.reuters.com/rssFeed/businessNews"
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:3]:  # Prendre 3 actus
        articles.append(f"- {entry.title}")
    return articles

# ------------------------------
# Étape 3 : Génération du résumé par IA (HuggingFace)
# ------------------------------
def generate_summary(data, news):
    prompt = f"""
    Voici des infos financières de la semaine :

    📊 Cours boursiers :
    {data}

    📰 Actualités principales :
    {news}

    Résume-les en 3-4 phrases claires et concises, avec des émojis,
    comme une petite newsletter.
    """

    api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {os.environ['HF_API_KEY']}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 250}}

    response = requests.post(api_url, headers=headers, json=payload)
    result = response.json()

    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    else:
        return "⚠️ Impossible de générer un résumé cette semaine."

# ------------------------------
# Étape 4 : Mise en forme email
# ------------------------------
def build_email(content):
    email_sender = os.environ["EMAIL_ADDRESS"]
    email_receiver = os.environ["EMAIL_TO"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📩 Newsletter Finance - Mardi"
    msg["From"] = email_sender
    msg["To"] = email_receiver

    html_content = f"""
    <html>
      <body>
        <h2>📩 Newsletter Finance</h2>
        <p>{content}</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_content, "html"))
    return msg

# ------------------------------
# Étape 5 : Envoi de l’email
# ------------------------------
def send_email(msg):
    email_sender = os.environ["EMAIL_ADDRESS"]
    email_password = os.environ["EMAIL_PASSWORD"]
    email_receiver = os.environ["EMAIL_TO"]

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_receiver, msg.as_string())

# ------------------------------
# Étape principale
# ------------------------------
def main():
    data = fetch_market_data()
    news = fetch_news()
    summary = generate_summary(data, news)
    msg = build_email(summary)
    send_email(msg)

if __name__ == "__main__":
    main()

