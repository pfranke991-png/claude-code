# 🚀 DEPLOYMENT GUIDE - Bitcoin Trading Bot

**Vollständige Anleitung für Production-Deployment mit Ihrem Haupt-Bitcoin**

---

## 📋 Voraussetzungen

### 1. System Requirements

- **Python 3.8+**
- **Linux/Mac** empfohlen (Ubuntu, Debian, etc.)
- **VPS/Server** für 24/7 Betrieb (DigitalOcean, AWS, etc.)
- **Min. 1 GB RAM**, 10 GB Disk Space
- **Stabile Internetverbindung**

### 2. Exchange Account

Wählen Sie einen der unterstützten Exchanges:

| Exchange | Empfehlung | Testnet | EUR Trading |
|----------|-----------|---------|-------------|
| **Binance** | ⭐⭐⭐⭐⭐ | ✅ Ja | ✅ Ja |
| **Kraken** | ⭐⭐⭐⭐ | ❌ Nein | ✅ Ja |
| **Coinbase Pro** | ⭐⭐⭐ | ❌ Nein | ✅ Ja |
| **Bitstamp** | ⭐⭐⭐ | ❌ Nein | ✅ Ja |

**Empfehlung:** Binance wegen Testnet und niedrigen Gebühren

---

## 🛠️ SCHRITT 1: Server Setup

### Option A: Lokaler Computer (für Tests)

```bash
# Installation
git clone <your-repo>
cd bitcoin-trading-bot

# Python Dependencies
pip install -r requirements.txt
```

### Option B: VPS/Cloud Server (für 24/7 Betrieb)

```bash
# 1. Server mieten (z.B. DigitalOcean, Hetzner, AWS)
# Kosten: ~5-10 EUR/Monat für Basis-VPS

# 2. SSH Verbindung
ssh root@your-server-ip

# 3. Python installieren
apt update
apt install -y python3 python3-pip git

# 4. Bot Code holen
git clone <your-repo>
cd bitcoin-trading-bot

# 5. Dependencies installieren
pip3 install -r requirements.txt
```

---

## 🔐 SCHRITT 2: Exchange API Setup

### Binance (EMPFOHLEN)

#### 2.1 Testnet Setup (für sichere Tests!)

```
1. Gehe zu: https://testnet.binance.vision/
2. Klicke "Generate HMAC_SHA256 Key"
3. Speichere API Key und Secret

Testnet Features:
✅ Echte Trading-Simulation
✅ Kostenlos
✅ Kein Risiko
✅ Perfekt zum Testen
```

#### 2.2 Live API Setup (NUR für echtes Trading!)

```
1. Login auf binance.com
2. Gehe zu: Account → API Management
3. Erstelle neuen API Key:
   - Name: "Bitcoin Trading Bot"
   - Permissions: ✅ Enable Spot Trading
   - IP Whitelist: Trage VPS IP ein (WICHTIG!)

4. Speichere Key und Secret SICHER!

SICHERHEIT:
⚠️ IP Whitelist IMMER aktivieren!
⚠️ Nur "Enable Spot Trading" Permission
⚠️ KEINE Withdrawal-Rechte!
```

### Kraken

```
1. Login auf kraken.com
2. Settings → API → Generate New Key
3. Permissions:
   ✅ Query Funds
   ✅ Query Open Orders & Trades
   ✅ Create & Modify Orders
   ❌ Withdraw Funds (DEAKTIVIEREN!)

4. Speichere Key und Secret
```

---

## ⚙️ SCHRITT 3: Bot Konfiguration

### 3.1 Basis-Konfiguration

```bash
# Kopiere Template
cp config_production.py config_local.py

# Editiere config_local.py
nano config_local.py
```

### 3.2 Wichtigste Einstellungen

