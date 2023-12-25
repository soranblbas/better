# from importlib.resources import _
from django.db.models import Q
from django.utils.translation import gettext as _

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import *
from django import forms


# Register your models here.
# class SaleItemInlineForm(forms.ModelForm):
#     manual_item_input = forms.CharField(max_length=255, required=False, label='Enter Item Details')
#
#     class Meta:
#         model = SaleItem
#         fields = '__all__'
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['item'].queryset = Item.objects.exclude(price_list='شراء')


class SalesItem(admin.TabularInline):
    # form = SaleItemInlineForm
    model = SaleItem
    extra = 1
    template = "admin/common_item_inline.html"  # Path to your common template

    autocomplete_fields = ['item']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "item":
            kwargs["queryset"] = Item.objects.exclude(price_list='شراء')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    readonly_fields = ('sub_total',)


@admin.register(SaleInvoice)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [SalesItem]

    class Meta:
        model = SaleInvoice

    # def show_sales_total(self, obj):
    #     total_sales = sum(sale.total_amt for sale in obj.sales.all())
    #     return format_html('<b>{}</b>', total_sales)

    list_display = (
        'invoice_number', 'customer_name', 'total_sub_amount', 'total_discount_amount', 'total_sales_amount', 'date',
        'updated_at',)
    list_filter = ('status',)



    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.method == 'POST':
            try:
                return super().changeform_view(request, object_id=object_id, form_url=form_url,
                                               extra_context=extra_context)
            except ValueError as error:
                self.message_user(request, _(str(error)), level='ERROR')
                url = reverse('admin:%s_%s_change' % (self.opts.app_label, self.opts.model_name), args=[object_id])
                return HttpResponseRedirect(url)
        else:
            return super().changeform_view(request, object_id=object_id, form_url=form_url, extra_context=extra_context)

class PurchasesItem(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    template = "admin/common_item_inline.html"  # Path to your common template

    autocomplete_fields = ['item']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "item":
            kwargs["queryset"] = Item.objects.exclude(price_list__in=['مفرد', 'قسط', 'جملة'])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    #

@admin.register(Purchase)
class ProfileAdmin(admin.ModelAdmin):
    inlines = [PurchasesItem]

    class Meta:
        model = Purchase

    list_display = ('invoice_number', 'vendor', 'total_purchase_amount', 'date')


@admin.register(Item)
class CustomerPagination(admin.ModelAdmin):
    list_display = ('item_code', 'name', 'price_list', 'price')
    list_filter = ("price_list",)
    # list_display_links = ('client_name',)
    list_per_page = 100
    search_fields = ['item_code', ]  # Define the search fields for the autocomplete functionality


# @admin.register(Purchase)
# class CustomerPagination(admin.ModelAdmin):
#     list_display = ('item', 'vendor', 'qty', 'price', 'total_amt', 'pur_date')
#     # list_filter = ("client_name", "status", "date_created")
#     # list_display_links = ('client_name',)
#     # list_per_page = 20
#     readonly_fields = ['total_amt', ]


# @admin.register(PurchaseItem)
# class CustomerPagination(admin.ModelAdmin):
#     list_display = ('item', 'qty', 'total_amt', 'pur_date')
#
#     readonly_fields = ['total_amt', ]

#
# @admin.register(SaleItem)
# class CustomerPagination(admin.ModelAdmin):
#     list_display = ('item', 'qty', 'total_amt', 'sale_date')
#
#     readonly_fields = ('total_amt',)


@admin.register(Inventory)
class CustomerPagination(admin.ModelAdmin):
    list_display = ('item','warehouse', 'purchase', 'sale', 'pur_qty', 'sale_qty', 'return_qty', 'total_bal_qty')
    list_display_links = ['purchase', 'sale', ]
    search_fields = ['item__item_code', 'item__name', 'warehouse__name']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        search_terms = search_term.split(';')

        if len(search_terms) > 1:
            query = Q()
            for term in search_terms:
                query |= Q(item__item_code__icontains=term.strip()) | Q(item__name__icontains=term.strip()) | Q(
                    warehouse__name__icontains=term.strip())

            queryset = queryset.filter(query)

        return queryset, use_distinct


@admin.register(Salary)
class CustomerPagination(admin.ModelAdmin):
    list_display = (
        'employee', 'amount', 'slfa', 'fines', 'absent_days', 'amount_deducted_per_day', 'date', 'final_amount')
    list_display_links = ['employee', ]
    list_filter = ('employee',)


@admin.register(Employee)
class CustomerPagination(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'birthdate', 'phone_number', 'relative_phone_number', 'hire_date', 'job_title',
        'department',)
    list_display_links = ['first_name', ]
    list_filter = ('department', 'job_title',)


@admin.register(Payment_Entry)
class CustomerPagination(admin.ModelAdmin):
    list_display = ('sales_invoice', 'paid_amount', 'q_type', 'payment_date', 'note','discount_amount')
    list_display_links = ['sales_invoice', ]
    list_filter = ('sales_invoice',)


@admin.register(Customer)
class CustomerPagination(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_mobile', 'customer_address', 'city',)
    list_display_links = ['customer_name', ]
    list_filter = ('city',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status')
    list_filter = ('date', 'status')
    search_fields = ('employee__first_name', 'employee__last_name')


admin.site.register(Vendor)
admin.site.register(Unit)
admin.site.register(Warehouse)


admin.site.register(JournalEntry)
admin.site.register(OpeningBalance)


admin.site.site_header = "Better Cooking Admin"
admin.site.site_title = "Better Cooking Admin Portal"
admin.site.index_title = "Welcome to Better Cooking Retailer Portal"
