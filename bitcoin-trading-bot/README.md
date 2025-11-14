# 🪙 Konservativer Bitcoin Trading Bot

**Speziell entwickelt für Holder mit geringem Risiko**

Ein emotionsloser, 24/7 Trading-Bot, der automatisch den optimalen Zeitpunkt findet, um wöchentlich 100 EUR aus Ihren Bitcoin-Holdings zu verkaufen.

---

## 🎯 Warum dieser Bot?

Als Holder mit über 10 Jahren Bitcoin-Erfahrung kennen Sie das Problem:

- ❌ **Manuelles Timing ist unmöglich** - Sie müssten 24/7 den Markt beobachten
- ❌ **Emotionen beeinflussen Entscheidungen** - Gier und Angst führen zu suboptimalen Verkäufen
- ❌ **Beste Verkaufszeitpunkte werden verpasst** - Der Kurs ist günstig, aber Sie schlafen gerade

**Dieser Bot löst alle diese Probleme:**

- ✅ **24/7 Überwachung** ohne müde zu werden
- ✅ **Emotionslose Entscheidungen** basierend auf technischer Analyse
- ✅ **Konservative Strategie** speziell für Holder (kein aggressives Trading!)
- ✅ **Automatische Ausführung** zum optimalen Zeitpunkt

---

## 📊 Strategie im Detail

### Wochenziel: 100 EUR

Der Bot verkauft **100 EUR pro Woche** aus Ihren Bitcoin-Holdings, aufgeteilt in **7 Tranchen** (ca. 14,29 EUR pro Tag).

**Warum aufteilen?**
- Minimiert Timing-Risiko (Reverse Dollar-Cost-Averaging)
- Glättet Preisschwankungen über die Woche
- Kein "alles auf eine Karte" setzen

### Konservative Verkaufskriterien

Der Bot verkauft **NUR** wenn **ALLE** folgenden Kriterien erfüllt sind:

1. **Mindestgewinn: 1,5%**
   - Verkauft nur bei klarem Profit
   - Schützt vor Verlusten

2. **Preis über gleitendem Durchschnitt**
   - 7-Tage MA > 30-Tage MA
   - Zeigt Aufwärtstrend an

3. **RSI überkauft (>70)**
   - Relative Strength Index zeigt Überkauftheit
   - Guter Zeitpunkt zum Verkaufen

4. **Innerhalb Handelsfenster**
   - Standard: 08:00 - 22:00 Uhr
   - Vermeidet Verkäufe zu ungünstigen Nachtzeiten

5. **Stop-Loss bei -3%**
   - Verkauft automatisch bei 3% Verlust
   - Begrenzt Risiko nach unten

---

## 🚀 Schnellstart

### 1. Installation

```bash
# Dependencies installieren
pip install -r requirements.txt
```

### 2. Konfiguration anpassen

Öffnen Sie `config.py` und passen Sie folgende Werte an:

```python
# Ihr durchschnittlicher Bitcoin-Einkaufspreis
REFERENCE_PRICE = 45000  # Beispiel: 45.000 EUR/BTC

# Wöchentliches Verkaufsziel
WEEKLY_TARGET_EUR = 100.0  # Standard: 100 EUR

# Dry-Run Modus (Simulation ohne echte Trades)
DRY_RUN = True  # Auf False setzen für echte Trades!
```

### 3. Bot starten (Simulation)

```bash
python monitor.py 45000
```

Ersetzen Sie `45000` mit Ihrem durchschnittlichen Bitcoin-Einkaufspreis.

Der Bot läuft jetzt im **Dry-Run Modus** (nur Simulation, keine echten Trades).

---

## 📈 Beispiel-Ausgabe

```
============================================================
BITCOIN TRADING BOT GESTARTET
Modus: DRY RUN (Simulation)
Ziel: 100.0 EUR/Woche
Prüf-Intervall: 300s
============================================================

2025-01-15 10:23:15 - Preis: 48234.50 EUR/BTC | Entscheidung: HALTEN
2025-01-15 10:23:15 - Grund: RSI überverkauft: 28.3 (besser halten)

2025-01-15 14:45:32 - Preis: 49127.80 EUR/BTC | Entscheidung: VERKAUFEN
2025-01-15 14:45:32 - Grund: ✓ Innerhalb Handelsfenster | ✓ Gewinn: 2.35% | ✓ Preis über MA | ✓ RSI überkauft: 72.1

============================================================
DRY RUN - SIMULIERTER TRADE
Verkaufe: 0.00029123 BTC
Erhält: 14.29 EUR
Preis: 49127.80 EUR/BTC
Zeitpunkt: 2025-01-15 14:45:32
============================================================

Wochenfortschritt: 14.29/100.00 EUR (14.3%)
```