```python
# config_local.py

# 1. EXCHANGE
EXCHANGE_ID = "binance"
EXCHANGE_API_KEY = "IHR_API_KEY"
EXCHANGE_API_SECRET = "IHR_API_SECRET"
USE_TESTNET = True  # Für Tests!

# 2. REFERENZPREIS (WICHTIG!)
REFERENCE_PRICE_EUR = 45000.0  # Ihr Durchschnittspreis!

# 3. VERKAUFSZIEL
WEEKLY_TARGET_EUR = 100.0  # 100 EUR pro Woche

# 4. SICHERHEIT
DRY_RUN = True  # Erst mal Simulation!

# 5. TRADING PAIR
TRADING_PAIR = "BTC/EUR"  # Oder BTC/USDT
```

### 3.3 Referenzpreis berechnen

```python
# Wenn Sie mehrere BTC-Käufe hatten:

kauf_1 = {'btc': 0.5, 'eur': 20000}  # 0.5 BTC für 20k EUR
kauf_2 = {'btc': 0.3, 'eur': 15000}  # 0.3 BTC für 15k EUR
kauf_3 = {'btc': 0.2, 'eur': 12000}  # 0.2 BTC für 12k EUR

total_btc = 0.5 + 0.3 + 0.2  # = 1.0 BTC
total_eur = 20000 + 15000 + 12000  # = 47,000 EUR

REFERENCE_PRICE_EUR = total_eur / total_btc  # = 47,000 EUR/BTC
```

---

## 🧪 SCHRITT 4: Testphase (SEHR WICHTIG!)

### Phase 1: Dry-Run (1 Woche)

```bash
# Starte Bot in Simulation Mode
python3 monitor_advanced.py 45000

# Was passiert:
✅ Preis-Überwachung läuft
✅ Verkaufssignale werden erkannt
✅ Trades werden simuliert
❌ KEIN echtes Trading!

# Logs beobachten
tail -f trading_bot_production.log

# Nach 1 Woche:
- Prüfen Sie die Logs
- Sehen Sie sich simulierte Trades an
- Passen Sie Parameter an wenn nötig
```

### Phase 2: Testnet Trading (wenn verfügbar)

```bash
# config_local.py
DRY_RUN = False
USE_TESTNET = True

# Starte Bot
python3 monitor_advanced.py 45000

# Was passiert:
✅ Echte Orders auf Testnet
✅ Echte API Calls
✅ Kein echtes Geld
✅ Perfekt zum Testen!

# Laufen lassen für 1 Woche
```

### Phase 3: Mini-Live-Test (kleine Beträge)

```bash
# config_local.py
WEEKLY_TARGET_EUR = 10.0  # NUR 10 EUR!
DRY_RUN = False
USE_TESTNET = False

# Starte Bot
python3 monitor_advanced.py 45000

# Was passiert:
⚠️ ECHTES TRADING!
💰 Aber nur kleine Beträge (10 EUR/Woche)

# Laufen lassen für 1-2 Wochen
# Wenn alles OK → Auf 100 EUR erhöhen
```

---

## 🚀 SCHRITT 5: Production Deployment

### 5.1 Finale Konfiguration

```python
# config_local.py - PRODUCTION

EXCHANGE_ID = "binance"
EXCHANGE_API_KEY = "IHR_LIVE_API_KEY"
EXCHANGE_API_SECRET = "IHR_LIVE_API_SECRET"
USE_TESTNET = False  # LIVE!

REFERENCE_PRICE_EUR = 45000.0  # Ihr echter Preis
WEEKLY_TARGET_EUR = 100.0  # Ihr Ziel

DRY_RUN = False  # ECHTES TRADING!

# Trading Parameter (konservativ für Holder)
MIN_PROFIT_THRESHOLD = 1.5  # 1.5% Mindestgewinn
MAX_DRAWDOWN_THRESHOLD = 3.0  # 3% Stop-Loss
```

### 5.2 Als Hintergrund-Dienst starten

#### Option A: Screen (einfach)

```bash
# Screen Session starten
screen -S bitcoin-bot

# Bot starten
python3 monitor_advanced.py 45000

# Detach: Ctrl+A, dann D
# Wieder anhängen: screen -r bitcoin-bot
```

