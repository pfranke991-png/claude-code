"""
Konservative Bitcoin Trading Bot Konfiguration
Speziell entwickelt für Holder mit geringem Risiko
"""

# ============================================================
# WÖCHENTLICHES ZIEL
# ============================================================
WEEKLY_TARGET_EUR = 100.0  # 100 EUR pro Woche aus Bitcoin verkaufen

# ============================================================
# KONSERVATIVE PARAMETER (für Holder)
# ============================================================
# Diese Werte sind bewusst konservativ gewählt:

# Mindestgewinn bevor Verkauf (in Prozent)
# 1.5% = Nur verkaufen wenn mindestens 1.5% Gewinn möglich ist
MIN_PROFIT_THRESHOLD = 1.5

# Maximaler Drawdown bevor Stop-Loss (in Prozent)
# 3% = Verkaufen wenn Kurs 3% unter Einstiegspreis fällt (Risikobegrenzung)
MAX_DRAWDOWN_THRESHOLD = 3.0

# Anzahl der Tage für gleitenden Durchschnitt
# Längere Periode = konservativer, weniger volatil
MA_SHORT_PERIOD = 7   # 1 Woche
MA_LONG_PERIOD = 30   # 1 Monat

# RSI Parameter (Relative Strength Index)
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70  # Über 70 = überkauft (guter Zeitpunkt zum Verkaufen)
RSI_OVERSOLD = 30    # Unter 30 = überverkauft (NICHT verkaufen)

# ============================================================
# VERKAUFSSTRATEGIE
# ============================================================
# Wie wird die wöchentliche Verkaufsmenge aufgeteilt?

# Anzahl der Verkaufs-Tranchen pro Woche
# 7 = Eine pro Tag, minimiert Timing-Risiko (Dollar-Cost-Averaging umgekehrt)
SELL_TRANCHES_PER_WEEK = 7

# Berechnete Tranchengröße
TRANCHE_SIZE_EUR = WEEKLY_TARGET_EUR / SELL_TRANCHES_PER_WEEK  # ~14.29 EUR pro Tag

# Zeitfenster für Verkauf (in Stunden pro Tag)
# Bot sucht innerhalb dieser Zeit den besten Zeitpunkt
TRADING_WINDOW_START_HOUR = 8   # 08:00 Uhr
TRADING_WINDOW_END_HOUR = 22    # 22:00 Uhr

# ============================================================
# MARKT-MONITORING
# ============================================================
# Wie oft wird der Preis geprüft?
PRICE_CHECK_INTERVAL_SECONDS = 300  # Alle 5 Minuten (konservativ, spart API-Calls)

# API für Bitcoin-Preise (kostenlos)
PRICE_API = "https://api.coingecko.com/api/v3/simple/price"

# ============================================================
# SIGNAL-KRITERIEN (alle müssen erfüllt sein für Verkauf)
# ============================================================
SIGNAL_CRITERIA = {
    # 1. Preis über gleitendem Durchschnitt
    'price_above_ma': True,

    # 2. RSI zeigt überkauft (guter Verkaufszeitpunkt)
    'rsi_favorable': True,

    # 3. Mindestgewinn erreicht
    'min_profit_reached': True,

    # 4. Innerhalb Handelsfenster
    'within_trading_window': True,
}

# ============================================================
# SICHERHEITS-EINSTELLUNGEN
# ============================================================
# Dry-Run Modus (nur Simulation, kein echter Verkauf)
DRY_RUN = True  # WICHTIG: Auf False setzen für echte Trades!

# Maximaler täglicher Verlust (EUR)
MAX_DAILY_LOSS = 20.0

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "trading_bot.log"

# ============================================================
# EXCHANGE/WALLET KONFIGURATION
# ============================================================
# HINWEIS: Diese müssen vom Benutzer ausgefüllt werden!
EXCHANGE_API_KEY = ""  # Ihre Exchange API Key
EXCHANGE_API_SECRET = ""  # Ihre Exchange API Secret
WALLET_ADDRESS = ""  # Ihre Bitcoin Wallet Adresse

# ============================================================
# BENACHRICHTIGUNGEN
# ============================================================
ENABLE_NOTIFICATIONS = True
NOTIFICATION_EMAIL = ""  # Optional: Email für Benachrichtigungen
