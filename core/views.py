from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect
from django.contrib import messages

from core.filters import *
from core.models import *
from django.contrib.auth import authenticate, login, logout


@login_required(login_url='login')
def index(request):
    t_sale_invoice = SaleInvoice.objects.select_related().count()
    t_sale = SaleItem.objects.values_list().aggregate(Sum('total_amt'))

    t_payment = Payment_Entry.objects.select_related().count()
    t_total_payment = Payment_Entry.objects.values_list().aggregate(Sum('paid_amount'))

    t_purchase = Purchase.objects.select_related().count()
    t_p_sale = PurchaseItem.objects.values_list().aggregate(Sum('total_amt'))

    t_item = Item.objects.select_related().count()
    t_customer = Customer.objects.select_related().count()

    context = {'t_sale_invoice': t_sale_invoice, 't_sale': t_sale,
               't_payment': t_payment, 't_purchase': t_purchase,
               't_p_sale': t_p_sale, 't_item': t_item, 't_customer': t_customer,
               't_total_payment': t_total_payment, }

    return render(request, 'core/index.html', context)


def base(request):
    return render(request, 'core/base.html')


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('electro/index.html')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.info(request, 'Username Or Password is Incorrect')
                return render(request, 'core/login.html')
        context = {}
        return render(request, 'core/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


# repoerting
def sales_repoert(request):
    s_reports = SaleItem.objects.select_related()
    myFilter = Sales_Filter(request.GET, queryset=s_reports)
    s_reports = myFilter.qs

    context = {'s_reports': s_reports, 'myFilter': myFilter}
    return render(request, 'core/reports/sales_report.html', context)


def purchase_report(request):
    p_reports = PurchaseItem.objects.select_related()
    myFilter = Purchase_Filter(request.GET, queryset=p_reports)
    p_reports = myFilter.qs

    context = {'p_reports': p_reports, 'myFilter': myFilter}
    return render(request, 'core/reports/purchase_report.html', context)


def payment_report(request):
    payment_report = Payment_Entry.objects.select_related()
    myFilter = Purchase_Filter(request.GET, queryset=payment_report)
    payment_repoert = myFilter.qs

    context = {'payment_report': payment_report, 'myFilter': myFilter}
    return render(request, 'core/reports/payment_report.html', context)


def stock_report(request):
    stock_report = Inventory.objects.select_related()

    context = {'stock_report': stock_report}
    return render(request, 'core/reports/stock_report.html', context)

    # def customer_balance(request):
    c_balance_report = SaleItem.objects.select_related()
    b_report = Payment_Entry.objects.select_related()
    # cust_t_payment = Payment_Entry.objects.select_related().values_list('customer_name__customer_name').annotate(
    #     total_paid=Sum('paid_amount'))
    # # cust_t_sale = SaleItem.objects.select_related().values_list('sales_invoice__customer_name__customer_name').annotate(
    # #     total_paid=Sum('total_amt'))
    #
    context = {'c_balance_report': c_balance_report, 'b_report': b_report,
               'cust_t_payment': cust_t_payment, 'cust_t_sale': cust_t_sale}
    return render(request, 'core/reports/customer_balance.html', context)


def customer_balance(request):
    cc_balance_report = SaleItem.objects.select_related()
    bb_report = Payment_Entry.objects.select_related()

    context = {'cc_balance_report': cc_balance_report, 'bb_report': bb_report}
    return render(request, 'core/reports/customer_balance.html', context)


def customer_total_report_summary(request):
    customer_ids = SaleItem.objects.values_list('sales_invoice__customer_name_id', flat=True).distinct()
    c_balance_report = {}

    for customer_id in customer_ids:
        customer_name = Customer.objects.get(id=customer_id).customer_name

        sale_items = SaleItem.objects.filter(sales_invoice__customer_name_id=customer_id)
        payments = Payment_Entry.objects.filter(customer_name=customer_id).order_by('-payment_date')

        total_invoice_amount = sum(sale_item.total_amt for sale_item in sale_items)
        total_paid_amount = sum(payment.paid_amount for payment in payments)
        actual_credit = total_invoice_amount - total_paid_amount

        last_payment = payments.first()
        balance_before_last_payment = actual_credit + last_payment.paid_amount if last_payment else actual_credit

        c_balance_report[customer_name] = {
            'total_invoice_amount': total_invoice_amount,
            'total_paid_amount': total_paid_amount,
            'actual_credit': actual_credit,
            'last_payment': last_payment.paid_amount if last_payment else 0,
            'balance_before_last_payment': balance_before_last_payment
        }

    context = {'c_balance_report': c_balance_report}
    return render(request, 'core/reports/total_customer_summary_report.html', context)


def item_balance(request):
    items = Inventory.objects.values('item__name').annotate(
        pur_qty=Sum('pur_qty'),
        sale_qty=Sum('sale_qty')
    )
    for item in items:
        if item['pur_qty'] and item['sale_qty'] is not None:
            item['balance'] = item['pur_qty'] - item['sale_qty']
        else:
            item['balance'] = item['pur_qty']
    context = {'items': items}
    return render(request, 'core/reports/item_balance.html', context)
