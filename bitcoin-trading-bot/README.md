# 🤖 Bitcoin Trading Bot - Binance Testnet

Ein modularer, KI-gesteuerter Bitcoin-Trading-Bot für das **Binance Testnet** (Sandbox-Modus, kein Echtgeld).

## 🎯 Projektziel

Entwicklung eines lernfähigen Trading-Bots mit drei Modi (VERKAUFEN, KAUFEN, HOLD), der als Lernsystem für KI-gestützte Automatisierung dient und durch Backtesting optimiert werden kann.

## ⚠️ WICHTIG: Testnet-Modus

Dieser Bot läuft ausschließlich auf dem **Binance Testnet** (testnet.binance.vision). Es wird **kein echtes Geld** verwendet. Alle Trades sind simuliert mit Testnet-Guthaben.

## 🚀 Features (Phase 1 - CHECKPOINT 1 ✅)

### Implementiert:
- ✅ **Binance Testnet API-Connector** mit vollständiger Fehlerbehandlung
- ✅ **Verbindungstest** mit automatischer Validierung
- ✅ **Balance-Abfrage** für BTC und USDT
- ✅ **Preis-Abfrage** mit 24h-Statistiken
- ✅ **Rate-Limiting Management** zum Schutz vor API-Überlastung
- ✅ **Umfassendes Logging-System** mit Farbcodierung und Rotation
- ✅ **Konfigurierbare Parameter** via YAML (kein Code-Editing nötig)
- ✅ **Retry-Logik** bei API-Fehlern mit exponentiellem Backoff

### Geplant (Phase 2-3):
- 🔄 **VERKAUFEN-Modus** - Automatischer Verkauf bei Kurssteigerung
- 🔄 **KAUFEN-Modus** - DCA-Strategie bei Kursrückgang
- 🔄 **HOLD-Modus** - Monitoring ohne Trading
- 🔄 **State Management** - Persistente Speicherung des Bot-Status
- 🔄 **Order Execution** - Tatsächliche Trade-Platzierung
- 🔄 **Backtesting** - Historische Validierung der Strategien

## 📁 Projektstruktur

```
bitcoin-trading-bot/
├── main.py                 # Einstiegspunkt des Bots
├── requirements.txt        # Python-Dependencies
├── .env.example           # Template für API-Keys
├── .env                   # Deine API-Keys (nicht in Git!)
│
├── config/
│   ├── config.yaml        # Haupt-Konfiguration (alle Parameter)
│   └── bot_state.json     # Bot-Status (wird automatisch erstellt)
│
├── src/
│   ├── logger.py          # Logging-System
│   ├── bot_core.py        # API-Connector (CHECKPOINT 1 ✅)
│   └── (weitere Module folgen in Phase 2)
│
├── logs/
│   └── trading_bot.log    # Log-Dateien (automatisch erstellt)
│
└── tests/
    └── (Tests folgen später)
```

## 🛠️ Setup-Anleitung

### 1. Voraussetzungen

- Python 3.8 oder höher
- pip (Python Package Manager)
- Binance Testnet Account (kostenlos)

### 2. Python-Dependencies installieren

```bash
cd bitcoin-trading-bot
pip install -r requirements.txt
```

### 3. Binance Testnet API-Keys erstellen

