from PySide6.QtGui import QColor

from trace_app.infra import config_store, custom_colors, theme
from trace_app.ui.dialogs.custom_theme import CustomThemeDialog


def test_custom_theme_round_trip(qapp, monkeypatch, tmp_path):
    monkeypatch.setattr(config_store, 'config_file', lambda: str(tmp_path / 'config.ini'))
    dialog = CustomThemeDialog(None)
    dialog.base.setCurrentText('light')
    monkeypatch.setattr('trace_app.ui.dialogs.custom_theme.QColorDialog.getColor',
                        lambda *args: QColor('#fce8d0'))
    dialog.buttons['background'].click()
    dialog.save()
    theme.apply_theme(qapp, theme.CUSTOM, remember=True)
    assert theme.read_choice() == theme.CUSTOM
    assert theme.read_theme() == 'light'
    assert 'background-color: #fce8d0' in qapp.styleSheet()
    theme.apply_theme(qapp, 'dark', remember=True)
    assert '#fce8d0' not in qapp.styleSheet()
    theme.save_theme(theme.CUSTOM)
    assert theme.apply_theme(qapp) == 'light'
    assert '#fce8d0' in qapp.styleSheet()
    reopened = CustomThemeDialog(None)
    assert reopened.buttons['background'].text() == '#FCE8D0'
    reopened.base.setCurrentText('dark')
    reopened.buttons['text'].click()
    reopened.reject()
    assert custom_colors.read()[0] == 'light'
    theme.apply_theme(qapp, 'light')


def test_invalid_colors_fall_back(monkeypatch, tmp_path):
    monkeypatch.setattr(config_store, 'config_file', lambda: str(tmp_path / 'config.ini'))
    config_store.set_values(custom_colors.SECTION, {'base': '../missing', 'text': 'broken'})
    assert custom_colors.read() == ('dark', custom_colors.DEFAULTS['dark'])


def test_view_menu_applies_and_restores_palette(qapp, monkeypatch, tmp_path):
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QAction, QPalette
    from tests.conftest import close_window
    from trace_app.ui.main_window import MainWindow

    monkeypatch.setattr(config_store, 'config_file', lambda: str(tmp_path / 'config.ini'))
    window = MainWindow()
    actions = {item.text(): item for item in window.findChildren(QAction)}

    def choose():
        editor = qapp.activeModalWidget()
        editor.base.setCurrentText('dark')
        editor.palettes['dark']['selection'] = '#776655'
        editor.save()

    try:
        QTimer.singleShot(0, choose)
        actions['Edit Custom Theme…'].trigger()
        assert actions['Custom Theme'].isChecked()
        assert theme.read_choice() == theme.CUSTOM
        assert qapp.palette().color(QPalette.Highlight).name() == '#776655'
        actions['Light Mode'].trigger()
        assert theme.read_choice() == 'light'
        actions['Custom Theme'].trigger()
        assert '#776655' in qapp.styleSheet()
    finally:
        actions['Light Mode'].trigger()
        close_window(window)
