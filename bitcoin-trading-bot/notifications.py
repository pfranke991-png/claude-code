"""
Benachrichtigungs-System für Bitcoin Trading Bot
Telegram, Email, und mehr

PRODUCTION-READY für echte Alerts!
"""

import logging
from typing import Optional, Dict, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Telegram Benachrichtigungen

    Setup:
    1. Erstelle Bot über @BotFather
    2. Hole Bot Token
    3. Starte Chat mit Bot und sende /start
    4. Hole Chat ID über https://api.telegram.org/bot<TOKEN>/getUpdates
    """

    def __init__(self, bot_token: str, chat_id: str):
        """
        Args:
            bot_token: Telegram Bot Token
            chat_id: Telegram Chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
        self.bot = None

        if not self.enabled:
            logger.warning("Telegram nicht konfiguriert - Benachrichtigungen deaktiviert")
            return

        try:
            from telegram import Bot
            self.bot = Bot(token=self.bot_token)
            logger.info("✓ Telegram Bot initialisiert")

        except ImportError:
            logger.warning("python-telegram-bot nicht installiert")
            logger.warning("Für Telegram: pip install python-telegram-bot")
            self.enabled = False

        except Exception as e:
            logger.error(f"Fehler bei Telegram-Initialisierung: {e}")
            self.enabled = False

    def send_message(self, message: str, parse_mode: str = 'Markdown') -> bool:
        """
        Sende Telegram Nachricht

        Args:
            message: Nachricht (unterstützt Markdown)
            parse_mode: 'Markdown' oder 'HTML'

        Returns:
            True wenn erfolgreich
        """
        if not self.enabled:
            logger.debug(f"[Telegram deaktiviert] {message}")
            return False

        try:
            import asyncio

            async def send():
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=parse_mode
                )

            asyncio.run(send())
            logger.debug("Telegram Nachricht gesendet")
            return True

        except Exception as e:
            logger.error(f"Fehler beim Senden der Telegram-Nachricht: {e}")
            return False

    def notify_trade_executed(self, trade_info: Dict) -> bool:
        """Benachrichtige über ausgeführten Trade"""
        message = f"""
🤖 *Bitcoin Trading Bot*

✅ *VERKAUF AUSGEFÜHRT*

💰 *Betrag:* {trade_info['eur_amount']:.2f} EUR
₿ *BTC:* {trade_info['btc_amount']:.8f}
📊 *Preis:* {trade_info['price']:.2f} EUR/BTC
⏰ *Zeit:* {trade_info['timestamp'].strftime('%d.%m.%Y %H:%M')}

{trade_info.get('reason', '')}
"""
        return self.send_message(message)

    def notify_signal_detected(self, price: float, reason: str) -> bool:
        """Benachrichtige über erkanntes Verkaufssignal"""
        message = f"""
🔔 *Verkaufssignal erkannt*

📊 Preis: {price:.2f} EUR/BTC
💡 Grund: {reason}
"""
        return self.send_message(message)

    def notify_error(self, error: str) -> bool:
        """Benachrichtige über Fehler"""
        message = f"""
⚠️ *FEHLER*

{error}
"""
        return self.send_message(message)

    def notify_weekly_summary(self, summary: Dict) -> bool:
        """Sende wöchentliche Zusammenfassung"""
        message = f"""
📊 *Wochenzusammenfassung*

🎯 Ziel: {summary['target']:.2f} EUR
✅ Verkauft: {summary['sold']:.2f} EUR ({summary['completion_percent']:.1f}%)
📈 Trades: {summary['trades_count']}

Woche vom {summary['week_start'].strftime('%d.%m.%Y')}
"""
        return self.send_message(message)

    def notify_bot_started(self) -> bool:
        """Benachrichtige über Bot-Start"""
        message = """
🚀 *Bitcoin Trading Bot gestartet*

Der Bot überwacht jetzt 24/7 den Bitcoin-Preis
und führt automatisch Verkäufe bei günstigen
Gelegenheiten aus.
"""
        return self.send_message(message)

    def notify_bot_stopped(self, summary: Dict) -> bool:
        """Benachrichtige über Bot-Stop"""
        message = f"""
🛑 *Bitcoin Trading Bot gestoppt*

Trades diese Woche: {summary['trades_count']}
Verkauft: {summary['sold']:.2f} EUR
"""
        return self.send_message(message)


