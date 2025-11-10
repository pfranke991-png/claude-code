"""
Bitcoin Trading Bot - Logging System
====================================
Umfassendes Logging-System mit Farbcodierung und automatischer Rotation
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
import colorlog


class TradingBotLogger:
    """
    Zentrales Logging-System für den Trading Bot

    Features:
    - Farbcodierte Konsolen-Ausgabe
    - Automatische Log-Rotation
    - Verschiedene Log-Level
    - Strukturiertes Format für Analyse
    """

    def __init__(self, config: dict):
        """
        Initialisiere das Logging-System

        Args:
            config: Logging-Konfiguration aus config.yaml
        """
        self.config = config
        self.logger = logging.getLogger('TradingBot')
        self.logger.setLevel(self._get_log_level(config.get('level', 'INFO')))

        # Verhindere doppelte Handler bei Reinitialisierung
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Setup Handler
        self._setup_file_handler()
        if config.get('console_output', True):
            self._setup_console_handler()

    def _get_log_level(self, level_str: str) -> int:
        """
        Konvertiere String-Level zu logging-Konstante

        Args:
            level_str: Level als String (DEBUG, INFO, etc.)

        Returns:
            logging Level-Konstante
        """
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return levels.get(level_str.upper(), logging.INFO)

    def _setup_file_handler(self):
        """
        Richte Datei-Handler mit automatischer Rotation ein
        """
        # ✅ CHECKPOINT: Stelle sicher, dass Log-Verzeichnis existiert
        log_file = Path(self.config.get('file_path', 'logs/trading_bot.log'))
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Maximale Größe in Bytes
        max_bytes = self.config.get('max_file_size_mb', 10) * 1024 * 1024
        backup_count = self.config.get('backup_count', 5)

        # Rotating File Handler
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )

        # Detailliertes Format für Datei
        file_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def _setup_console_handler(self):
        """
        Richte farbcodierten Konsolen-Handler ein
        """
        console_handler = logging.StreamHandler(sys.stdout)

        if self.config.get('colored_output', True):
            # Farbcodierung für bessere Lesbarkeit
            color_formatter = colorlog.ColoredFormatter(
                fmt='%(log_color)s%(asctime)s | %(levelname)-8s | %(message)s%(reset)s',
                datefmt='%H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            console_handler.setFormatter(color_formatter)
        else:
            # Einfaches Format ohne Farben
            plain_formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(plain_formatter)

        self.logger.addHandler(console_handler)

    # ===================================================================
    # Convenience-Methoden für verschiedene Log-Arten
    # ===================================================================

    def debug(self, message: str):
        """Debug-Level Nachricht (nur bei DEBUG-Level sichtbar)"""
        self.logger.debug(message)

    def info(self, message: str):
        """Info-Level Nachricht (normale Operationen)"""
        self.logger.info(message)

    def warning(self, message: str):
        """Warning-Level Nachricht (potenzielle Probleme)"""
        self.logger.warning(message)

    def error(self, message: str, exc_info=False):
        """
        Error-Level Nachricht (Fehler, die behoben werden können)

        Args:
            message: Fehlermeldung
            exc_info: Wenn True, füge Stack-Trace hinzu
        """
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message: str, exc_info=False):
        """
        Critical-Level Nachricht (schwerwiegende Fehler)

        Args:
            message: Kritische Meldung
            exc_info: Wenn True, füge Stack-Trace hinzu
        """
        self.logger.critical(message, exc_info=exc_info)

    # ===================================================================
    # Spezielle Methoden für Trading-Events
    # ===================================================================

    def log_trade(self, action: str, amount: float, price: float, total: float):
        """
        Logge einen Trade mit strukturierten Daten

        Args:
            action: 'BUY' oder 'SELL'
            amount: Menge (BTC)
            price: Preis (USDT)
            total: Gesamtwert (USDT)
        """
        self.logger.info(
            f"TRADE | {action:4s} | Amount: {amount:.8f} BTC | "
            f"Price: {price:.2f} USDT | Total: {total:.2f} USDT"
        )

    def log_balance(self, btc_balance: float, usdt_balance: float, btc_price: float):
        """
        Logge aktuellen Kontostand

        Args:
            btc_balance: BTC-Guthaben
            usdt_balance: USDT-Guthaben
            btc_price: Aktueller BTC-Preis
        """
        total_value = (btc_balance * btc_price) + usdt_balance
        self.logger.info(
            f"BALANCE | BTC: {btc_balance:.8f} | USDT: {usdt_balance:.2f} | "
            f"Total: {total_value:.2f} USDT @ {btc_price:.2f}"
        )

    def log_mode_switch(self, old_mode: str, new_mode: str, reason: str = ""):
        """
        Logge Moduswechsel

        Args:
            old_mode: Alter Modus
            new_mode: Neuer Modus
            reason: Grund für Wechsel (optional)
        """
        message = f"MODE SWITCH | {old_mode} → {new_mode}"
        if reason:
            message += f" | Reason: {reason}"
        self.logger.warning(message)

    def log_api_error(self, endpoint: str, error: Exception, retry_count: int = 0):
        """
        Logge API-Fehler mit Details

        Args:
            endpoint: API-Endpunkt
            error: Exception-Objekt
            retry_count: Anzahl bisheriger Retries
        """
        self.logger.error(
            f"API ERROR | Endpoint: {endpoint} | "
            f"Error: {type(error).__name__}: {str(error)} | "
            f"Retry: {retry_count}",
            exc_info=True
        )

    def log_startup(self, config_summary: dict):
        """
        Logge Bot-Start mit Konfigurationsübersicht

        Args:
            config_summary: Dictionary mit wichtigen Config-Werten
        """
        self.logger.info("=" * 70)
        self.logger.info("Bitcoin Trading Bot - Starting Up")
        self.logger.info("=" * 70)
        for key, value in config_summary.items():
            self.logger.info(f"Config | {key}: {value}")
        self.logger.info("=" * 70)

    def log_shutdown(self, reason: str = "Normal shutdown"):
        """
        Logge Bot-Shutdown

        Args:
            reason: Grund für Shutdown
        """
        self.logger.info("=" * 70)
        self.logger.info(f"Bitcoin Trading Bot - Shutting Down | Reason: {reason}")
        self.logger.info("=" * 70)


# ===================================================================
# Convenience-Funktion für schnelle Logger-Erstellung
# ===================================================================

def create_logger(config: dict) -> TradingBotLogger:
    """
    Factory-Funktion zum Erstellen eines konfigurierten Loggers

    Args:
        config: Logging-Konfiguration

    Returns:
        Konfigurierter TradingBotLogger
    """
    return TradingBotLogger(config)
