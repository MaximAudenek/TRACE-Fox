"""Edit a private palette. Changes are committed only when accepted."""

from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (QColorDialog, QComboBox, QDialog, QDialogButtonBox,
                               QFormLayout, QMessageBox, QPushButton)

from trace_app.infra import config_store, custom_colors


class CustomThemeDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Custom Theme")
        base, saved = custom_colors.read()
        self.palettes = {name: colors.copy() for name, colors in custom_colors.DEFAULTS.items()}
        self.palettes[base] = saved
        form = QFormLayout(self)
        self.base = QComboBox()
        self.base.addItems(['light', 'dark'])
        self.base.setCurrentText(base)
        form.addRow("Base theme", self.base)
        self.buttons = {}
        for key in saved:
            button = QPushButton()
            self.buttons[key] = button
            button.clicked.connect(lambda checked=False, role=key: self.pick(role))
            form.addRow(key.replace('_', ' ').title(), button)
        self.base.currentTextChanged.connect(self.refresh)
        self.refresh()
        actions = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        actions.accepted.connect(self.save)
        actions.rejected.connect(self.reject)
        form.addRow(actions)

    def refresh(self):
        colors = self.palettes[self.base.currentText()]
        for key, button in self.buttons.items():
            value = colors[key]
            button.setText(value.upper())
            swatch = QColor(value)
            chip = QPixmap(20, 16)
            chip.fill(swatch)
            button.setIcon(QIcon(chip))

    def pick(self, key):
        colors = self.palettes[self.base.currentText()]
        value = QColorDialog.getColor(QColor(colors[key]), self, "Choose colour")
        if value.isValid():
            colors[key] = value.name()
            self.refresh()

    def save(self):
        base = self.base.currentText()
        if config_store.set_values(custom_colors.SECTION, dict(base=base, **self.palettes[base])):
            self.accept()
        else:
            QMessageBox.warning(self, "Custom Theme", "Could not save the theme settings.")
