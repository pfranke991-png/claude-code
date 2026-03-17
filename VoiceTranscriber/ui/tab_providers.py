"""Tab 2 - API & Provider: Setup with dynamic model lists, prompt field."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QLineEdit, QTextEdit, QListWidget, QListWidgetItem,
    QGroupBox, QFormLayout, QMessageBox, QStackedWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.postprocessor import PROVIDER_CONFIGS, DEFAULT_PROMPT
from ui.theme import NEON_GREEN, TEXT_SECONDARY


class ProviderTab(QWidget):
    """Provider configuration interface."""

    provider_changed = pyqtSignal()

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self._setup_ui()
        self._load_providers()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # -- Left: Provider list --
        left = QVBoxLayout()
        left_title = QLabel("Provider")
        left_title.setObjectName("sectionTitle")
        left.addWidget(left_title)

        self.provider_list = QListWidget()
        self.provider_list.setFixedWidth(220)
        self.provider_list.currentRowChanged.connect(self._on_provider_selected)
        left.addWidget(self.provider_list)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("+")
        self.add_btn.setObjectName("addProviderBtn")
        self.add_btn.setFixedSize(50, 50)
        self.add_btn.clicked.connect(self._add_provider)
        btn_row.addWidget(self.add_btn)

        self.del_btn = QPushButton("Entfernen")
        self.del_btn.clicked.connect(self._delete_provider)
        btn_row.addWidget(self.del_btn)
        btn_row.addStretch()
        left.addLayout(btn_row)

        layout.addLayout(left)

        # -- Right: Config panel --
        self.stack = QStackedWidget()

        # Empty state
        empty = QWidget()
        empty_layout = QVBoxLayout(empty)
        empty_layout.addStretch()
        empty_label = QLabel("Klicke '+' um einen Provider hinzuzufuegen")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 16px;")
        empty_layout.addWidget(empty_label)

        add_big = QPushButton("+")
        add_big.setObjectName("addProviderBtn")
        add_big.setFixedSize(100, 100)
        add_big.clicked.connect(self._add_provider)
        empty_layout.addWidget(add_big, alignment=Qt.AlignmentFlag.AlignCenter)
        empty_layout.addStretch()
        self.stack.addWidget(empty)

        # Config form
        config = QWidget()
        config_layout = QVBoxLayout(config)

        self.config_title = QLabel("Provider konfigurieren")
        self.config_title.setObjectName("sectionTitle")
        config_layout.addWidget(self.config_title)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("z.B. Mein OpenAI")
        form.addRow("Name:", self.name_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItems(list(PROVIDER_CONFIGS.keys()))
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        form.addRow("Provider:", self.type_combo)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://api.openai.com/v1")
        form.addRow("Base URL:", self.url_edit)

        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("sk-...")
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("API Key:", self.key_edit)

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        form.addRow("Modell:", self.model_combo)

        config_layout.addLayout(form)

        # Prompt
        prompt_label = QLabel("System-Prompt:")
        prompt_label.setObjectName("sectionTitle")
        config_layout.addWidget(prompt_label)

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Prompt fuer Post-Processing...")
        self.prompt_edit.setMaximumHeight(120)
        self.prompt_edit.setPlainText(DEFAULT_PROMPT)
        config_layout.addWidget(self.prompt_edit)

        # Action buttons
        action_row = QHBoxLayout()

        self.test_btn = QPushButton("Verbindung testen")
        self.test_btn.clicked.connect(self._test_connection)
        action_row.addWidget(self.test_btn)

        self.save_btn = QPushButton("Speichern")
        self.save_btn.setStyleSheet(f"background-color: {NEON_GREEN}; color: #1a1a1a; font-weight: bold;")
        self.save_btn.clicked.connect(self._save_provider)
        action_row.addWidget(self.save_btn)

        self.activate_btn = QPushButton("Aktivieren")
        self.activate_btn.clicked.connect(self._activate_provider)
        action_row.addWidget(self.activate_btn)

        action_row.addStretch()
        config_layout.addLayout(action_row)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        config_layout.addWidget(self.status_label)

        config_layout.addStretch()
        self.stack.addWidget(config)

        layout.addWidget(self.stack, 1)

    def _on_type_changed(self, provider_type):
        config = PROVIDER_CONFIGS.get(provider_type, {})
        self.url_edit.setText(config.get("base_url", ""))
        self.model_combo.clear()
        self.model_combo.addItems(config.get("models", []))

    def _add_provider(self):
        self.stack.setCurrentIndex(1)
        self.name_edit.clear()
        self.key_edit.clear()
        self.type_combo.setCurrentIndex(0)
        self._on_type_changed(self.type_combo.currentText())
        self.prompt_edit.setPlainText(DEFAULT_PROMPT)
        self.status_label.clear()
        self._current_id = None

    def _save_provider(self):
        name = self.name_edit.text().strip()
        if not name:
            name = self.type_combo.currentText()

        ptype = self.type_combo.currentText()
        key = self.key_edit.text().strip()
        url = self.url_edit.text().strip()
        model = self.model_combo.currentText().strip()
        prompt = self.prompt_edit.toPlainText().strip()

        if hasattr(self, "_current_id") and self._current_id:
            self.db.update_provider(
                self._current_id,
                name=name, provider_type=ptype, api_key=key,
                base_url=url, model=model, prompt=prompt,
            )
        else:
            self.db.save_provider(name, ptype, key, url, model, prompt)

        self.status_label.setText("Gespeichert!")
        self.status_label.setStyleSheet(f"color: {NEON_GREEN}; font-size: 12px;")
        self._load_providers()
        self.provider_changed.emit()

    def _delete_provider(self):
        row = self.provider_list.currentRow()
        if row < 0:
            return
        providers = self.db.get_providers()
        if row < len(providers):
            self.db.delete_provider(providers[row]["id"])
            self._load_providers()
            self.stack.setCurrentIndex(0)
            self.provider_changed.emit()

    def _activate_provider(self):
        if hasattr(self, "_current_id") and self._current_id:
            self.db.set_active_provider(self._current_id)
            self.status_label.setText("Provider aktiviert!")
            self.status_label.setStyleSheet(f"color: {NEON_GREEN}; font-size: 12px;")
            self._load_providers()
            self.provider_changed.emit()

    def _load_providers(self):
        self.provider_list.clear()
        providers = self.db.get_providers()
        for p in providers:
            prefix = "* " if p.get("is_active") else "  "
            item = QListWidgetItem(f"{prefix}{p['name']} ({p['provider_type']})")
            item.setData(Qt.ItemDataRole.UserRole, p["id"])
            self.provider_list.addItem(item)

        if not providers:
            self.stack.setCurrentIndex(0)

    def _on_provider_selected(self, row):
        if row < 0:
            return
        providers = self.db.get_providers()
        if row >= len(providers):
            return
        p = providers[row]
        self._current_id = p["id"]
        self.stack.setCurrentIndex(1)
        self.name_edit.setText(p["name"])
        idx = self.type_combo.findText(p["provider_type"])
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        self.url_edit.setText(p.get("base_url", ""))
        self.key_edit.setText(p.get("api_key", ""))
        self.model_combo.setCurrentText(p.get("model", ""))
        self.prompt_edit.setPlainText(p.get("prompt", DEFAULT_PROMPT))
        self.status_label.clear()
        if p.get("is_active"):
            self.config_title.setText(f"Provider: {p['name']} (AKTIV)")
        else:
            self.config_title.setText(f"Provider: {p['name']}")

    def _test_connection(self):
        from core.postprocessor import PostProcessor
        pp = PostProcessor()
        try:
            pp.configure(
                self.type_combo.currentText(),
                self.key_edit.text().strip(),
                self.url_edit.text().strip(),
                self.model_combo.currentText().strip(),
            )
            ok, msg = pp.test_connection()
            if ok:
                self.status_label.setText(f"OK: {msg}")
                self.status_label.setStyleSheet(f"color: {NEON_GREEN}; font-size: 12px;")
            else:
                self.status_label.setText(f"Fehler: {msg}")
                self.status_label.setStyleSheet("color: #ff4444; font-size: 12px;")
        except Exception as e:
            self.status_label.setText(f"Fehler: {e}")
            self.status_label.setStyleSheet("color: #ff4444; font-size: 12px;")