#### Option B: Systemd (professionell)

```bash
# Erstelle Service File
sudo nano /etc/systemd/system/bitcoin-bot.service
```

```ini
[Unit]
Description=Bitcoin Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/bitcoin-trading-bot
ExecStart=/usr/bin/python3 monitor_advanced.py 45000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Service aktivieren
sudo systemctl enable bitcoin-bot
sudo systemctl start bitcoin-bot

# Status prüfen
sudo systemctl status bitcoin-bot

# Logs anschauen
sudo journalctl -u bitcoin-bot -f
```

#### Option C: Docker (isoliert)

```bash
# Erstelle Dockerfile
cat > Dockerfile <<'EOF'
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

CMD ["python3", "monitor_advanced.py", "45000"]
EOF

# Build Image
docker build -t bitcoin-bot .

# Run Container
docker run -d \
  --name bitcoin-bot \
  --restart unless-stopped \
  -v $(pwd)/config_local.py:/app/config_local.py \
  -v $(pwd)/logs:/app/logs \
  bitcoin-bot

# Logs anschauen
docker logs -f bitcoin-bot
```

---

## 📱 SCHRITT 6: Telegram Benachrichtigungen (Optional)

### 6.1 Bot erstellen

```
1. Telegram öffnen
2. Suche nach @BotFather
3. Sende: /newbot
4. Bot Name: "Bitcoin Trading Bot"
5. Username: "your_bitcoin_bot"
6. Speichere Bot Token
```

### 6.2 Chat ID erhalten

```
1. Starte Chat mit Ihrem Bot
2. Sende: /start
3. Öffne Browser:
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
4. Finde "chat":{"id":123456789}
5. Speichere Chat ID
```

### 6.3 Konfigurieren

```python
# config_local.py
TELEGRAM_ENABLED = True
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHAT_ID = "123456789"
```

### 6.4 Testen

```python
# Test Benachrichtigung
python3 -c "
from notifications import TelegramNotifier
from datetime import datetime

notifier = TelegramNotifier('YOUR_TOKEN', 'YOUR_CHAT_ID')
notifier.send_message('🤖 Bitcoin Bot läuft!')
"
```

---

## 📊 SCHRITT 7: Monitoring & Wartung

### Täglich prüfen

```bash
# Logs checken
tail -n 100 trading_bot_production.log

# Statistiken anschauen
grep "STATISTIKEN" trading_bot_production.log | tail -n 20

# Trades anschauen
grep "VERKAUF" trading_bot_production.log
```

### Wöchentlich prüfen

```bash
# Wochenzusammenfassung
grep "Wochenzusammenfassung" trading_bot_production.log | tail -n 5

# Performance analysieren
# → Wurden Trades zu guten Preisen ausgeführt?
# → Wurde Wochenziel erreicht?
# → Gab es Fehler?
```

### Monatlich prüfen

```bash
# Gesamtperformance
# → Durchschnittlicher Verkaufspreis
# → Total verkaufte EUR
# → Gewinn vs. Referenzpreis
```

---

## 🔒 SICHERHEITS-CHECKLISTE

Vor Production Deployment ALLE Punkte prüfen:

### API Security

- [ ] IP Whitelist auf Exchange aktiviert
- [ ] Nur "Spot Trading" Permission
- [ ] KEINE Withdrawal-Rechte
- [ ] 2FA auf Exchange aktiviert
- [ ] API Keys in config_local.py (NICHT in Git!)

### Server Security

- [ ] Server hat Firewall
- [ ] SSH nur mit Key, nicht Passwort
- [ ] Regelmäßige Updates (apt update && apt upgrade)
- [ ] Fail2ban installiert
- [ ] Logs regelmäßig checken

### Bot Security

- [ ] DRY_RUN erst nach Tests auf False
- [ ] Kleine Beträge zum Testen
- [ ] MAX_DAILY_LOSS gesetzt
- [ ] MIN_PROFIT_THRESHOLD nicht zu niedrig
- [ ] Benachrichtigungen aktiviert

