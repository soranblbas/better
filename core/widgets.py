# widgets.py

from django import forms


class PercentageInput(forms.TextInput):
    def format_value(self, value):
        if value is None:
            return ''
        return f'{value * 100:.2f}%'