1. Gehe zu [Binance Testnet](https://testnet.binance.vision/)
2. Klicke auf "Generate HMAC_SHA256 Key"
3. Speichere **API Key** und **Secret Key** sicher

### 4. Environment-Datei konfigurieren

```bash
# .env.example als .env kopieren
cp .env.example .env

# .env mit deinem Editor öffnen und API-Keys eintragen
nano .env
```

Trage deine Keys ein:
```env
BINANCE_TESTNET_API_KEY=dein_testnet_api_key_hier
BINANCE_TESTNET_API_SECRET=dein_testnet_secret_key_hier

TRADING_MODE=HOLD
DRY_RUN=true
```

### 5. Konfiguration anpassen (optional)

Bearbeite `config/config.yaml` um Parameter anzupassen:

```yaml
# Beispiel: Verkaufsschwelle ändern
sell_mode:
  threshold_percent: 5.0  # Verkaufe bei +5% Kurssteigerung
  max_sell_fraction: 0.10 # Max. 10% des BTC-Bestands pro Trade
```

### 6. Bot starten

```bash
python main.py
```

## 📊 CHECKPOINT 1 - Was wird getestet?

Beim ersten Start führt der Bot folgende Tests durch:

1. **Verbindungstest** - Stelle Verbindung zu Binance Testnet her
2. **API-Key Validierung** - Prüfe ob API-Keys korrekt sind
3. **Balance-Abfrage** - Hole BTC und USDT Kontostände
4. **Preis-Abfrage** - Hole aktuellen BTC/USDT Preis
5. **24h-Statistiken** - Hole High/Low/Volume der letzten 24h
6. **Account-Status** - Zeige vollständigen Account-Überblick

Wenn alle Tests ✅ sind, ist CHECKPOINT 1 erfolgreich abgeschlossen!

## 🎮 Verwendung

### Erste Schritte nach dem Setup

```bash
# Bot starten (führt CHECKPOINT 1 Tests durch)
python main.py
```

### Erwartete Ausgabe (CHECKPOINT 1)

```
======================================================================
🤖 Bitcoin Trading Bot - Binance Testnet
======================================================================
Phase 1: Verbindungstest und Grundfunktionen
Testnet-Modus: Kein echtes Geld wird verwendet
======================================================================

📂 Lade Umgebungsvariablen...
⚙️  Lade Konfiguration...
📝 Initialisiere Logging-System...

======================================================================
Bitcoin Trading Bot - Starting Up
======================================================================
Config | Trading Pair: BTCUSDT
Config | Min Trade Interval: 300s
Config | Sell Threshold: 5.0%
Config | Buy Threshold: 3.0%
Config | Max API Calls/Min: 50
======================================================================

🤖 Initialisiere Trading Bot...
BinanceTradingBot initialisiert für BTCUSDT

======================================================================
CHECKPOINT 1: Starte Verbindungstests
======================================================================

🔌 Test 1: Verbindung zu Binance Testnet...
✅ Verbindung erfolgreich!

💰 Test 2: Kontostand abfragen...
✅ Balance erfolgreich abgerufen:
BALANCE | BTC: 0.50000000 | USDT: 10000.00 | Total: 20000.00 USDT @ 40000.00

📈 Test 3: Aktuellen BTC-Preis abfragen...
✅ Aktueller BTC-Preis: 40000.00 USDT

📊 Test 4: 24h-Statistiken abrufen...
✅ 24h-Stats erfolgreich abgerufen:
   High: 41000.00 USDT
   Low: 39000.00 USDT
   Change: +2.50%

🔍 Test 5: Vollständiger Account-Status...
✅ Account-Status erfolgreich abgerufen:
   BTC Balance: 0.50000000 BTC
   USDT Balance: 10000.00 USDT
   Total Value: 30000.00 USDT

======================================================================
✅ CHECKPOINT 1 ABGESCHLOSSEN - Alle Tests erfolgreich!
======================================================================

🎉 Phase 1 erfolgreich abgeschlossen!
📋 Nächste Schritte:
   - Phase 2: Trading-Modi implementieren (VERKAUFEN, KAUFEN, HOLD)
   - Phase 3: State-Management und Persistenz
   - Phase 4: Backtesting und Optimierung
```

## 🔧 Konfiguration

Alle Parameter können in `config/config.yaml` angepasst werden:

### Trading-Parameter

```yaml
# VERKAUFEN-Modus
sell_mode:
  threshold_percent: 5.0      # Verkaufe bei +5% Kurs
  max_sell_fraction: 0.10     # Max 10% des BTC pro Trade
  num_splits: 3               # Aufteilen in 3 Teilverkäufe

# KAUFEN-Modus
buy_mode:
  threshold_percent: 3.0      # Kaufe bei -3% Kurs
  max_buy_fraction: 0.10      # Max 10% des USDT pro Trade
  num_splits: 3               # DCA über 3 Käufe
```

### Sicherheits-Parameter

```yaml
safety:
  max_order_size_usdt: 1000.0         # Max. Order-Größe
  min_order_size_usdt: 10.0           # Min. Order-Größe
  max_daily_volume_usdt: 5000.0       # Tägliches Limit
  emergency_stop_loss_percent: 20.0   # Notfall-Stop bei -20%
  max_api_calls_per_minute: 50        # Rate-Limiting
```

### Logging-Einstellungen

```yaml
logging:
  level: "INFO"                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
  console_output: true             # Konsolen-Ausgabe
  colored_output: true             # Farbcodierung
  max_file_size_mb: 10            # Log-Rotation
```

## 🐛 Troubleshooting

### Problem: "API-Keys nicht gefunden"

**Lösung:**
- Stelle sicher, dass `.env` Datei existiert (nicht `.env.example`)
- Prüfe ob API-Keys korrekt eingetragen sind
- Keine Anführungszeichen um die Keys

### Problem: "Verbindung fehlgeschlagen"

**Lösung:**
- Prüfe Internetverbindung
- Testnet-URL korrekt: `https://testnet.binance.vision/api`
- API-Keys vom richtigen Testnet (nicht Mainnet!)

### Problem: "Rate-Limit erreicht"

**Lösung:**
- Bot wartet automatisch
- In `config.yaml` `max_api_calls_per_minute` reduzieren
- Längeres `min_trade_interval` setzen

### Problem: "Balance-Abfrage liefert 0.0"

**Lösung:**
- Testnet-Account hat initial kein Guthaben
- Auf [Binance Testnet](https://testnet.binance.vision/) Testnet-Guthaben anfordern
- "Get Test Funds" Button klicken

## 📈 Entwicklungs-Roadmap

### ✅ Phase 1 (Abgeschlossen): Technische Basis
- [x] CHECKPOINT 1: Binance Testnet Verbindung
- [x] CHECKPOINT 2: Config-System & Logging
- [x] CHECKPOINT 3: Modi-Grundstruktur (Vorbereitung)

### 🔄 Phase 2 (In Arbeit): Trading-Logik
- [ ] CHECKPOINT 4: VERKAUFEN-Modus implementieren
- [ ] CHECKPOINT 5: KAUFEN-Modus implementieren
- [ ] CHECKPOINT 6: HOLD-Modus & Monitoring
- [ ] State-Management System
- [ ] Order-Execution mit Safety-Checks

### 📅 Phase 3 (Geplant): Testing & Validation
- [ ] CHECKPOINT 7: Sandbox-Tests mit Dummy-Parametern
- [ ] CHECKPOINT 8: Integration optimierter Parameter
- [ ] Backtesting-System
- [ ] Parameter-Optimierung
- [ ] Live-Monitoring Dashboard

## 🔒 Sicherheitshinweise

1. **Nur Testnet verwenden** - Dieser Bot ist für Lernzwecke
2. **API-Keys schützen** - Niemals in Git commiten
3. **Testnet-Keys verwenden** - Keine Mainnet-Keys!
4. **Rate-Limits beachten** - Bot respektiert automatisch Limits
5. **Logs regelmäßig prüfen** - `logs/trading_bot.log` überwachen

## 🤝 Entwicklung

### Neue Features hinzufügen

1. Module in `src/` erweitern
2. Parameter in `config/config.yaml` hinzufügen
3. Tests schreiben in `tests/`
4. Logging für alle kritischen Operationen

### Code-Qualität

- ✅ Defensive Programmierung (alle Fehler abfangen)
- ✅ Ausführliche Kommentare auf Deutsch
- ✅ Modular & erweiterbar
- ✅ Kein Hardcoding
- ✅ Logging bei jeder kritischen Aktion

## 📝 Lizenz

Dieses Projekt ist für Lern- und Testzwecke. Keine Finanzberatung!

## 🆘 Support

Bei Fragen oder Problemen:
1. Prüfe die Logs: `logs/trading_bot.log`
2. Erhöhe Log-Level auf DEBUG in `config/config.yaml`
3. Prüfe Binance Testnet Status

## 🎓 Lernressourcen

- [Binance Testnet Dokumentation](https://testnet.binance.vision/)
- [python-binance Dokumentation](https://python-binance.readthedocs.io/)
- [Binance API Docs](https://binance-docs.github.io/apidocs/spot/en/)

---

**Version:** 1.0 (Phase 1 - CHECKPOINT 1 ✅)
**Status:** Development - Testnet Only
**Letztes Update:** November 2025