### Backup

- [ ] config_local.py Backup
- [ ] Logs regelmäßig sichern
- [ ] Server Snapshots erstellen

---

## ⚠️ TROUBLESHOOTING

### Problem: "API Error" in Logs

```bash
# Lösung:
1. Prüfe API Keys in config_local.py
2. Prüfe IP Whitelist auf Exchange
3. Prüfe ob Exchange erreichbar: ping api.binance.com
```

### Problem: "Minimum Order Size" Fehler

```bash
# Lösung:
# Erhöhe WEEKLY_TARGET_EUR in config_local.py
WEEKLY_TARGET_EUR = 200.0  # Statt 100.0
```

### Problem: "Zu wenige Trades"

```bash
# Lösung:
# Lockere Parameter:
MIN_PROFIT_THRESHOLD = 1.0  # Statt 1.5
RSI_OVERBOUGHT = 65  # Statt 70
```

### Problem: Bot stoppt unerwartet

```bash
# Logs checken
tail -n 200 trading_bot_production.log

# Neustart mit systemd
sudo systemctl restart bitcoin-bot

# Oder mit Screen
screen -r bitcoin-bot
# Strg+C, dann neu starten
python3 monitor_advanced.py 45000
```

---

## 📈 PERFORMANCE OPTIMIERUNG

### Wenn zu wenig verkauft wird:

```python
# Aggressivere Parameter
MIN_PROFIT_THRESHOLD = 1.0  # Niedriger
WEEKLY_TARGET_EUR = 150.0   # Höher
```

### Wenn zu oft verkauft wird:

```python
# Konservativere Parameter
MIN_PROFIT_THRESHOLD = 2.0  # Höher
RSI_OVERBOUGHT = 75  # Höher
```

### Multi-Exchange für beste Preise:

```python
# In monitor_advanced.py
from exchange import create_binance_connector, create_kraken_connector

exchanges = {
    'binance': create_binance_connector(KEY1, SECRET1),
    'kraken': create_kraken_connector(KEY2, SECRET2),
}

monitor.setup_multi_exchange(exchanges)
# → Verkauft automatisch auf Exchange mit bestem Preis!
```

---

## 🎯 FINALE CHECKLISTE

Vor dem Start mit echtem Geld:

- [ ] 1 Woche Dry-Run erfolgreich
- [ ] 1 Woche Testnet erfolgreich (falls verfügbar)
- [ ] Mini-Live-Test mit 10 EUR erfolgreich
- [ ] Telegram Benachrichtigungen funktionieren
- [ ] Alle Logs sehen gut aus
- [ ] API Keys sicher gespeichert
- [ ] Server läuft stabil 24/7
- [ ] Backup erstellt
- [ ] Referenzpreis korrekt berechnet
- [ ] Parameter für Ihre Risikotoleranz angepasst

**NUR wenn ALLE Punkte ✅ → Production starten!**

---

## 🆘 SUPPORT

Bei Problemen:

1. Logs checken: `trading_bot_production.log`
2. README.md lesen
3. Code in `monitor_advanced.py` anschauen
4. GitHub Issues erstellen

---

## 📚 WEITERFÜHRENDE INFOS

### Empfohlene VPS Provider

- **Hetzner Cloud**: 4.15 EUR/Monat (Deutschland)
- **DigitalOcean**: $5/Monat (weltweit)
- **Contabo**: 4.99 EUR/Monat (Deutschland)

### CCXT Documentation

https://docs.ccxt.com/

### Binance API Docs

https://binance-docs.github.io/apidocs/spot/en/

### Kraken API Docs

https://docs.kraken.com/rest/

---

**🚀 VIEL ERFOLG MIT IHREM BITCOIN TRADING BOT! 🚀**

*Denken Sie daran: Trading birgt Risiken. Starten Sie konservativ und erhöhen Sie schrittweise!*
