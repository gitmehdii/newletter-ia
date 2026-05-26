import requests
from openai import OpenAI
import yfinance as yf
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

OPENAI_API_KEY = os.environ.get("OPEN_AI_API_KEY")
client = OpenAI(
  api_key= OPENAI_API_KEY
)

API_KEY = os.environ.get("NEWSAPI_API_KEY")

ASSETS = {
    # Tech US
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Alphabet": "GOOGL",
    "Amazon": "AMZN",
    "Meta": "META",
    "Tesla": "TSLA",

    # Finance & Investissement
    "Berkshire Hathaway": "BRK-B",
    "JPMorgan Chase": "JPM",
    "Goldman Sachs": "GS",

    # Énergie & Industrie
    "Saudi Aramco": "2222.SR",
    "ExxonMobil": "XOM",
    "Shell": "SHEL",

    # Santé & Pharma
    "Johnson & Johnson": "JNJ",
    "Pfizer": "PFE",

    # Consommation & Luxe
    "Coca-Cola": "KO",
    "Procter & Gamble": "PG",
    "LVMH": "MC.PA",
    "TotalEnergies": "TTE.PA",
    "Airbus": "AIR.PA",

    # Semi-conducteurs & Asie
    "TSMC": "TSM",
    "Samsung": "005930.KQ",

    # Indices & Crypto
    "S&P 500": "^GSPC",
    "CAC 40": "^FCHI",
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
}

def get_financials(ticker):
    """Récupère les données financières de base depuis yfinance"""
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "currentPrice": info.get("currentPrice"),
        "marketCap": info.get("marketCap"),
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
        "dividendYield": info.get("dividendYield"),
        "previousClose": info.get("previousClose"),
    }

def get_news_yfinance(ticker="TSLA", limit=5):
    t = yf.Ticker(ticker)
    news = t.news

    results = []
    for item in news[:limit]:
        title = item["content"]["title"]
        pub_date = item["content"]["pubDate"]

        url = item["content"]["canonicalUrl"]["url"]
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            article_text = "\n".join([p.get_text() for p in paragraphs])
        else:
            article_text = "⚠️ Impossible de récupérer le contenu."

        result = f"📰 {title}\n📅 Publié le: {pub_date}\n\n{article_text}\n"
        results.append(result)

    return "\n\n".join(results)


def get_news_newsapi(query, n=5):
    """Récupère les derniers articles NewsAPI"""
    if not API_KEY:
        raise ValueError("NEWSAPI_API_KEY is required")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": n,
    }
    headers = {"X-Api-Key": API_KEY}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        r = response.json()
    except requests.RequestException as exc:
        raise RuntimeError("Failed to fetch data from NewsAPI") from exc
    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError("Invalid response format from NewsAPI") from exc
    
    articles = []
    for art in r.get("articles", []):
        articles.append({
            "title": art["title"],
            "publishedAt": art["publishedAt"],
            "description": art["description"],
            "url": art["url"]
        })
    return articles

def build_financial_summary(name, ticker):
    """Construit un résumé brut pour GPT"""
    fin = get_financials(ticker)
    news = get_news_newsapi(name, n=4)
    yfinance_news = get_news_yfinance(ticker, limit=4)

    summary = f"### {name} ({ticker})\n"
    summary += f"- Prix actuel : {fin['currentPrice']}\n"
    summary += f"- Capitalisation : {fin['marketCap']}\n"
    summary += f"- PER (TTM) : {fin['trailingPE']}\n"
    summary += f"- PER (Forward) : {fin['forwardPE']}\n"
    summary += f"- Dividende : {fin['dividendYield']}\n"
    summary += f"- Clôture précédente : {fin['previousClose']}\n\n"

    summary += "**Articles récents :**\n"
    for art in news:
        date = datetime.fromisoformat(art["publishedAt"].replace("Z", "+00:00")).strftime("%Y-%m-%d")
        summary += f"- ({date}) {art['title']} – {art['description']} [Lien]({art['url']})\n"

    return summary + yfinance_news

test = client.responses.create(
     model="gpt-4o-mini",
     input= "bonjour, ça va ?")
print("⏳ Searching articles...")
article_for_prompt = ""
for name, ticker in ASSETS.items():
        article_for_prompt += "\n" + build_financial_summary(name, ticker)
print("✅ Articles successfully retrieved")
# Config SMTP via secrets GitHub
smtp_server = "smtp.gmail.com"
smtp_port = 587
username = os.environ.get("EMAIL_ADDRESS")
password = os.environ.get("EMAIL_PASSWORD")

from_email = username
to_emails = ["azouzmehdi603@gmail.com", "azouz.ms@gmail.com"]

# Construire le message
msg = MIMEMultipart("alternative")
msg["Subject"] = "📩 Newsletter Marchés Financiers"
msg["From"] = from_email
msg["To"] = ", ".join(to_emails)


