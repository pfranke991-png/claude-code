"""
Konservative Bitcoin Trading Strategie
Ziel: 100 EUR/Woche aus Bitcoin verkaufen zum optimalen Zeitpunkt

PRODUCTION-READY Version - Keine externen Dependencies benötigt!
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

import config

logger = logging.getLogger(__name__)


def mean(values: List[float]) -> float:
    """Berechne Durchschnitt einer Liste"""
    return sum(values) / len(values) if values else 0.0


def diff(values: List[float]) -> List[float]:
    """Berechne Differenzen zwischen aufeinanderfolgenden Werten"""
    return [values[i] - values[i-1] for i in range(1, len(values))]


class ConservativeStrategy:
    """
    Konservative Trading-Strategie für Holder

    Kernprinzipien:
    1. Risikominimierung durch Diversifikation über die Woche
    2. Nur verkaufen bei klaren Profit-Signalen
    3. Emotionslose, datenbasierte Entscheidungen
    4. Dollar-Cost-Averaging in Reverse (DCA-out)
    """

    def __init__(self):
        self.weekly_target = config.WEEKLY_TARGET_EUR
        self.tranches = config.SELL_TRANCHES_PER_WEEK
        self.tranche_size = config.TRANCHE_SIZE_EUR
        self.min_profit = config.MIN_PROFIT_THRESHOLD / 100.0  # Convert to decimal

        # Tracking
        self.sold_this_week = 0.0
        self.trades_this_week = []
        self.week_start = self._get_week_start()

        logger.info(f"Strategie initialisiert: {self.weekly_target} EUR/Woche in {self.tranches} Tranchen")

    def _get_week_start(self) -> datetime:
        """Berechne Start der aktuellen Woche (Montag 00:00)"""
        now = datetime.now()
        monday = now - timedelta(days=now.weekday())
        return monday.replace(hour=0, minute=0, second=0, microsecond=0)

    def _is_new_week(self) -> bool:
        """Prüfe ob eine neue Woche begonnen hat"""
        return datetime.now() >= self.week_start + timedelta(weeks=1)

    def reset_weekly_tracking(self):
        """Reset Tracking für neue Woche"""
        if self._is_new_week():
            logger.info(f"Neue Woche! Bisheriger Verkauf: {self.sold_this_week:.2f} EUR")
            self.sold_this_week = 0.0
            self.trades_this_week = []
            self.week_start = self._get_week_start()

    def calculate_moving_averages(self, prices: List[float]) -> Tuple[float, float]:
        """
        Berechne gleitende Durchschnitte

        Args:
            prices: Liste von Preisen (neueste zuletzt)

        Returns:
            (ma_short, ma_long): Kurzfristiger und langfristiger MA
        """
        if len(prices) < config.MA_LONG_PERIOD:
            logger.warning(f"Nicht genug Daten für MA: {len(prices)} < {config.MA_LONG_PERIOD}")
            return None, None

        ma_short = mean(prices[-config.MA_SHORT_PERIOD:])
        ma_long = mean(prices[-config.MA_LONG_PERIOD:])

        return ma_short, ma_long

    def calculate_rsi(self, prices: List[float], period: int = None) -> float:
        """
        Berechne Relative Strength Index (RSI)

        RSI > 70: Überkauft (guter Zeitpunkt zum Verkaufen)
        RSI < 30: Überverkauft (NICHT verkaufen, besser halten)

        Args:
            prices: Liste von Preisen
            period: RSI Periode (Standard: aus config)

        Returns:
            RSI Wert (0-100)
        """
        if period is None:
            period = config.RSI_PERIOD

        if len(prices) < period + 1:
            logger.warning(f"Nicht genug Daten für RSI: {len(prices)} < {period + 1}")
            return 50.0  # Neutral

        # Berechne Preisänderungen
        deltas = diff(prices)

        # Separate Gewinne und Verluste
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [abs(d) if d < 0 else 0 for d in deltas]

        # Durchschnittliche Gewinne/Verluste (letzte period Werte)
        avg_gain = mean(gains[-period:])
        avg_loss = mean(losses[-period:])

        if avg_loss == 0:
            return 100.0  # Maximaler RSI

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def is_within_trading_window(self) -> bool:
        """Prüfe ob aktuell innerhalb des Handelsfensters"""
        now = datetime.now()
        current_hour = now.hour

        return config.TRADING_WINDOW_START_HOUR <= current_hour < config.TRADING_WINDOW_END_HOUR

    def should_sell(self, current_price: float, price_history: List[float],
                    reference_price: float) -> Tuple[bool, str, Dict]:
        """
        Hauptentscheidungslogik: Soll jetzt verkauft werden?

        Args:
            current_price: Aktueller Bitcoin-Preis in EUR
            price_history: Historische Preise für Indikatoren
            reference_price: Referenzpreis (z.B. durchschnittlicher Einkaufspreis)

        Returns:
            (should_sell, reason, signals): Bool, Begründung, Signal-Details
        """
        self.reset_weekly_tracking()

        signals = {
            'price_above_ma': False,
            'rsi_favorable': False,
            'min_profit_reached': False,
            'within_trading_window': False,
            'weekly_target_not_exceeded': False,
        }

        reasons = []

        # 1. Prüfe ob Wochenziel bereits erreicht
        if self.sold_this_week >= self.weekly_target:
            return False, "Wochenziel bereits erreicht", signals

        signals['weekly_target_not_exceeded'] = True

        # 2. Prüfe Handelsfenster
        if not self.is_within_trading_window():
            return False, "Außerhalb des Handelsfensters", signals

        signals['within_trading_window'] = True
        reasons.append("✓ Innerhalb Handelsfenster")

        # 3. Prüfe Mindestgewinn
        profit_percent = ((current_price - reference_price) / reference_price) * 100

        if profit_percent < config.MIN_PROFIT_THRESHOLD:
            return False, f"Gewinn zu gering: {profit_percent:.2f}% < {config.MIN_PROFIT_THRESHOLD}%", signals

        signals['min_profit_reached'] = True
        reasons.append(f"✓ Gewinn: {profit_percent:.2f}%")

        # 4. Prüfe gleitende Durchschnitte
        ma_short, ma_long = self.calculate_moving_averages(price_history)

        if ma_short is not None and ma_long is not None:
            if current_price > ma_short > ma_long:
                signals['price_above_ma'] = True
                reasons.append(f"✓ Preis über MA (Short: {ma_short:.2f}, Long: {ma_long:.2f})")
            else:
                return False, "Preis nicht über gleitendem Durchschnitt", signals
        else:
            logger.warning("Nicht genug Daten für MA-Analyse")

        # 5. Prüfe RSI
        rsi = self.calculate_rsi(price_history)

        if rsi >= config.RSI_OVERBOUGHT:
            # Überkauft = guter Verkaufszeitpunkt
            signals['rsi_favorable'] = True
            reasons.append(f"✓ RSI überkauft: {rsi:.1f}")
        elif rsi <= config.RSI_OVERSOLD:
            # Überverkauft = NICHT verkaufen
            return False, f"RSI überverkauft: {rsi:.1f} (besser halten)", signals
        else:
            # Neutral - wir verkaufen trotzdem wenn andere Signale gut sind
            signals['rsi_favorable'] = True
            reasons.append(f"○ RSI neutral: {rsi:.1f}")

        # ALLE KONSERVATIVEN KRITERIEN ERFÜLLT!
        reason = " | ".join(reasons)
        logger.info(f"VERKAUFSSIGNAL: {reason}")

        return True, reason, signals

    def calculate_sell_amount(self, current_price: float) -> Tuple[float, float]:
        """
        Berechne wie viel verkauft werden soll

        Args:
            current_price: Aktueller BTC-Preis in EUR

        Returns:
            (eur_amount, btc_amount): Zu verkaufende Menge in EUR und BTC
        """
        # Verbleibende Menge für diese Woche
        remaining = self.weekly_target - self.sold_this_week

        # Nimm Tranchengröße oder Rest (was kleiner ist)
        eur_amount = min(self.tranche_size, remaining)

        # Konvertiere zu BTC
        btc_amount = eur_amount / current_price

        logger.info(f"Verkaufsmenge: {eur_amount:.2f} EUR = {btc_amount:.8f} BTC")

        return eur_amount, btc_amount

    def record_trade(self, eur_amount: float, btc_amount: float, price: float):
        """Zeichne Trade auf"""
        trade = {
            'timestamp': datetime.now(),
            'eur_amount': eur_amount,
            'btc_amount': btc_amount,
            'price': price,
        }

        self.trades_this_week.append(trade)
        self.sold_this_week += eur_amount

        logger.info(f"Trade aufgezeichnet: {eur_amount:.2f} EUR @ {price:.2f} EUR/BTC")
        logger.info(f"Wochenfortschritt: {self.sold_this_week:.2f}/{self.weekly_target} EUR")

    def get_weekly_summary(self) -> Dict:
        """Erhalte Zusammenfassung der Woche"""
        return {
            'week_start': self.week_start,
            'target': self.weekly_target,
            'sold': self.sold_this_week,
            'remaining': self.weekly_target - self.sold_this_week,
            'trades_count': len(self.trades_this_week),
            'trades': self.trades_this_week,
            'completion_percent': (self.sold_this_week / self.weekly_target) * 100,
        }
