"""
Backtesting-System für Bitcoin Trading Strategie

Testet die Strategie mit historischen Daten um zu sehen,
wie sie in der Vergangenheit performed hätte.
"""

import requests
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json

import config
from strategy import ConservativeStrategy


class Backtester:
    """
    Backtesting für konservative Trading-Strategie

    Simuliert Trades über historische Zeiträume
    """

    def __init__(self, reference_price: float):
        """
        Args:
            reference_price: Durchschnittlicher Einkaufspreis in EUR/BTC
        """
        self.reference_price = reference_price
        self.strategy = ConservativeStrategy()

        # Ergebnisse
        self.results = {
            'trades': [],
            'total_eur_sold': 0.0,
            'total_btc_sold': 0.0,
            'avg_sell_price': 0.0,
            'best_price': 0.0,
            'worst_price': float('inf'),
            'weeks_simulated': 0,
        }

    def fetch_historical_prices(self, days: int = 30) -> List[Tuple[datetime, float]]:
        """
        Holt historische Bitcoin-Preise von CoinGecko

        Args:
            days: Anzahl Tage zurück (max 365 für kostenlose API)

        Returns:
            Liste von (timestamp, price) Tupeln
        """
        print(f"Lade historische Preise für {days} Tage...")

        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart",
                params={
                    'vs_currency': 'eur',
                    'days': days,
                    'interval': 'hourly' if days <= 90 else 'daily'
                },
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            prices_data = data['prices']

            # Konvertiere zu (datetime, price) Tupeln
            prices = [
                (datetime.fromtimestamp(timestamp / 1000), price)
                for timestamp, price in prices_data
            ]

            print(f"✓ {len(prices)} Preispunkte geladen")
            return prices

        except requests.exceptions.RequestException as e:
            print(f"✗ Fehler beim Laden historischer Preise: {e}")
            return []

    def simulate_week(self, week_prices: List[Tuple[datetime, float]]) -> Dict:
        """
        Simuliere eine Woche Trading

        Args:
            week_prices: Preise für diese Woche

        Returns:
            Wochen-Zusammenfassung
        """
        week_summary = {
            'trades': [],
            'eur_sold': 0.0,
            'btc_sold': 0.0,
            'opportunities_found': 0,
        }

        # Reset Strategie für neue Woche
        self.strategy.sold_this_week = 0.0
        self.strategy.trades_this_week = []

        # Simuliere jeden Tag
        for day in range(7):
            # Preise für diesen Tag
            day_start = day * 24
            day_end = min((day + 1) * 24, len(week_prices))

            if day_start >= len(week_prices):
                break

            day_prices = week_prices[day_start:day_end]

            if not day_prices:
                continue

            # Suche besten Verkaufszeitpunkt des Tages
            best_opportunity = None
            best_score = 0

            for timestamp, price in day_prices:
                # Prüfe ob Handelsfenster (8-22 Uhr)
                hour = timestamp.hour
                if hour < config.TRADING_WINDOW_START_HOUR or hour >= config.TRADING_WINDOW_END_HOUR:
                    continue

                # Prüfe Verkaufskriterien
                # Für Backtest: Verwenden wir vereinfachte Kriterien
                profit_percent = ((price - self.reference_price) / self.reference_price) * 100

                if profit_percent < config.MIN_PROFIT_THRESHOLD:
                    continue

                # Berechne "Score" für diesen Zeitpunkt
                # Höherer Preis = besserer Score
                score = price

                if score > best_score:
                    best_score = score
                    best_opportunity = (timestamp, price)

            # Wenn gute Gelegenheit gefunden, verkaufe
            if best_opportunity and self.strategy.sold_this_week < self.strategy.weekly_target:
                timestamp, price = best_opportunity

                # Berechne Verkaufsmenge
                remaining = self.strategy.weekly_target - self.strategy.sold_this_week
                eur_amount = min(self.strategy.tranche_size, remaining)
                btc_amount = eur_amount / price

                # Führe virtuellen Trade aus
                trade = {
                    'timestamp': timestamp,
                    'price': price,
                    'eur_amount': eur_amount,
                    'btc_amount': btc_amount,
                    'profit_percent': ((price - self.reference_price) / self.reference_price) * 100,
                }

                week_summary['trades'].append(trade)
                week_summary['eur_sold'] += eur_amount
                week_summary['btc_sold'] += btc_amount
                week_summary['opportunities_found'] += 1

                self.strategy.sold_this_week += eur_amount

                # Aktualisiere globale Best/Worst
                if price > self.results['best_price']:
                    self.results['best_price'] = price
                if price < self.results['worst_price']:
                    self.results['worst_price'] = price

        return week_summary

    def run_backtest(self, days: int = 30):
        """
        Führe Backtest über angegebenen Zeitraum aus

        Args:
            days: Anzahl Tage für Backtest (empfohlen: 30-90)
        """
        print("=" * 60)
        print("BACKTESTING GESTARTET")
        print("=" * 60)
        print(f"Zeitraum: {days} Tage")
        print(f"Referenzpreis: {self.reference_price:.2f} EUR/BTC")
        print(f"Wochenziel: {config.WEEKLY_TARGET_EUR} EUR")
        print("=" * 60)
        print()

        # Lade historische Daten
        historical_prices = self.fetch_historical_prices(days)

        if not historical_prices:
            print("Backtest abgebrochen: Keine Daten verfügbar")
            return

        print()

        # Teile in Wochen auf
        num_weeks = days // 7
        self.results['weeks_simulated'] = num_weeks

        for week in range(num_weeks):
            week_start_idx = week * 7 * 24  # 7 Tage * 24 Stunden
            week_end_idx = min((week + 1) * 7 * 24, len(historical_prices))

            week_prices = historical_prices[week_start_idx:week_end_idx]

            if not week_prices:
                break

            # Simuliere diese Woche
            week_summary = self.simulate_week(week_prices)

            # Ausgabe
            week_start_date = week_prices[0][0].strftime('%Y-%m-%d')
            print(f"Woche {week + 1} ({week_start_date}):")
            print(f"  Trades: {week_summary['opportunities_found']}")
            print(f"  Verkauft: {week_summary['eur_sold']:.2f} EUR ({week_summary['btc_sold']:.8f} BTC)")

            if week_summary['trades']:
                avg_price = week_summary['eur_sold'] / week_summary['btc_sold']
                print(f"  Ø Preis: {avg_price:.2f} EUR/BTC")

            print()

            # Speichere Trades
            self.results['trades'].extend(week_summary['trades'])
            self.results['total_eur_sold'] += week_summary['eur_sold']
            self.results['total_btc_sold'] += week_summary['btc_sold']

        # Berechne finale Statistiken
        self.print_results()

    def print_results(self):
        """Zeige Backtest-Ergebnisse"""
        print("=" * 60)
        print("BACKTEST ERGEBNISSE")
        print("=" * 60)

        if not self.results['trades']:
            print("Keine Trades im Backtest-Zeitraum!")
            print("Mögliche Gründe:")
            print("- Referenzpreis zu hoch (Mindestgewinn nie erreicht)")
            print("- Zu konservative Parameter")
            print("- Ungünstiger Marktzeitraum")
            return

        # Gesamtstatistiken
        print(f"\nWochen simuliert: {self.results['weeks_simulated']}")
        print(f"Trades ausgeführt: {len(self.results['trades'])}")
        print(f"Gesamt verkauft: {self.results['total_eur_sold']:.2f} EUR")
        print(f"Gesamt verkauft: {self.results['total_btc_sold']:.8f} BTC")

        # Durchschnittlicher Verkaufspreis
        if self.results['total_btc_sold'] > 0:
            avg_price = self.results['total_eur_sold'] / self.results['total_btc_sold']
            self.results['avg_sell_price'] = avg_price
            print(f"\nØ Verkaufspreis: {avg_price:.2f} EUR/BTC")
            print(f"Referenzpreis: {self.reference_price:.2f} EUR/BTC")

            profit_vs_ref = ((avg_price - self.reference_price) / self.reference_price) * 100
            print(f"Gewinn vs. Referenz: {profit_vs_ref:+.2f}%")

        # Best/Worst Trades
        if self.results['best_price'] > 0:
            print(f"\nBester Verkaufspreis: {self.results['best_price']:.2f} EUR/BTC")
        if self.results['worst_price'] != float('inf'):
            print(f"Schlechtester Verkaufspreis: {self.results['worst_price']:.2f} EUR/BTC")

        # Trades pro Woche
        trades_per_week = len(self.results['trades']) / max(self.results['weeks_simulated'], 1)
        print(f"\nØ Trades pro Woche: {trades_per_week:.1f}")

        target_per_week = config.WEEKLY_TARGET_EUR
        actual_per_week = self.results['total_eur_sold'] / max(self.results['weeks_simulated'], 1)
        print(f"Ziel pro Woche: {target_per_week:.2f} EUR")
        print(f"Tatsächlich pro Woche: {actual_per_week:.2f} EUR")
        completion = (actual_per_week / target_per_week) * 100
        print(f"Ziel-Erreichung: {completion:.1f}%")

        # Detail-Liste (erste 5 Trades)
        print("\n" + "=" * 60)
        print("ERSTE 5 TRADES:")
        print("=" * 60)

        for i, trade in enumerate(self.results['trades'][:5], 1):
            print(f"\n{i}. {trade['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            print(f"   Preis: {trade['price']:.2f} EUR/BTC")
            print(f"   Verkauft: {trade['eur_amount']:.2f} EUR ({trade['btc_amount']:.8f} BTC)")
            print(f"   Gewinn: {trade['profit_percent']:+.2f}%")

        if len(self.results['trades']) > 5:
            print(f"\n... und {len(self.results['trades']) - 5} weitere Trades")

        print("\n" + "=" * 60)

        # Empfehlungen
        print("\nEMPFEHLUNGEN:")

        if completion < 50:
            print("⚠ Ziel-Erreichung unter 50%")
            print("  → Parameter weniger konservativ setzen")
            print("  → MIN_PROFIT_THRESHOLD reduzieren")

        if trades_per_week < 3:
            print("⚠ Wenige Trades pro Woche")
            print("  → Verkaufskriterien lockern")

        if profit_vs_ref < 0:
            print("⚠ Durchschnittlicher Verkaufspreis unter Referenzpreis!")
            print("  → Referenzpreis überprüfen")
            print("  → Ungünstiger Marktzeitraum")

        if completion >= 80 and profit_vs_ref > 1:
            print("✓ Strategie funktioniert gut!")
            print("✓ Gute Ziel-Erreichung und Gewinn")

        print("=" * 60)


def main():
    """
    Haupteinstiegspunkt für Backtest
    """
    import sys

    print()
    print("=" * 60)
    print("BITCOIN TRADING BOT - BACKTESTING")
    print("=" * 60)
    print()

    # Referenzpreis
    if len(sys.argv) < 2:
        print("Verwendung: python backtest.py <referenzpreis> [tage]")
        print()
        print("Beispiel:")
        print("  python backtest.py 45000      # Backtest über 30 Tage")
        print("  python backtest.py 45000 90   # Backtest über 90 Tage")
        print()
        sys.exit(1)

    try:
        reference_price = float(sys.argv[1])
    except ValueError:
        print("FEHLER: Referenzpreis muss eine Zahl sein!")
        sys.exit(1)

    # Tage (optional)
    days = 30  # Standard
    if len(sys.argv) >= 3:
        try:
            days = int(sys.argv[2])
            if days < 7 or days > 365:
                print("FEHLER: Tage müssen zwischen 7 und 365 liegen!")
                sys.exit(1)
        except ValueError:
            print("FEHLER: Tage müssen eine Zahl sein!")
            sys.exit(1)

    # Starte Backtest
    backtester = Backtester(reference_price=reference_price)
    backtester.run_backtest(days=days)


if __name__ == "__main__":
    main()