# Exemple d'utilisation
print("⏳ Generating email...")
response = client.responses.create(
  model="gpt-4o-mini",
  input="""Tu es un analyste financier senior. Je vais te donner des articles issus de ma veille (NewsAPI).
Ta tâche : produire UNIQUEMENT un email en **HTML pur** (aucun texte hors des balises HTML), prêt à coller dans un client mail.

Contraintes strictes :
- Pas de JavaScript, pas d’images externes, pas de CSS externe.
- Utilise un style inline minimal compatible email.
- Police sûre : system-ui, Arial, sans-serif.
- Largeur max 600px, avec blocs visuellement différenciés (fonds gris clairs, encadrés, marges).
- Titres clairs avec un peu de couleur (#333 ou #0056b3).
- Rédige des phrases complètes et concises : 3–5 lignes par section, pas seulement des puces.

Structure obligatoire :
- Titre principal du mail (📩).
- Bloc "État général du marché" (📊) → résumé global (3–5 lignes).
- Bloc "Secteurs & entreprises marquants" (🏦/💻) → liste + petits paragraphes pour chaque point.
- Bloc "Prix & mouvements notables" (💵) → chiffres s’ils sont présents, sinon indique “(pas de chiffre mentionné)”.
- Bloc "Ambiance & facteurs clés" (💡) → contexte macro/émotion des marchés (3–4 lignes).
- Conclusion synthétique (✅) → 2–3 phrases avec une tonalité claire et un conseil général.
- Footer discret (date, source: “Synthèse basée sur votre veille NewsAPI”, note légale courte).
- Dans le footer, remplace {{DATE}} par la date du jour au format "Lundi 26 août 2025" (en français, complet).

Important :
- Si certains chiffres ne sont pas présents, écris “(pas de chiffre mentionné)”, n’invente rien.
- Ton formel, clair, type note d’investissement.
- Le HTML doit être complet : <html>, <head>, <body>.
- Rends le rendu agréable avec encadrés et espacements (marges internes, séparateurs).

Voici le template HTML à utiliser et à remplir :

<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Newsletter Hebdo</title>
</head>
<body style="margin:0;padding:20px;background:#f4f6f8;font-family:system-ui, Arial, sans-serif;">

  <!-- Container -->
  <div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 6px rgba(0,0,0,0.1);border:1px solid #e6e9ef;">

    <!-- Header -->
    <div style="background:#0056b3;padding:24px;text-align:center;color:#fff;">
      <h1 style="margin:0;font-size:22px;">📩 Newsletter Hebdomadaire</h1>
      <p style="margin:6px 0 0;font-size:14px;color:#e2e6ef;">Votre synthèse marchés & entreprises</p>
    </div>

    <!-- Etat général du marché -->
    <div style="padding:20px;background:#fafcfe;">
      <h2 style="margin:0 0 10px;color:#0056b3;font-size:18px;">📊 État général du marché</h2>
      <p style="margin:0;font-size:14px;line-height:1.6;color:#333;">
        {{ETAT_GENERAL_DU_MARCHE}}
      </p>
    </div>

    <div style="padding:20px;">
  <h2 style="margin:0 0 12px;color:#0056b3;font-size:18px;">🏦 / 💻 Secteurs & entreprises marquants</h2>
  
    <!-- Bloc entreprise générique -->
    <div style="margin-bottom:14px;padding:14px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;">
      <strong style="color:#111;">{{ENTREPRISE_1_NOM}}</strong>
      <p style="margin:6px 0 0;font-size:14px;line-height:1.6;color:#444;">
        {{ENTREPRISE_1_TEXTE}}
      </p>
    </div>

    <div style="margin-bottom:14px;padding:14px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;">
      <strong style="color:#111;">{{ENTREPRISE_2_NOM}}</strong>
      <p style="margin:6px 0 0;font-size:14px;line-height:1.6;color:#444;">
        {{ENTREPRISE_2_TEXTE}}
      </p>
    </div>

    <div style="margin-bottom:14px;padding:14px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;">
      <strong style="color:#111;">{{ENTREPRISE_3_NOM}}</strong>
      <p style="margin:6px 0 0;font-size:14px;line-height:1.6;color:#444;">
        {{ENTREPRISE_3_TEXTE}}
      </p>
    </div>

    <div style="margin-bottom:14px;padding:14px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;">
      <strong style="color:#111;">{{ENTREPRISE_4_NOM}}</strong>
      <p style="margin:6px 0 0;font-size:14px;line-height:1.6;color:#444;">
        {{ENTREPRISE_4_TEXTE}}
      </p>
    </div>
  </div>

    <!-- Prix & mouvements -->
    <div style="padding:20px;background:#fffef9;">
      <h2 style="margin:0 0 10px;color:#0056b3;font-size:18px;">💵 Prix & mouvements notables</h2>
      <p style="margin:0;font-size:14px;line-height:1.6;color:#333;">
        {{PRIX_MOUVEMENTS}}
      </p>
    </div>

    <!-- Ambiance -->
    <div style="padding:20px;">
      <h2 style="margin:0 0 10px;color:#0056b3;font-size:18px;">💡 Ambiance & facteurs clés</h2>
      <p style="margin:0;font-size:14px;line-height:1.6;color:#333;">
        {{AMBIANCE_FACTEURS}}
      </p>
    </div>

    <!-- Conclusion -->
    <div style="padding:20px;background:#f7fffa;border-top:2px solid #e0f2e9;">
      <h2 style="margin:0 0 10px;color:#0056b3;font-size:18px;">✅ Conclusion synthétique</h2>
      <p style="margin:0;font-size:14px;line-height:1.6;color:#333;">
        {{CONCLUSION}}
      </p>
    </div>

    <!-- Footer -->
    <div style="padding:16px;text-align:center;font-size:12px;color:#777;background:#f9f9f9;border-top:1px solid #e6e9ef;">
      <p style="margin:4px 0;">📅 {{DATE}}</p>
      <p style="margin:6px 0 0;color:#aaa;">Note : Ce résumé est fourni à titre informatif et ne constitue pas un conseil en investissement.</p>
    </div>

  </div>
</body>
</html>


Voici les articles :

""" + article_for_prompt + "\n Attendu : un document HTML complet, prêt à envoyer.", 
  store=False,
)
print("✅ Email successfully generated")
html_content = response.output_text
html_content = html_content.split("```html")[1].strip().rstrip("```").strip()
print(html_content)
msg.attach(MIMEText(html_content, "html"))

print("⏳ Sending email...")
# Envoyer
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(username, password)
    server.sendmail(from_email, to_emails, msg.as_string())
print("✅ Email sent successfully")