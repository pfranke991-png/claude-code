"""
24/7 Bitcoin Preis Monitor
Emotionslos und kontinuierlich - überwacht den Markt und führt Trades aus
"""

import time
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from collections import deque

import config
from strategy import ConservativeStrategy

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


class BitcoinPriceMonitor:
    """
    24/7 Preis-Überwachung und Trading-Ausführung

    Vorteile gegenüber manueller Überwachung:
    - Keine Emotionen
    - Niemals müde
    - Präzise Timing
    - Kontinuierliche Analyse
    """

    def __init__(self, reference_price: float = None):
        """
        Args:
            reference_price: Durchschnittlicher Einkaufspreis in EUR/BTC
                           Wird für Gewinnberechnung verwendet
        """
        self.strategy = ConservativeStrategy()
        self.reference_price = reference_price

        # Preis-Historie (Rolling Window)
        # Speichert bis zu 30 Tage an Preisen (bei 5-Min Intervall = ~8640 Datenpunkte)
        # Wir begrenzen auf die letzten 1000 für Speicher-Effizienz
        self.price_history = deque(maxlen=1000)

        # Statistiken
        self.stats = {
            'checks_performed': 0,
            'api_errors': 0,
            'signals_detected': 0,
            'trades_executed': 0,
            'last_check': None,
            'last_price': None,
        }

        logger.info("Bitcoin Price Monitor initialisiert")
        if self.reference_price:
            logger.info(f"Referenzpreis: {self.reference_price:.2f} EUR/BTC")

    def fetch_current_price(self) -> Optional[float]:
        """
        Holt aktuellen Bitcoin-Preis von CoinGecko API

        Returns:
            Preis in EUR oder None bei Fehler
        """
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

            logger.debug(f"Preis abgerufen: {price:.2f} EUR/BTC")
            return float(price)

        except requests.exceptions.RequestException as e:
            logger.error(f"API-Fehler beim Preisabruf: {e}")
            self.stats['api_errors'] += 1
            return None

        except (KeyError, ValueError) as e:
            logger.error(f"Fehler beim Parsen der API-Antwort: {e}")
            self.stats['api_errors'] += 1
            return None

    def update_price_history(self, price: float):
        """Füge Preis zur Historie hinzu"""
        self.price_history.append(price)
        logger.debug(f"Preis-Historie aktualisiert: {len(self.price_history)} Einträge")

    def execute_trade(self, price: float, eur_amount: float, btc_amount: float):
        """
        Führe Trade aus (oder simuliere im DRY_RUN Modus)

        Args:
            price: Aktueller Preis
            eur_amount: Zu verkaufende EUR-Menge
            btc_amount: Zu verkaufende BTC-Menge
        """
        if config.DRY_RUN:
            logger.info("=" * 60)
            logger.info("DRY RUN - SIMULIERTER TRADE")
            logger.info(f"Verkaufe: {btc_amount:.8f} BTC")
            logger.info(f"Erhält: {eur_amount:.2f} EUR")
            logger.info(f"Preis: {price:.2f} EUR/BTC")
            logger.info(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)

            # Simuliere erfolgreichen Trade
            self.strategy.record_trade(eur_amount, btc_amount, price)
            self.stats['trades_executed'] += 1

        else:
            # ECHTER TRADE
            # WICHTIG: Hier muss Exchange-spezifischer Code eingefügt werden!
            logger.warning("ECHTER TRADE-MODUS NICHT IMPLEMENTIERT!")
            logger.warning("Bitte Exchange API Integration hinzufügen in execute_trade()")

            # Beispiel für Exchange-Integration:
            # try:
            #     exchange = ccxt.binance({
            #         'apiKey': config.EXCHANGE_API_KEY,
            #         'secret': config.EXCHANGE_API_SECRET,
            #     })
            #     order = exchange.create_market_sell_order('BTC/EUR', btc_amount)
            #     self.strategy.record_trade(eur_amount, btc_amount, price)
            #     self.stats['trades_executed'] += 1
            #     logger.info(f"Trade ausgeführt: {order}")
            # except Exception as e:
            #     logger.error(f"Trade-Fehler: {e}")

    def check_and_trade(self):
        """
        Hauptschleife: Preis prüfen und ggf. Trade ausführen
        """
        self.stats['checks_performed'] += 1
        self.stats['last_check'] = datetime.now()

        # 1. Preis abrufen
        current_price = self.fetch_current_price()

        if current_price is None:
            logger.warning("Konnte Preis nicht abrufen, überspringe diesen Check")
            return

        self.stats['last_price'] = current_price

        # 2. Historie aktualisieren
        self.update_price_history(current_price)

        # 3. Prüfe ob wir Referenzpreis haben
        if self.reference_price is None:
            logger.warning("Kein Referenzpreis gesetzt! Bitte setzen für Gewinnberechnung.")
            return

        # 4. Prüfe ob genug Historie für Analyse
        if len(self.price_history) < config.MA_LONG_PERIOD:
            logger.info(f"Sammle Preis-Daten... {len(self.price_history)}/{config.MA_LONG_PERIOD}")
            return

        # 5. Strategie-Entscheidung
        should_sell, reason, signals = self.strategy.should_sell(
            current_price=current_price,
            price_history=list(self.price_history),
            reference_price=self.reference_price
        )

        # 6. Logge Entscheidung
        logger.info(f"Preis: {current_price:.2f} EUR/BTC | Entscheidung: {'VERKAUFEN' if should_sell else 'HALTEN'}")
        logger.info(f"Grund: {reason}")

        if should_sell:
            self.stats['signals_detected'] += 1

            # Berechne Verkaufsmenge
            eur_amount, btc_amount = self.strategy.calculate_sell_amount(current_price)

            # Führe Trade aus
            self.execute_trade(current_price, eur_amount, btc_amount)

            # Zeige Wochenzusammenfassung
            summary = self.strategy.get_weekly_summary()
            logger.info(f"Wochenfortschritt: {summary['completion_percent']:.1f}% "
                       f"({summary['sold']:.2f}/{summary['target']:.2f} EUR)")

    def run(self):
        """
        Hauptschleife: Läuft kontinuierlich 24/7

        Emotionslos und präzise - genau das, was ein Mensch nicht kann.
        """
        logger.info("=" * 60)
        logger.info("BITCOIN TRADING BOT GESTARTET")
        logger.info(f"Modus: {'DRY RUN (Simulation)' if config.DRY_RUN else 'LIVE TRADING'}")
        logger.info(f"Ziel: {config.WEEKLY_TARGET_EUR} EUR/Woche")
        logger.info(f"Prüf-Intervall: {config.PRICE_CHECK_INTERVAL_SECONDS}s")
        logger.info("=" * 60)

        try:
            while True:
                try:
                    # Prüfen und ggf. handeln
                    self.check_and_trade()

                    # Statistiken ausgeben (jede Stunde)
                    if self.stats['checks_performed'] % 12 == 0:  # 12 * 5 Min = 1 Stunde
                        self.print_stats()

                    # Warten bis zum nächsten Check
                    time.sleep(config.PRICE_CHECK_INTERVAL_SECONDS)

                except KeyboardInterrupt:
                    raise

                except Exception as e:
                    logger.error(f"Fehler in Hauptschleife: {e}", exc_info=True)
                    time.sleep(60)  # Bei Fehler 1 Minute warten

        except KeyboardInterrupt:
            logger.info("Bot gestoppt durch Benutzer")
            self.print_final_summary()

    def print_stats(self):
        """Zeige Statistiken"""
        logger.info("=" * 60)
        logger.info("STATISTIKEN")
        logger.info(f"Checks: {self.stats['checks_performed']}")
        logger.info(f"API-Fehler: {self.stats['api_errors']}")
        logger.info(f"Signale erkannt: {self.stats['signals_detected']}")
        logger.info(f"Trades ausgeführt: {self.stats['trades_executed']}")
        logger.info(f"Letzter Preis: {self.stats['last_price']:.2f} EUR/BTC")

        summary = self.strategy.get_weekly_summary()
        logger.info(f"Woche: {summary['sold']:.2f}/{summary['target']:.2f} EUR "
                   f"({summary['completion_percent']:.1f}%)")
        logger.info("=" * 60)

    def print_final_summary(self):
        """Zeige finale Zusammenfassung beim Beenden"""
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
    Haupteinstiegspunkt

    WICHTIG: Referenzpreis muss gesetzt werden!
    Dies ist Ihr durchschnittlicher Bitcoin-Einkaufspreis.
    """
    import sys

    # Prüfe ob Referenzpreis als Argument übergeben wurde
    if len(sys.argv) < 2:
        print("=" * 60)
        print("FEHLER: Referenzpreis fehlt!")
        print("=" * 60)
        print("\nVerwendung:")
        print("  python monitor.py <referenzpreis>")
        print("\nBeispiel:")
        print("  python monitor.py 45000")
        print("\nDer Referenzpreis ist Ihr durchschnittlicher Bitcoin-Einkaufspreis")
        print("in EUR/BTC. Dieser wird für die Gewinnberechnung verwendet.")
        print("=" * 60)
        sys.exit(1)

    try:
        reference_price = float(sys.argv[1])

        if reference_price <= 0:
            print("FEHLER: Referenzpreis muss positiv sein!")
            sys.exit(1)

    except ValueError:
        print("FEHLER: Referenzpreis muss eine Zahl sein!")
        sys.exit(1)

    # Starte Monitor
    monitor = BitcoinPriceMonitor(reference_price=reference_price)
    monitor.run()


if __name__ == "__main__":
    main()
