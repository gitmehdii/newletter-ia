import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

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

html_content= """```html
<html>
<head>
    <meta charset="UTF-8">
    <title>Veille Financier</title>
</head>
<body style="font-family: system-ui, Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">

    <h1 style="color: #0056b3;">📩 Rapport de Veille Financière</h1>

    <div style="background-color: #f0f0f0; padding: 15px; margin: 20px 0;">
        <h2 style="color: #333;">État général du marché 📊</h2>
        <p>Les marchés continuent de montrer des signes de volatilité alors que l'attention est portée sur la possible réduction des taux d'intérêt par la Réserve Fédérale. L'incertitude politique liée aux décisions de Trump a également affecté l'humeur des investisseurs.</p>
    </div>

    <div style="background-color: #f0f0f0; padding: 15px; margin: 20px 0;">
        <h2 style="color: #333;">Secteurs & entreprises marquants 🏦💻</h2>
        <p><strong>Apple (AAPL)</strong> : Prix actuel à 229.31$. Attente d'un événement de lancement pour le nouvel iPhone le 9 septembre.</p>
        <p><strong>Nvidia (NVDA)</strong> : Prix prévu à 46.2 milliards$ avec un EPS ajusté de 1.01$. Réponse prévue aux attentes futures des investisseurs.</p>
        <p><strong>Microsoft (MSFT)</strong> : Revenus solides avec un focus sur l'IA, mis à jour des produits Windows.</p>
    </div>

    <div style="background-color: #f0f0f0; padding: 15px; margin: 20px 0;">
        <h2 style="color: #333;">Prix & mouvements notables 💵</h2>
        <p>Apple : +0.45$ depuis la clôture précédente. Microsoft : -2.22$ avec un prix actuel de 502.04$. Nvidia : prévisions indiquent une hausse significative.</p>
    </div>

    <div style="background-color: #f0f0f0; padding: 15px; margin: 20px 0;">
        <h2 style="color: #333;">Ambiance & facteurs clés 💡</h2>
        <p>La tension politique aux États-Unis continue d'inquiéter les marchés, en particulier avec les actions de Trump visant la Réserve Fédérale. L'humeur générale est anxieuse et les investisseurs se préoccupent des implications des taux d'intérêt.</p>
    </div>

    <div style="background-color: #f0f0f0; padding: 15px; margin: 20px 0;">
        <h2 style="color: #333;">Conclusion synthétique ✅</h2>
        <p>Alors que l'incertitude persiste, il est conseillé de garder une approche prudente. Diversifier les investissements semble essentiel dans ce climat économique instable.</p>
    </div>

    <footer style="margin-top: 20px; font-size: 12px; color: #999;">
        <p>Date : 2025-08-27</p>
        <p>Source : Synthèse basée sur votre veille NewsAPI</p>
        <p>Nota bene : Cet email ne constitue pas un conseil d'investissement.</p>
    </footer>
</body>
</html>
```
"""

html_content = html_content.split("```html")[1].strip().rstrip("```").strip()
msg.attach(MIMEText(html_content, "html"))

# Envoyer
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(username, password)
    server.sendmail(from_email, to_emails, msg.as_string())

print("✅ Email envoyé avec succès")