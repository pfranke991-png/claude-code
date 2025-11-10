"""
Bitcoin Trading Bot - Core API Connector
=========================================
Binance Testnet Integration mit Fehlerbehandlung und Sicherheits-Features

✅ CHECKPOINT 1: Binance Testnet Verbindung
- API-Key Integration
- Verbindungstest
- Balance-Abfrage
- Preis-Abfrage
"""

import time
from typing import Dict, Optional, Tuple
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from datetime import datetime, timedelta


class BinanceTradingBot:
    """
    Haupt-Connector für Binance Testnet API

    Verantwortlichkeiten:
    - API-Verbindung verwalten
    - Kontostände abfragen
    - Preise abrufen
    - Orders platzieren (in Phase 2)
    - Fehler mit Retry-Logik behandeln
    - Rate-Limits respektieren
    """

    def __init__(self, api_key: str, api_secret: str, config: dict, logger):
        """
        Initialisiere Binance-Connector

        Args:
            api_key: Binance Testnet API Key
            api_secret: Binance Testnet Secret Key
            config: Bot-Konfiguration
            logger: Logger-Instanz
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.config = config
        self.logger = logger

        # Trading-Pair (z.B. BTCUSDT)
        self.symbol = config['trading']['symbol']

        # API-Konfiguration
        self.max_retries = config['api']['max_retries']
        self.retry_delay = config['api']['retry_delay']
        self.request_timeout = config['api']['request_timeout']

        # Rate-Limiting: Tracking der API-Calls
        self.api_call_timestamps = []
        self.max_calls_per_minute = config['safety']['max_api_calls_per_minute']

        # Client-Instanz (wird in connect() initialisiert)
        self.client: Optional[Client] = None

        # ✅ CHECKPOINT: Initialisierung erfolgreich
        self.logger.info(f"BinanceTradingBot initialisiert für {self.symbol}")

    # ===================================================================
    # ✅ CHECKPOINT 1.1: API-Verbindung & Tests
    # ===================================================================

    def connect(self) -> bool:
        """
        Stelle Verbindung zu Binance Testnet her

        Returns:
            True wenn Verbindung erfolgreich, False sonst
        """
        try:
            self.logger.info("Verbinde mit Binance Testnet...")

            # Erstelle Client mit Testnet-URL
            self.client = Client(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=True  # ✅ WICHTIG: Testnet-Modus aktivieren
            )

            # ✅ CHECKPOINT: Teste Verbindung mit Server-Zeit
            server_time = self.client.get_server_time()
            self.logger.info(
                f"Verbindung erfolgreich | Server-Zeit: "
                f"{datetime.fromtimestamp(server_time['serverTime']/1000)}"
            )

            # ✅ CHECKPOINT: Teste API-Key Permissions
            account_info = self.client.get_account()
            self.logger.info(
                f"API-Key Permissions validiert | "
                f"Account Type: {account_info.get('accountType', 'Unknown')}"
            )

            return True

        except BinanceAPIException as e:
            self.logger.error(
                f"Binance API Fehler bei Verbindungsaufbau: {e.status_code} - {e.message}",
                exc_info=True
            )
            return False

        except BinanceRequestException as e:
            self.logger.error(
                f"Binance Request Fehler: {str(e)}",
                exc_info=True
            )
            return False

        except Exception as e:
            self.logger.error(
                f"Unerwarteter Fehler bei Verbindung: {str(e)}",
                exc_info=True
            )
            return False

    def test_connection(self) -> Dict[str, any]:
        """
        Führe umfassenden Verbindungstest durch

        Returns:
            Dictionary mit Testergebnissen
        """
        results = {
            'connection': False,
            'balance_query': False,
            'price_query': False,
            'errors': []
        }

        try:
            # Test 1: Verbindung
            if self.connect():
                results['connection'] = True
                self.logger.info("✓ Verbindungstest bestanden")
            else:
                results['errors'].append("Verbindung fehlgeschlagen")
                return results

            # Test 2: Balance-Abfrage
            balances = self.get_balances()
            if balances:
                results['balance_query'] = True
                self.logger.info("✓ Balance-Abfrage erfolgreich")
            else:
                results['errors'].append("Balance-Abfrage fehlgeschlagen")

            # Test 3: Preis-Abfrage
            price = self.get_current_price()
            if price > 0:
                results['price_query'] = True
                self.logger.info(f"✓ Preis-Abfrage erfolgreich: {price} USDT")
            else:
                results['errors'].append("Preis-Abfrage fehlgeschlagen")

        except Exception as e:
            results['errors'].append(f"Test-Fehler: {str(e)}")
            self.logger.error(f"Fehler beim Verbindungstest: {str(e)}", exc_info=True)

        return results

    # ===================================================================
    # ✅ CHECKPOINT 1.2: Balance-Abfrage
    # ===================================================================

    def get_balances(self) -> Optional[Dict[str, float]]:
        """
        Hole aktuelle Kontostände für BTC und USDT

        Returns:
            Dictionary mit {'BTC': amount, 'USDT': amount} oder None bei Fehler
        """
        if not self.client:
            self.logger.error("Client nicht verbunden. Rufe connect() zuerst auf.")
            return None

        # ✅ Rate-Limiting prüfen
        if not self._check_rate_limit():
            self.logger.warning("Rate-Limit erreicht, warte...")
            time.sleep(1)

        # Retry-Logik
        for attempt in range(self.max_retries):
            try:
                self._track_api_call()

                # Hole Account-Info
                account = self.client.get_account()

                # Extrahiere BTC und USDT Balances
                balances = {}
                for balance in account['balances']:
                    asset = balance['asset']
                    if asset in ['BTC', 'USDT']:
                        free = float(balance['free'])
                        locked = float(balance['locked'])
                        total = free + locked
                        balances[asset] = {
                            'free': free,
                            'locked': locked,
                            'total': total
                        }

                # ✅ CHECKPOINT: Validiere dass wir beide Assets haben
                if 'BTC' in balances and 'USDT' in balances:
                    self.logger.debug(
                        f"Balance abgerufen | BTC: {balances['BTC']['total']:.8f} | "
                        f"USDT: {balances['USDT']['total']:.2f}"
                    )
                    return balances
                else:
                    self.logger.warning(
                        f"BTC oder USDT nicht im Account gefunden. "
                        f"Verfügbare Assets: {list(balances.keys())}"
                    )
                    return None

            except BinanceAPIException as e:
                self._handle_api_error("get_balances", e, attempt)
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    return None

            except Exception as e:
                self.logger.error(f"Unerwarteter Fehler bei Balance-Abfrage: {str(e)}", exc_info=True)
                return None

        return None

    # ===================================================================
    # ✅ CHECKPOINT 1.3: Preis-Abfrage
    # ===================================================================

    def get_current_price(self) -> Optional[float]:
        """
        Hole aktuellen BTC-Preis in USDT

        Returns:
            Aktueller Preis als float oder None bei Fehler
        """
        if not self.client:
            self.logger.error("Client nicht verbunden. Rufe connect() zuerst auf.")
            return None

        # ✅ Rate-Limiting prüfen
        if not self._check_rate_limit():
            self.logger.warning("Rate-Limit erreicht, warte...")
            time.sleep(1)

        # Retry-Logik
        for attempt in range(self.max_retries):
            try:
                self._track_api_call()

                # Hole aktuellen Ticker-Preis
                ticker = self.client.get_symbol_ticker(symbol=self.symbol)
                price = float(ticker['price'])

                self.logger.debug(f"Preis abgerufen | {self.symbol}: {price:.2f} USDT")
                return price

            except BinanceAPIException as e:
                self._handle_api_error("get_current_price", e, attempt)
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    return None

            except Exception as e:
                self.logger.error(f"Unerwarteter Fehler bei Preis-Abfrage: {str(e)}", exc_info=True)
                return None

        return None

    def get_24h_price_stats(self) -> Optional[Dict[str, float]]:
        """
        Hole 24h Preis-Statistiken

        Returns:
            Dictionary mit Statistiken (high, low, avg, change) oder None
        """
        if not self.client:
            self.logger.error("Client nicht verbunden. Rufe connect() zuerst auf.")
            return None

        if not self._check_rate_limit():
            time.sleep(1)

        try:
            self._track_api_call()

            ticker = self.client.get_ticker(symbol=self.symbol)

            stats = {
                'current': float(ticker['lastPrice']),
                'high_24h': float(ticker['highPrice']),
                'low_24h': float(ticker['lowPrice']),
                'volume_24h': float(ticker['volume']),
                'price_change_24h': float(ticker['priceChange']),
                'price_change_percent_24h': float(ticker['priceChangePercent'])
            }

            self.logger.debug(
                f"24h Stats | High: {stats['high_24h']:.2f} | "
                f"Low: {stats['low_24h']:.2f} | "
                f"Change: {stats['price_change_percent_24h']:.2f}%"
            )

            return stats

        except Exception as e:
            self.logger.error(f"Fehler bei 24h Stats-Abfrage: {str(e)}", exc_info=True)
            return None

    # ===================================================================
    # Rate-Limiting & Error-Handling
    # ===================================================================

    def _check_rate_limit(self) -> bool:
        """
        Prüfe ob Rate-Limit eingehalten wird

        Returns:
            True wenn OK, False wenn Limit erreicht
        """
        now = time.time()

        # Entferne Timestamps älter als 1 Minute
        self.api_call_timestamps = [
            ts for ts in self.api_call_timestamps
            if now - ts < 60
        ]

        # Prüfe Anzahl der Calls in letzter Minute
        return len(self.api_call_timestamps) < self.max_calls_per_minute

    def _track_api_call(self):
        """
        Registriere einen API-Call für Rate-Limiting
        """
        self.api_call_timestamps.append(time.time())

    def _handle_api_error(self, function_name: str, error: BinanceAPIException, attempt: int):
        """
        Behandle Binance API-Fehler mit detailliertem Logging

        Args:
            function_name: Name der Funktion die fehlschlug
            error: BinanceAPIException
            attempt: Aktueller Retry-Versuch
        """
        error_code = error.code
        error_msg = error.message

        # Spezielle Behandlung für bekannte Fehler
        if error_code == -1021:
            self.logger.error(
                f"Timestamp-Fehler in {function_name} | "
                f"Systemzeit möglicherweise nicht synchronisiert"
            )
        elif error_code == -2015:
            self.logger.error(f"Ungültiger API-Key in {function_name}")
        elif error_code == -1003:
            self.logger.warning(f"Rate-Limit überschritten in {function_name}")
        else:
            self.logger.error(
                f"API-Fehler in {function_name} | "
                f"Code: {error_code} | Message: {error_msg} | "
                f"Versuch: {attempt + 1}/{self.max_retries}"
            )

    # ===================================================================
    # Hilfsfunktionen
    # ===================================================================

    def get_account_status(self) -> Dict[str, any]:
        """
        Hole umfassenden Account-Status

        Returns:
            Dictionary mit allen relevanten Account-Informationen
        """
        balances = self.get_balances()
        price = self.get_current_price()

        if not balances or not price:
            return {'error': 'Konnte Account-Status nicht abrufen'}

        btc_balance = balances['BTC']['total']
        usdt_balance = balances['USDT']['total']
        total_value_usdt = (btc_balance * price) + usdt_balance

        status = {
            'timestamp': datetime.now().isoformat(),
            'btc_balance': btc_balance,
            'usdt_balance': usdt_balance,
            'btc_price': price,
            'total_value_usdt': total_value_usdt,
            'balances': balances
        }

        return status

    def is_connected(self) -> bool:
        """
        Prüfe ob Client verbunden ist

        Returns:
            True wenn verbunden, False sonst
        """
        return self.client is not None


# ===================================================================
# ✅ CHECKPOINT 1 ABGESCHLOSSEN
# ===================================================================
# Funktionen implementiert:
# ✓ API-Verbindung zu Binance Testnet
# ✓ Verbindungstest mit Validierung
# ✓ Balance-Abfrage für BTC und USDT
# ✓ Preis-Abfrage mit 24h-Statistiken
# ✓ Rate-Limiting Management
# ✓ Fehlerbehandlung mit Retry-Logik
#
# Nächste Schritte (Phase 2):
# - Order-Placement implementieren
# - Modi-Logik (VERKAUFEN, KAUFEN, HOLD)
# - State-Management
# ===================================================================
