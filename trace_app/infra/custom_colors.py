"""Editable colours for the custom theme, based on TRACE's stock sheets."""

import re

from trace_app.infra import config_store

SECTION = 'Custom theme'
DEFAULTS = {
    'light': dict(background='#FFFFFF', text='#333333', border='#CED4DA',
                  selection='#CCE8FF', selected_text='#212529', link='#1A73E8'),
    'dark': dict(background='#2E2E2E', text='#E0E0E0', border='#5A5A5A',
                 selection='#505050', selected_text='#E0E0E0', link='#6CB4FF'),
}
HEX = re.compile(r'#[0-9a-fA-F]{6}\Z')


def read():
    section = config_store.load()
    base = section.get(SECTION, 'base', fallback='dark')
    if base not in DEFAULTS:
        base = 'dark'
    colors = DEFAULTS[base].copy()
    for key, default in colors.items():
        value = section.get(SECTION, key, fallback=default)
        if HEX.fullmatch(value):
            colors[key] = value
    return base, colors


def recolor(sheet, base, colors):
    """Replace UI role declarations only, leaving evidence status colours intact."""
    defaults = DEFAULTS[base]
    backgrounds = {'#FFFFFF', '#F8F9FA'} if base == 'light' else {'#2E2E2E', '#3C3C3C'}
    foregrounds = {defaults['text'], '#202124', '#212529'}
    def declaration(match):
        prop, value, literal = match.groups()
        old = literal.upper()
        role = None
        if prop == 'selection-color':
            role = 'selected_text'
        elif prop == 'selection-background-color':
            role = 'selection'
        elif prop == 'background-color' and old == defaults['selection']:
            role = 'selection'
        elif prop == 'background-color' and old in backgrounds:
            role = 'background'
        elif prop == 'color' and old in foregrounds:
            role = 'text'
        elif prop == 'color' and old == defaults['link']:
            role = 'link'
        elif prop.startswith('border') and old == defaults['border']:
            role = 'border'
        return prop + value + colors[role] if role else match.group()

    sheet = re.sub(r'(?<![\w-])(selection-background-color|selection-color|background-color|color|border(?:-[a-z]+)?)'
                   r'(\s*:\s*[^#;{}\n]*)(#[\da-fA-F]{6})\b', declaration, sheet)
    return sheet + """
QAbstractItemView::item:selected, QComboBox QAbstractItemView::item:selected {
    background-color: %s; color: %s;
}
""" % (colors['selection'], colors['selected_text'])