---

## ⚙️ Konfiguration

### Konservative Parameter (Standard)

Diese Werte sind für **Holder mit geringem Risiko** optimiert:

```python
# Mindestgewinn bevor Verkauf
MIN_PROFIT_THRESHOLD = 1.5  # 1.5%

# Stop-Loss
MAX_DRAWDOWN_THRESHOLD = 3.0  # 3%

# Gleitende Durchschnitte
MA_SHORT_PERIOD = 7   # 1 Woche
MA_LONG_PERIOD = 30   # 1 Monat

# RSI
RSI_OVERBOUGHT = 70  # Verkaufen wenn >70
RSI_OVERSOLD = 30    # NICHT verkaufen wenn <30
```

### Aggressivere Parameter (nicht empfohlen)

Wenn Sie mehr Risiko eingehen möchten:

```python
# Weniger konservativ
MIN_PROFIT_THRESHOLD = 0.5  # Nur 0.5% Mindestgewinn
MAX_DRAWDOWN_THRESHOLD = 5.0  # 5% Stop-Loss

# Oder: Mehr verkaufen pro Woche
WEEKLY_TARGET_EUR = 200.0  # 200 EUR statt 100 EUR
```

**⚠️ WARNUNG:** Dies erhöht das Risiko erheblich!

---

## 🔒 Sicherheit

### Dry-Run Modus (empfohlen für Tests)

Standardmäßig läuft der Bot im **Dry-Run Modus**:

```python
DRY_RUN = True
```

In diesem Modus:
- ✅ Alle Analysen werden durchgeführt
- ✅ Verkaufssignale werden erkannt
- ✅ Trades werden simuliert und geloggt
- ❌ **KEINE echten Trades** werden ausgeführt

**Testen Sie den Bot mindestens 1 Woche im Dry-Run Modus!**

### Live-Trading aktivieren

Wenn Sie mit echtem Geld handeln möchten:

1. **Exchange API konfigurieren**

```python
# In config.py
EXCHANGE_API_KEY = "ihr_api_key"
EXCHANGE_API_SECRET = "ihr_api_secret"
```

2. **Exchange-Integration hinzufügen**

Öffnen Sie `monitor.py` und implementieren Sie `execute_trade()` für Ihre Exchange (z.B. Binance, Kraken).

Beispiel mit CCXT:

```python
import ccxt

def execute_trade(self, price, eur_amount, btc_amount):
    exchange = ccxt.binance({
        'apiKey': config.EXCHANGE_API_KEY,
        'secret': config.EXCHANGE_API_SECRET,
    })

    order = exchange.create_market_sell_order('BTC/EUR', btc_amount)
    self.strategy.record_trade(eur_amount, btc_amount, price)
```

3. **Dry-Run deaktivieren**

```python
DRY_RUN = False  # ACHTUNG: Echtes Trading!
```

---

## 📊 Monitoring & Logs

### Log-Datei

Alle Aktivitäten werden in `trading_bot.log` gespeichert:

```bash
tail -f trading_bot.log  # Live-Logs anzeigen
```

### Statistiken

Der Bot zeigt stündlich Statistiken:

```
============================================================
STATISTIKEN
Checks: 144
API-Fehler: 0
Signale erkannt: 3
Trades ausgeführt: 3
Letzter Preis: 49234.50 EUR/BTC
Woche: 42.87/100.00 EUR (42.9%)
============================================================
```

---

## 🧪 Backtesting

Um die Strategie mit historischen Daten zu testen:

```bash
python backtest.py
```

Dies simuliert die Strategie über vergangene Wochen und zeigt:
- Durchschnittlicher Verkaufspreis
- Anzahl Trades
- Beste/schlechteste Verkaufszeitpunkte

---

## 🛠️ Erweiterte Funktionen

### Benachrichtigungen

Fügen Sie Telegram-Benachrichtigungen hinzu:

```python
# requirements.txt
python-telegram-bot>=20.0

# config.py
ENABLE_NOTIFICATIONS = True
TELEGRAM_BOT_TOKEN = "ihr_bot_token"
TELEGRAM_CHAT_ID = "ihre_chat_id"
```

