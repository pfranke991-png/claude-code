"""
PRODUCTION-READY Bitcoin Trading Bot Monitor
Mit Exchange-Integration, Benachrichtigungen, und Multi-Exchange Support

VOLLSTÄNDIG EINSATZBEREIT FÜR IHR HAUPT-BITCOIN!
"""

import time
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from collections import deque
import sys

import config
from strategy import ConservativeStrategy
from exchange import ExchangeConnector, MultiExchangeManager
from notifications import NotificationManager

# Logging Setup
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class AdvancedBitcoinMonitor:
    """
    PRODUCTION-READY 24/7 Bitcoin Trading Bot

    Features:
    ✅ Multi-Exchange Support (Binance, Kraken, etc.)
    ✅ Telegram & Email Benachrichtigungen
    ✅ Automatische Failover
    ✅ Erweiterte Sicherheits-Features
    ✅ Rate Limiting
    ✅ Error Recovery
    ✅ Detailliertes Logging
    """

    def __init__(self, reference_price: float = None,
                 exchange_connector: ExchangeConnector = None,
                 use_coingecko: bool = True):
        """
        Args:
            reference_price: Durchschnittlicher Einkaufspreis in EUR/BTC
            exchange_connector: Exchange für echtes Trading (optional)
            use_coingecko: CoinGecko für Preise nutzen (kostenlos)
        """
        self.strategy = ConservativeStrategy()
        self.reference_price = reference_price

        # Exchange
        self.exchange = exchange_connector
        self.use_coingecko = use_coingecko

        # Multi-Exchange Manager (optional)
        self.multi_exchange = None

        # Benachrichtigungen
        self.notifications = NotificationManager()

        # Preis-Historie
        self.price_history = deque(maxlen=1000)

        # Statistiken
        self.stats = {
            'checks_performed': 0,
            'api_errors': 0,
            'signals_detected': 0,
            'trades_executed': 0,
            'trades_failed': 0,
            'last_check': None,
            'last_price': None,
            'uptime_start': datetime.now(),
        }

        # Error Recovery
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5

        logger.info("=" * 60)
        logger.info("ADVANCED BITCOIN TRADING BOT")
        logger.info("=" * 60)
        logger.info(f"Referenzpreis: {self.reference_price:.2f} EUR/BTC" if self.reference_price else "Kein Referenzpreis gesetzt")
        logger.info(f"Exchange: {self.exchange.exchange_id if self.exchange else 'CoinGecko API'}")
        logger.info(f"Wochenziel: {config.WEEKLY_TARGET_EUR} EUR")
        logger.info("=" * 60)

    def setup_notifications(self, telegram_token: str = None,
                          telegram_chat_id: str = None):
        """
        Konfiguriere Benachrichtigungen

        Args:
            telegram_token: Telegram Bot Token
            telegram_chat_id: Telegram Chat ID
        """
        if telegram_token and telegram_chat_id:
            self.notifications.add_telegram(telegram_token, telegram_chat_id)
            logger.info("✓ Telegram Benachrichtigungen konfiguriert")

    def setup_multi_exchange(self, exchanges: Dict[str, ExchangeConnector]):
        """
        Konfiguriere Multi-Exchange

        Args:
            exchanges: Dict mit Exchange Name -> Connector
        """
        self.multi_exchange = MultiExchangeManager()

        for name, connector in exchanges.items():
            self.multi_exchange.add_exchange(name, connector)

        logger.info(f"✓ Multi-Exchange mit {len(exchanges)} Exchanges konfiguriert")

    def fetch_current_price(self) -> Optional[float]:
        """
        Holt aktuellen Bitcoin-Preis

        Fallback-Hierarchie:
        1. Exchange API (wenn konfiguriert)
        2. Multi-Exchange (bester Preis)
        3. CoinGecko API (kostenlos)

        Returns:
            Preis in EUR oder None
        """
        # 1. Versuche Multi-Exchange
        if self.multi_exchange:
            try:
                _, price = self.multi_exchange.get_best_price('BTC/EUR')
                if price > 0:
                    logger.debug(f"Preis von Multi-Exchange: {price:.2f} EUR/BTC")
                    return price
            except Exception as e:
                logger.warning(f"Multi-Exchange Fehler: {e}")

        # 2. Versuche Exchange
        if self.exchange:
            try:
                price = self.exchange.get_current_price('BTC/EUR')
                if price:
                    logger.debug(f"Preis von {self.exchange.exchange_id}: {price:.2f} EUR/BTC")
                    return price
            except Exception as e:
                logger.warning(f"Exchange Fehler: {e}")

        # 3. Fallback zu CoinGecko
        if self.use_coingecko:
            try:
                response = requests.get(
                    config.PRICE_API,
                    params={
                        'ids': 'bitcoin',
                        'vs_currencies': 'eur'
                    },
                    timeout=10
                )
                response.raise_for_status()

                data = response.json()
                price = data['bitcoin']['eur']

                logger.debug(f"Preis von CoinGecko: {price:.2f} EUR/BTC")
                return float(price)

            except Exception as e:
                logger.error(f"CoinGecko API-Fehler: {e}")

        # Alle Methoden fehlgeschlagen
        logger.error("Konnte Preis von keiner Quelle abrufen!")
        return None

    def execute_trade(self, price: float, eur_amount: float, btc_amount: float,
                     reason: str):
        """
        Führe Trade aus

        Args:
            price: Aktueller Preis
            eur_amount: EUR Betrag
            btc_amount: BTC Menge
            reason: Verkaufsgrund
        """
        trade_info = {
            'timestamp': datetime.now(),
            'price': price,
            'eur_amount': eur_amount,
            'btc_amount': btc_amount,
            'reason': reason,
        }

        # Entscheide welche Exchange nutzen
        order = None

        if config.DRY_RUN:
            # DRY RUN Mode
            logger.info("=" * 60)
            logger.info("DRY RUN - SIMULIERTER TRADE")
            logger.info(f"Verkaufe: {btc_amount:.8f} BTC")
            logger.info(f"Erhält: {eur_amount:.2f} EUR")
            logger.info(f"Preis: {price:.2f} EUR/BTC")
            logger.info(f"Grund: {reason}")
            logger.info("=" * 60)

            # Simuliere erfolgreichen Trade
            self.strategy.record_trade(eur_amount, btc_amount, price)
            self.stats['trades_executed'] += 1

            # Benachrichtigung
            self.notifications.notify_trade_executed(trade_info)

        elif self.multi_exchange:
            # Multi-Exchange: Verkaufe auf bestem Exchange
            logger.info("Verkaufe auf Exchange mit bestem Preis...")
            order = self.multi_exchange.execute_on_best_exchange(
                btc_amount, 'BTC/EUR', dry_run=False
            )

            if order:
                self.strategy.record_trade(eur_amount, btc_amount, price)
                self.stats['trades_executed'] += 1
                self.notifications.notify_trade_executed(trade_info)
            else:
                self.stats['trades_failed'] += 1
                self.notifications.notify_error(f"Trade fehlgeschlagen: {eur_amount:.2f} EUR")

        elif self.exchange:
            # Single Exchange
            logger.info(f"Verkaufe auf {self.exchange.exchange_id}...")
            order = self.exchange.create_market_sell_order(
                'BTC/EUR', btc_amount, dry_run=False
            )

            if order:
                self.strategy.record_trade(eur_amount, btc_amount, price)
                self.stats['trades_executed'] += 1
                self.notifications.notify_trade_executed(trade_info)
            else:
                self.stats['trades_failed'] += 1
                self.notifications.notify_error(f"Trade fehlgeschlagen: {eur_amount:.2f} EUR")

        else:
            logger.error("Kein Exchange konfiguriert und DRY_RUN=False!")
            self.stats['trades_failed'] += 1

        # Zeige Wochenzusammenfassung
        summary = self.strategy.get_weekly_summary()
        logger.info(f"Wochenfortschritt: {summary['completion_percent']:.1f}% "
                   f"({summary['sold']:.2f}/{summary['target']:.2f} EUR)")

    def check_and_trade(self):
        """Hauptschleife: Preis prüfen und ggf. Trade ausführen"""
        self.stats['checks_performed'] += 1
        self.stats['last_check'] = datetime.now()

        try:
            # 1. Preis abrufen
            current_price = self.fetch_current_price()

            if current_price is None:
                self.consecutive_errors += 1
                logger.warning(f"Konnte Preis nicht abrufen ({self.consecutive_errors}/{self.max_consecutive_errors})")

                if self.consecutive_errors >= self.max_consecutive_errors:
                    error_msg = f"Zu viele aufeinanderfolgende Fehler! ({self.consecutive_errors})"
                    logger.error(error_msg)
                    self.notifications.notify_error(error_msg)

                self.stats['api_errors'] += 1
                return

            # Reset error counter bei Erfolg
            self.consecutive_errors = 0
            self.stats['last_price'] = current_price

            # 2. Historie aktualisieren
            self.price_history.append(current_price)

            # 3. Prüfe Referenzpreis
            if self.reference_price is None:
                logger.warning("Kein Referenzpreis gesetzt!")
                return

            # 4. Prüfe ob genug Historie
            if len(self.price_history) < config.MA_LONG_PERIOD:
                logger.info(f"Sammle Daten... {len(self.price_history)}/{config.MA_LONG_PERIOD}")
                return

            # 5. Strategie-Entscheidung
            should_sell, reason, signals = self.strategy.should_sell(
                current_price=current_price,
                price_history=list(self.price_history),
                reference_price=self.reference_price
            )

            # 6. Logge Entscheidung
            decision = "VERKAUFEN 🔥" if should_sell else "HALTEN ⏳"
            logger.info(f"Preis: {current_price:.2f} EUR/BTC | {decision}")
            logger.debug(f"Grund: {reason}")

            if should_sell:
                self.stats['signals_detected'] += 1

                # Benachrichtige über Signal
                self.notifications.notify_signal_detected(current_price, reason)

                # Berechne Verkaufsmenge
                eur_amount, btc_amount = self.strategy.calculate_sell_amount(current_price)

                # Prüfe Minimum Order Size
                if self.exchange:
                    min_amount = self.exchange.get_minimum_order_amount('BTC/EUR')
                    if btc_amount < min_amount:
                        logger.warning(f"BTC Menge zu klein: {btc_amount:.8f} < {min_amount:.8f}")
                        logger.warning("Erhöhe TRANCHE_SIZE_EUR in config.py")
                        return

                # Führe Trade aus
                self.execute_trade(current_price, eur_amount, btc_amount, reason)

        except Exception as e:
            logger.error(f"Fehler in check_and_trade: {e}", exc_info=True)
            self.stats['api_errors'] += 1
            self.consecutive_errors += 1

    def run(self):
        """Hauptschleife: 24/7 Trading Bot"""
        logger.info("=" * 60)
        logger.info("BOT GESTARTET")
        logger.info(f"Modus: {'DRY RUN (Simulation)' if config.DRY_RUN else '🔴 LIVE TRADING 🔴'}")
        logger.info(f"Ziel: {config.WEEKLY_TARGET_EUR} EUR/Woche")
        logger.info(f"Prüf-Intervall: {config.PRICE_CHECK_INTERVAL_SECONDS}s")
        logger.info("=" * 60)

        # Benachrichtige über Start
        self.notifications.notify_bot_started()

        try:
            while True:
                try:
                    # Check und ggf. Trade
                    self.check_and_trade()

                    # Statistiken (jede Stunde)
                    if self.stats['checks_performed'] % 12 == 0:
                        self.print_stats()

                    # Wöchentliche Zusammenfassung (Sonntag 20:00)
                    now = datetime.now()
                    if now.weekday() == 6 and now.hour == 20 and now.minute < 5:
                        summary = self.strategy.get_weekly_summary()
                        self.notifications.notify_weekly_summary(summary)

                    # Warten
                    time.sleep(config.PRICE_CHECK_INTERVAL_SECONDS)

                except KeyboardInterrupt:
                    raise

                except Exception as e:
                    logger.error(f"Fehler in Hauptschleife: {e}", exc_info=True)
                    time.sleep(60)  # Warte 1 Minute bei Fehler

        except KeyboardInterrupt:
            logger.info("Bot gestoppt durch Benutzer")
            summary = self.strategy.get_weekly_summary()
            self.notifications.notify_bot_stopped(summary)
            self.print_final_summary()

    def print_stats(self):
        """Zeige Statistiken"""
        uptime = datetime.now() - self.stats['uptime_start']

        logger.info("=" * 60)
        logger.info("STATISTIKEN")
        logger.info(f"Uptime: {uptime}")
        logger.info(f"Checks: {self.stats['checks_performed']}")
        logger.info(f"API-Fehler: {self.stats['api_errors']}")
        logger.info(f"Signale: {self.stats['signals_detected']}")
        logger.info(f"Trades erfolgreich: {self.stats['trades_executed']}")
        logger.info(f"Trades fehlgeschlagen: {self.stats['trades_failed']}")
        logger.info(f"Letzter Preis: {self.stats['last_price']:.2f} EUR/BTC")

        summary = self.strategy.get_weekly_summary()
        logger.info(f"Woche: {summary['sold']:.2f}/{summary['target']:.2f} EUR "
                   f"({summary['completion_percent']:.1f}%)")
        logger.info("=" * 60)

    def print_final_summary(self):
        """Finale Zusammenfassung"""
        logger.info("=" * 60)
        logger.info("FINALE ZUSAMMENFASSUNG")
        logger.info("=" * 60)

        self.print_stats()

        summary = self.strategy.get_weekly_summary()

        if summary['trades']:
            logger.info("\nTRADES DIESE WOCHE:")
            for i, trade in enumerate(summary['trades'], 1):
                logger.info(f"{i}. {trade['timestamp'].strftime('%Y-%m-%d %H:%M')} | "
                           f"{trade['btc_amount']:.8f} BTC @ {trade['price']:.2f} EUR/BTC | "
                           f"{trade['eur_amount']:.2f} EUR")

        logger.info("\nBot beendet.")


