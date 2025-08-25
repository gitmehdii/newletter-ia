import yfinance as yf
import feedparser
import requests
import os
from transformers import pipeline

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

    # Charger un modèle de résumé gratuit (BART)
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    # Le modèle n’aime pas les textes trop longs → tronquons si besoin
    text = prompt[:1024]

    summary = summarizer(text, max_length=150, min_length=40, do_sample=False)

    return summary[0]['summary_text']

# ------------------------------
# Étape principale
# ------------------------------
def main():
    data = fetch_market_data()
    news = fetch_news()
    summary = generate_summary(data, news)

    # Affichage dans la console
    print("📩 --- Résumé Finance --- 📩\n")
    print(summary)
    print("\n📩 --------------------- 📩")

if __name__ == "__main__":
    main()

