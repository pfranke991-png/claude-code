#!/usr/bin/env python3
"""
Bitcoin Trading Bot - Main Entry Point
=======================================
Einstiegspunkt für den Trading Bot

Phase 1: Verbindungstest und Grundfunktionen
Phase 2: Trading-Modi-Implementation
Phase 3: Backtesting und Optimierung
"""

import sys
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Füge src-Verzeichnis zum Python-Path hinzu
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from logger import create_logger
from bot_core import BinanceTradingBot


def load_config(config_path: str = "config/config.yaml") -> dict:
    """
    Lade Konfiguration aus YAML-Datei

    Args:
        config_path: Pfad zur Config-Datei

    Returns:
        Konfiguration als Dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"❌ Config-Datei nicht gefunden: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Fehler beim Parsen der Config-Datei: {e}")
        sys.exit(1)


def load_environment():
    """
    Lade Umgebungsvariablen aus .env Datei
    """
    env_path = Path(__file__).parent / '.env'

    if not env_path.exists():
        print("❌ .env Datei nicht gefunden!")
        print("📝 Bitte .env.example als .env kopieren und API-Keys eintragen:")
        print("   cp .env.example .env")
        sys.exit(1)

    load_dotenv(env_path)


def display_welcome():
    """
    Zeige Willkommens-Banner
    """
    print("\n" + "=" * 70)
    print("🤖 Bitcoin Trading Bot - Binance Testnet")
    print("=" * 70)
    print("Phase 1: Verbindungstest und Grundfunktionen")
    print("Testnet-Modus: Kein echtes Geld wird verwendet")
    print("=" * 70 + "\n")


def run_checkpoint_1_tests(bot: BinanceTradingBot, logger):
    """
    ✅ CHECKPOINT 1: Führe alle Basis-Tests durch

    Args:
        bot: BinanceTradingBot-Instanz
        logger: Logger-Instanz

    Returns:
        True wenn alle Tests erfolgreich, False sonst
    """
    logger.info("=" * 70)
    logger.info("CHECKPOINT 1: Starte Verbindungstests")
    logger.info("=" * 70)

    # Test 1: Verbindungstest
    logger.info("\n🔌 Test 1: Verbindung zu Binance Testnet...")
    test_results = bot.test_connection()

    if not test_results['connection']:
        logger.error("❌ Verbindung fehlgeschlagen!")
        logger.error(f"Fehler: {test_results['errors']}")
        return False

    logger.info("✅ Verbindung erfolgreich!")

    # Test 2: Balance-Abfrage
    logger.info("\n💰 Test 2: Kontostand abfragen...")
    balances = bot.get_balances()

    if not balances:
        logger.error("❌ Balance-Abfrage fehlgeschlagen!")
        return False

    logger.info("✅ Balance erfolgreich abgerufen:")
    logger.log_balance(
        btc_balance=balances['BTC']['total'],
        usdt_balance=balances['USDT']['total'],
        btc_price=bot.get_current_price()
    )

    # Test 3: Preis-Abfrage
    logger.info("\n📈 Test 3: Aktuellen BTC-Preis abfragen...")
    price = bot.get_current_price()

    if not price:
        logger.error("❌ Preis-Abfrage fehlgeschlagen!")
        return False

    logger.info(f"✅ Aktueller BTC-Preis: {price:.2f} USDT")

    # Test 4: 24h Statistiken
    logger.info("\n📊 Test 4: 24h-Statistiken abrufen...")
    stats = bot.get_24h_price_stats()

    if stats:
        logger.info(f"✅ 24h-Stats erfolgreich abgerufen:")
        logger.info(f"   High: {stats['high_24h']:.2f} USDT")
        logger.info(f"   Low: {stats['low_24h']:.2f} USDT")
        logger.info(f"   Change: {stats['price_change_percent_24h']:.2f}%")
    else:
        logger.warning("⚠️  24h-Stats konnten nicht abgerufen werden (nicht kritisch)")

    # Test 5: Account-Status
    logger.info("\n🔍 Test 5: Vollständiger Account-Status...")
    status = bot.get_account_status()

    if 'error' not in status:
        logger.info("✅ Account-Status erfolgreich abgerufen:")
        logger.info(f"   BTC Balance: {status['btc_balance']:.8f} BTC")
        logger.info(f"   USDT Balance: {status['usdt_balance']:.2f} USDT")
        logger.info(f"   Total Value: {status['total_value_usdt']:.2f} USDT")
    else:
        logger.error(f"❌ Account-Status-Fehler: {status['error']}")
        return False

    # Alle Tests bestanden
    logger.info("\n" + "=" * 70)
    logger.info("✅ CHECKPOINT 1 ABGESCHLOSSEN - Alle Tests erfolgreich!")
    logger.info("=" * 70)

    return True


def main():
    """
    Hauptfunktion - Einstiegspunkt des Programms
    """
    # Willkommens-Banner
    display_welcome()

    # Lade Umgebungsvariablen
    print("📂 Lade Umgebungsvariablen...")
    load_environment()

    # Lade Konfiguration
    print("⚙️  Lade Konfiguration...")
    config = load_config()

    # Initialisiere Logger
    print("📝 Initialisiere Logging-System...")
    logger = create_logger(config['logging'])

    # Log Startup mit Config-Summary
    config_summary = {
        'Trading Pair': config['trading']['symbol'],
        'Min Trade Interval': f"{config['trading']['min_trade_interval']}s",
        'Sell Threshold': f"{config['sell_mode']['threshold_percent']}%",
        'Buy Threshold': f"{config['buy_mode']['threshold_percent']}%",
        'Max API Calls/Min': config['safety']['max_api_calls_per_minute']
    }
    logger.log_startup(config_summary)

    # Hole API-Credentials aus Umgebungsvariablen
    api_key = os.getenv('BINANCE_TESTNET_API_KEY')
    api_secret = os.getenv('BINANCE_TESTNET_API_SECRET')

    if not api_key or not api_secret:
        logger.critical("❌ API-Keys nicht gefunden in .env Datei!")
        logger.critical("Bitte BINANCE_TESTNET_API_KEY und BINANCE_TESTNET_API_SECRET setzen")
        sys.exit(1)

    # Initialisiere Bot
    logger.info("🤖 Initialisiere Trading Bot...")
    bot = BinanceTradingBot(
        api_key=api_key,
        api_secret=api_secret,
        config=config,
        logger=logger
    )

    try:
        # ✅ CHECKPOINT 1: Führe alle Tests durch
        success = run_checkpoint_1_tests(bot, logger)

        if not success:
            logger.critical("❌ CHECKPOINT 1 fehlgeschlagen - Bot wird beendet")
            sys.exit(1)

        # Erfolgreicher Abschluss
        logger.info("\n🎉 Phase 1 erfolgreich abgeschlossen!")
        logger.info("📋 Nächste Schritte:")
        logger.info("   - Phase 2: Trading-Modi implementieren (VERKAUFEN, KAUFEN, HOLD)")
        logger.info("   - Phase 3: State-Management und Persistenz")
        logger.info("   - Phase 4: Backtesting und Optimierung")

    except KeyboardInterrupt:
        logger.log_shutdown("Benutzer-Abbruch (Ctrl+C)")
        print("\n👋 Bot gestoppt durch Benutzer")
        sys.exit(0)

    except Exception as e:
        logger.critical(f"Kritischer Fehler: {str(e)}", exc_info=True)
        logger.log_shutdown(f"Kritischer Fehler: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