def main():
    """
    Haupteinstiegspunkt für PRODUCTION BOT

    Unterstützt verschiedene Modi:
    1. Nur Simulation (DRY_RUN=True)
    2. Mit Exchange (DRY_RUN=False)
    3. Mit Multi-Exchange
    4. Mit Benachrichtigungen
    """
    print("=" * 60)
    print("BITCOIN TRADING BOT - PRODUCTION READY")
    print("=" * 60)
    print()

    # Prüfe Argumente
    if len(sys.argv) < 2:
        print("FEHLER: Referenzpreis fehlt!")
        print()
        print("Verwendung:")
        print("  python monitor_advanced.py <referenzpreis>")
        print()
        print("Beispiel:")
        print("  python monitor_advanced.py 45000")
        print()
        print("Der Referenzpreis ist Ihr durchschnittlicher Bitcoin-Einkaufspreis.")
        sys.exit(1)

    try:
        reference_price = float(sys.argv[1])

        if reference_price <= 0:
            print("FEHLER: Referenzpreis muss positiv sein!")
            sys.exit(1)

    except ValueError:
        print("FEHLER: Referenzpreis muss eine Zahl sein!")
        sys.exit(1)

    # Erstelle Monitor
    monitor = AdvancedBitcoinMonitor(reference_price=reference_price)

    # Optional: Exchange konfigurieren
    # WICHTIG: Nur aktivieren wenn Sie echte API Keys haben!
    # exchange = ExchangeConnector('binance', 'YOUR_API_KEY', 'YOUR_API_SECRET', testnet=True)
    # monitor.exchange = exchange

    # Optional: Telegram konfigurieren
    # WICHTIG: Nur aktivieren wenn Sie Bot Token haben!
    # monitor.setup_notifications(
    #     telegram_token='YOUR_BOT_TOKEN',
    #     telegram_chat_id='YOUR_CHAT_ID'
    # )

    # Starte Bot
    monitor.run()


if __name__ == "__main__":
    main()
