"""
PRODUKTIONS-KONFIGURATION für Bitcoin Trading Bot
Für echtes Trading mit Ihrem Haupt-Bitcoin

WICHTIG: Kopieren Sie diese Datei zu config_local.py und passen Sie sie an!
"""

# ============================================================
# EXCHANGE KONFIGURATION
# ============================================================

# Welchen Exchange nutzen Sie?
# Unterstützt: 'binance', 'kraken', 'coinbase', 'bitstamp', etc.
EXCHANGE_ID = "binance"

# API Credentials
# WICHTIG: NIEMALS im Git committen! Nutzen Sie config_local.py!
EXCHANGE_API_KEY = ""  # Ihre API Key hier eintragen
EXCHANGE_API_SECRET = ""  # Ihre API Secret hier eintragen

# Testnet nutzen? (EMPFOHLEN für erste Tests!)
USE_TESTNET = True  # Auf False für echtes Trading!

# Trading Pair
TRADING_PAIR = "BTC/EUR"  # Oder BTC/USD, BTC/USDT, etc.

# ============================================================
# REFERENCE PREIS (Ihr durchschnittlicher Einkaufspreis)
# ============================================================

# WICHTIG: Diesen Wert MÜSSEN Sie setzen!
# Dies ist Ihr durchschnittlicher Bitcoin-Einkaufspreis in EUR/BTC
REFERENCE_PRICE_EUR = 45000.0  # Beispiel: 45,000 EUR/BTC

# Falls Sie mehrere Käufe hatten, berechnen Sie den Durchschnitt:
# Beispiel:
#   Kauf 1: 1.0 BTC @ 30,000 EUR = 30,000 EUR
#   Kauf 2: 0.5 BTC @ 50,000 EUR = 25,000 EUR
#   Total: 1.5 BTC für 55,000 EUR
#   Durchschnitt: 55,000 / 1.5 = 36,666.67 EUR/BTC

# ============================================================
# TRADING PARAMETER (Konservativ für Holder)
# ============================================================

# Wöchentliches Verkaufsziel in EUR
WEEKLY_TARGET_EUR = 100.0

# Wie viele Verkäufe pro Woche? (7 = einer pro Tag)
SELL_TRANCHES_PER_WEEK = 7

# Automatisch berechnet
TRANCHE_SIZE_EUR = WEEKLY_TARGET_EUR / SELL_TRANCHES_PER_WEEK

# Mindestgewinn bevor Verkauf (in Prozent)
# 1.5% = Nur verkaufen wenn mindestens 1.5% Gewinn
MIN_PROFIT_THRESHOLD = 1.5

# Stop-Loss (in Prozent)
# 3% = Verkaufen wenn Kurs 3% unter Referenzpreis
MAX_DRAWDOWN_THRESHOLD = 3.0

# Gleitende Durchschnitte
MA_SHORT_PERIOD = 7   # 7 Tage
MA_LONG_PERIOD = 30   # 30 Tage

# RSI Parameter
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# ============================================================
# HANDELSFENSTER
# ============================================================

# In welchem Zeitfenster soll gehandelt werden?
TRADING_WINDOW_START_HOUR = 8   # 08:00 Uhr
TRADING_WINDOW_END_HOUR = 22    # 22:00 Uhr

# ============================================================
# PREIS-MONITORING
# ============================================================

# Wie oft Preis prüfen? (in Sekunden)
PRICE_CHECK_INTERVAL_SECONDS = 300  # 5 Minuten

# CoinGecko API (kostenlos, als Fallback)
PRICE_API = "https://api.coingecko.com/api/v3/simple/price"
USE_COINGECKO_FALLBACK = True  # CoinGecko als Backup nutzen?

# ============================================================
# SICHERHEIT
# ============================================================

# DRY RUN Mode (EMPFOHLEN für Tests!)
# True = Nur Simulation, kein echtes Trading
# False = ECHTES TRADING!
DRY_RUN = True  # Auf False NUR wenn Sie bereit sind!

# Maximaler täglicher Verlust (Notbremse)
MAX_DAILY_LOSS_EUR = 50.0

# Maximale Anzahl Trades pro Tag
MAX_TRADES_PER_DAY = 2

# ============================================================
# BENACHRICHTIGUNGEN
# ============================================================

ENABLE_NOTIFICATIONS = True

# Telegram
TELEGRAM_ENABLED = False  # Auf True wenn konfiguriert
TELEGRAM_BOT_TOKEN = ""  # Von @BotFather
TELEGRAM_CHAT_ID = ""    # Ihre Chat ID

# Email (SendGrid)
EMAIL_ENABLED = False  # Auf True wenn konfiguriert
SENDGRID_API_KEY = ""
SENDGRID_FROM_EMAIL = ""
SENDGRID_TO_EMAIL = ""

# ============================================================
# LOGGING
# ============================================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "trading_bot_production.log"

# Logs rotieren?
LOG_ROTATION = True
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5  # 5 Backup-Dateien

# ============================================================
# MULTI-EXCHANGE (Optional)
# ============================================================

# Mehrere Exchanges nutzen um besten Preis zu finden?
USE_MULTI_EXCHANGE = False

# Wenn True, hier konfigurieren:
MULTI_EXCHANGE_CONFIG = {
    # 'binance': {
    #     'api_key': '',
    #     'api_secret': '',
    #     'testnet': True,
    # },
    # 'kraken': {
    #     'api_key': '',
    #     'api_secret': '',
    #     'testnet': False,
    # },
}

# ============================================================
# ERWEITERTE FEATURES
# ============================================================

# Performance Tracking
TRACK_PERFORMANCE = True  # Performance-Metriken sammeln?

# Backtesting Daten speichern?
SAVE_BACKTEST_RESULTS = True

# ============================================================
# SICHERHEITS-CHECKS
# ============================================================

def validate_config():
    """Validiere Konfiguration vor Start"""
    errors = []

    # Check Reference Price
    if REFERENCE_PRICE_EUR <= 0:
        errors.append("REFERENCE_PRICE_EUR muss gesetzt werden!")

    # Check API Keys für Live Trading
    if not DRY_RUN:
        if not EXCHANGE_API_KEY or not EXCHANGE_API_SECRET:
            errors.append("API Keys fehlen für Live-Trading!")

    # Check Wochenziel
    if WEEKLY_TARGET_EUR <= 0:
        errors.append("WEEKLY_TARGET_EUR muss > 0 sein!")

    # Check Telegram wenn aktiviert
    if TELEGRAM_ENABLED:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            errors.append("Telegram Token/Chat ID fehlen!")

    # Check Email wenn aktiviert
    if EMAIL_ENABLED:
        if not SENDGRID_API_KEY:
            errors.append("SendGrid API Key fehlt!")

    if errors:
        print("=" * 60)
        print("KONFIGURATIONS-FEHLER!")
        print("=" * 60)
        for error in errors:
            print(f"❌ {error}")
        print("=" * 60)
        return False

    return True


# Validierung ausführen wenn importiert
if __name__ != "__main__":
    if not validate_config():
        import sys
        sys.exit(1)
