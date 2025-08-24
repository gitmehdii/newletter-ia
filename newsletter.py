import yfinance as yf
import feedparser
import requests
import os

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
    # Vérifier que la clé API est définie
    api_key = os.environ.get("HF_API_KEY")
    if not api_key:
        print("Erreur: HF_API_KEY n'est pas définie dans les variables d'environnement")
        return "⚠️ Clé API Hugging Face manquante."
    
    prompt = f"""
    Voici des infos financières de la semaine :

    📊 Cours boursiers :
    {data}

    📰 Actualités principales :
    {news}

    Résume-les en 3-4 phrases claires et concises, avec des émojis,
    comme une petite newsletter.
    """
    api_url = "https://api-inference.huggingface.co/models/bigscience/bloomz-7b1-mt"
    print("HF_API_KEY =", "***" if api_key else "NOT SET")
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 250}}

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")
        
        # Vérifier le statut de la réponse
        if response.status_code != 200:
            print(f"Erreur API: {response.status_code} - {response.text}")
            return "⚠️ Erreur lors de l'appel à l'API Hugging Face."
        
        # Vérifier si la réponse n'est pas vide
        if not response.text.strip():
            print("Réponse vide de l'API")
            return "⚠️ Réponse vide de l'API Hugging Face."
        
        result = response.json()
        print(f"Parsed JSON: {result}")
        
        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            return result[0]["generated_text"]
        elif isinstance(result, dict) and "error" in result:
            print(f"Erreur dans la réponse: {result['error']}")
            return f"⚠️ Erreur API: {result['error']}"
        else:
            print(f"Format de réponse inattendu: {result}")
            return "⚠️ Format de réponse inattendu de l'API."
            
    except requests.exceptions.JSONDecodeError as e:
        print(f"Erreur de décodage JSON: {e}")
        print(f"Contenu de la réponse: {response.text}")
        return "⚠️ Erreur de décodage de la réponse API."
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête: {e}")
        return "⚠️ Erreur de connexion à l'API Hugging Face."
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return "⚠️ Erreur inattendue lors de la génération du résumé."

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