class EmailNotifier:
    """
    Email Benachrichtigungen via SendGrid

    Setup:
    1. Erstelle SendGrid Account
    2. Erstelle API Key
    3. Verifiziere Sender Email
    """

    def __init__(self, api_key: str, from_email: str, to_email: str):
        """
        Args:
            api_key: SendGrid API Key
            from_email: Absender Email (muss verifiziert sein)
            to_email: Empfänger Email
        """
        self.api_key = api_key
        self.from_email = from_email
        self.to_email = to_email
        self.enabled = bool(api_key and from_email and to_email)

        if not self.enabled:
            logger.warning("Email nicht konfiguriert - Email-Benachrichtigungen deaktiviert")
            return

        try:
            from sendgrid import SendGridAPIClient
            self.sg = SendGridAPIClient(api_key)
            logger.info("✓ SendGrid initialisiert")

        except ImportError:
            logger.warning("sendgrid nicht installiert")
            logger.warning("Für Email: pip install sendgrid")
            self.enabled = False

        except Exception as e:
            logger.error(f"Fehler bei SendGrid-Initialisierung: {e}")
            self.enabled = False

    def send_email(self, subject: str, html_content: str) -> bool:
        """
        Sende Email

        Args:
            subject: Email Subject
            html_content: HTML Content

        Returns:
            True wenn erfolgreich
        """
        if not self.enabled:
            logger.debug(f"[Email deaktiviert] {subject}")
            return False

        try:
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=self.from_email,
                to_emails=self.to_email,
                subject=subject,
                html_content=html_content
            )

            response = self.sg.send(message)
            logger.debug(f"Email gesendet: {response.status_code}")
            return True

        except Exception as e:
            logger.error(f"Fehler beim Senden der Email: {e}")
            return False

    def notify_trade_executed(self, trade_info: Dict) -> bool:
        """Benachrichtige über Trade"""
        subject = f"Bitcoin Trade ausgeführt: {trade_info['eur_amount']:.2f} EUR"

        html = f"""
        <h2>Bitcoin Trading Bot</h2>
        <h3>✅ Verkauf ausgeführt</h3>

        <table>
            <tr><td><strong>Betrag:</strong></td><td>{trade_info['eur_amount']:.2f} EUR</td></tr>
            <tr><td><strong>BTC:</strong></td><td>{trade_info['btc_amount']:.8f}</td></tr>
            <tr><td><strong>Preis:</strong></td><td>{trade_info['price']:.2f} EUR/BTC</td></tr>
            <tr><td><strong>Zeit:</strong></td><td>{trade_info['timestamp']}</td></tr>
        </table>

        <p>{trade_info.get('reason', '')}</p>
        """

        return self.send_email(subject, html)


class NotificationManager:
    """
    Zentraler Notification Manager

    Verwaltet alle Benachrichtigungs-Kanäle
    """

    def __init__(self):
        self.notifiers: List = []
        logger.info("Notification Manager initialisiert")

    def add_telegram(self, bot_token: str, chat_id: str):
        """Füge Telegram hinzu"""
        notifier = TelegramNotifier(bot_token, chat_id)
        if notifier.enabled:
            self.notifiers.append(notifier)
            logger.info("✓ Telegram Benachrichtigungen aktiviert")

    def add_email(self, api_key: str, from_email: str, to_email: str):
        """Füge Email hinzu"""
        notifier = EmailNotifier(api_key, from_email, to_email)
        if notifier.enabled:
            self.notifiers.append(notifier)
            logger.info("✓ Email Benachrichtigungen aktiviert")

    def notify_all(self, method_name: str, *args, **kwargs):
        """Sende Benachrichtigung an alle Kanäle"""
        for notifier in self.notifiers:
            try:
                method = getattr(notifier, method_name)
                method(*args, **kwargs)
            except Exception as e:
                logger.error(f"Fehler bei Benachrichtigung: {e}")

    def notify_trade_executed(self, trade_info: Dict):
        """Benachrichtige über Trade"""
        self.notify_all('notify_trade_executed', trade_info)

    def notify_signal_detected(self, price: float, reason: str):
        """Benachrichtige über Signal"""
        self.notify_all('notify_signal_detected', price, reason)

    def notify_error(self, error: str):
        """Benachrichtige über Fehler"""
        self.notify_all('notify_error', error)

    def notify_weekly_summary(self, summary: Dict):
        """Sende wöchentliche Zusammenfassung"""
        self.notify_all('notify_weekly_summary', summary)

    def notify_bot_started(self):
        """Benachrichtige über Bot-Start"""
        self.notify_all('notify_bot_started')

    def notify_bot_stopped(self, summary: Dict):
        """Benachrichtige über Bot-Stop"""
        self.notify_all('notify_bot_stopped', summary)


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("NOTIFICATION SYSTEM TEST")
    print("=" * 60)

    # Test ohne echte Credentials (Simulation)
    manager = NotificationManager()

    # Würde Telegram hinzufügen (wenn konfiguriert)
    manager.add_telegram('', '')

    # Test Trade Notification
    trade = {
        'eur_amount': 14.29,
        'btc_amount': 0.00029,
        'price': 49234.50,
        'timestamp': datetime.now(),
        'reason': 'RSI überkauft, Preis über MA'
    }

    manager.notify_trade_executed(trade)
    print("\n✓ Test abgeschlossen (Simulation Mode)")
