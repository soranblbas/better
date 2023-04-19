import django_filters
from django_filters import DateFilter
from .models import *


class Sales_Filter(django_filters.FilterSet):
    max_date = DateFilter(field_name='sale_date', lookup_expr='gte')
    min_date = DateFilter(field_name='sale_date', lookup_expr='lte')

    class Meta:
        model = SaleItem
        fields = ['min_date', 'max_date']
        exclude = ['sale_date', ]


class Purchase_Filter(django_filters.FilterSet):
    max_date = DateFilter(field_name='pur_date', lookup_expr='gte')
    min_date = DateFilter(field_name='pur_date', lookup_expr='lte')

    class Meta:
        model = SaleItem
        fields = ['min_date', 'max_date']
        exclude = ['pur_date', ]


class Payment_Filter(django_filters.FilterSet):
    max_date = DateFilter(field_name='payment_date', lookup_expr='gte')
    min_date = DateFilter(field_name='payment_date', lookup_expr='lte')

    class Meta:
        model = Payment_Entry
        fields = ['min_date', 'max_date']
        exclude = ['payment_date', ]