### Mehrere Coins

Erweitern Sie den Bot für Ethereum, Litecoin, etc.:

```python
COINS = ['bitcoin', 'ethereum', 'litecoin']
WEEKLY_TARGET_PER_COIN = 100.0
```

---

## ❓ FAQ

### Warum 100 EUR pro Woche?

Dies ist ein konservativer Startwert. Sie können ihn in `config.py` anpassen:

```python
WEEKLY_TARGET_EUR = 200.0  # Oder jeder andere Betrag
```

### Was ist der Referenzpreis?

Ihr durchschnittlicher Bitcoin-Einkaufspreis in EUR/BTC. Wird für Gewinnberechnung verwendet.

**Beispiel:**
- Sie haben 1 BTC für 30.000 EUR gekauft
- Später 1 BTC für 50.000 EUR gekauft
- Referenzpreis = (30.000 + 50.000) / 2 = 40.000 EUR/BTC

### Wie stoppe ich den Bot?

Drücken Sie `Ctrl+C` im Terminal. Der Bot zeigt eine finale Zusammenfassung.

### Kann ich aggressiver verkaufen?

Ja, aber **nicht empfohlen**. Passen Sie `MIN_PROFIT_THRESHOLD` in `config.py` an.

### Muss ich den Computer immer laufen lassen?

Für 24/7 Betrieb: Ja, oder nutzen Sie einen VPS (Virtual Private Server) in der Cloud.

---

## 📞 Support

Bei Fragen oder Problemen:

1. Prüfen Sie `trading_bot.log` für Fehler
2. Starten Sie im Dry-Run Modus zum Testen
3. Passen Sie Parameter in `config.py` an

---

## ⚠️ Disclaimer

**WICHTIG:**

- Trading birgt Risiken
- Keine Gewinngarantie
- Nur mit Geld handeln, das Sie verlieren können
- Testen Sie ausgiebig im Dry-Run Modus
- Der Bot ist keine Finanzberatung

**Sie tragen die volle Verantwortung für alle Trades!**

---

## 🎓 Wie funktioniert's technisch?

### Technische Indikatoren

1. **Moving Averages (MA)**
   - Gleitende Durchschnitte glätten Preisschwankungen
   - Short MA (7 Tage) > Long MA (30 Tage) = Aufwärtstrend

2. **RSI (Relative Strength Index)**
   - Misst Überkauft/Überverkauft-Niveau
   - RSI > 70: Überkauft (gut zum Verkaufen)
   - RSI < 30: Überverkauft (besser halten)

3. **Profit Threshold**
   - Verkauft nur bei Mindestgewinn
   - Schützt vor unprofitablen Verkäufen

### Workflow

```
┌─────────────────────┐
│  Preis abrufen      │ (alle 5 Minuten)
│  (CoinGecko API)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Technische Analyse │
│  - MA berechnen     │
│  - RSI berechnen    │
│  - Gewinn prüfen    │
└──────────┬──────────┘
           │
           ▼
      ┌────────┐
      │VERKAUFEN?│
      └─┬────┬─┘
        │    │
     JA │    │ NEIN
        │    │
        ▼    ▼
    ┌─────┐ ┌──────┐
    │Trade│ │Warten│
    │ aus-│ │      │
    │führen│ │      │
    └─────┘ └──────┘
```

---

## 📝 Dateistruktur

```
bitcoin-trading-bot/
├── config.py          # Alle Einstellungen
├── strategy.py        # Konservative Trading-Strategie
├── monitor.py         # 24/7 Preis-Monitoring
├── backtest.py        # Backtesting (optional)
├── requirements.txt   # Python Dependencies
├── README.md          # Diese Datei
└── trading_bot.log    # Log-Datei (wird erstellt)
```

---

## 🚀 Los geht's!

1. **Installieren:** `pip install -r requirements.txt`
2. **Konfigurieren:** Passen Sie `config.py` an
3. **Testen:** `python monitor.py 45000` (Dry-Run)
4. **Beobachten:** Lassen Sie den Bot 1 Woche laufen
5. **Live gehen:** Deaktivieren Sie `DRY_RUN` wenn Sie zufrieden sind

**Viel Erfolg mit Ihrem emotionslosen Trading-Assistenten!** 🤖💰
