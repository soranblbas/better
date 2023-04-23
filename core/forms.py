from django import forms
from .models import *


class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ('item', 'qty', 'is_returned')
        widgets = {
            'is_returned': forms.RadioSelect(choices=((False, 'No'), (True, 'Yes')))
        }
