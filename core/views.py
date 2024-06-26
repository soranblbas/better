from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, get_object_or_404

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

    t_journal_entry = JournalEntry.objects.select_related().count()
    j_total_amount = JournalEntry.objects.values_list().aggregate(Sum('amount'))
    def calculate_total_purchase_value():
        # Sum up the total purchase amount for all items
        total_purchase_value = PurchaseItem.objects.aggregate(total=models.Sum('total_amt'))['total']
        return total_purchase_value or 0

    def calculate_total_sales_value():
        # Sum up the total sales amount for all items
        total_sales_value = SaleItem.objects.aggregate(total=models.Sum('total_amt'))['total']
        return total_sales_value or 0
    def calculate_current_stock_money_balance():
        # Calculate the total purchase value
        total_purchase_value = calculate_total_purchase_value()

        # Calculate the total sales value
        total_sales_value = calculate_total_sales_value()

        # Calculate the total current stock money balance
        current_stock_money_balance = total_purchase_value - total_sales_value

        return current_stock_money_balance

    context = {'t_sale_invoice': t_sale_invoice, 't_sale': t_sale,
               't_payment': t_payment, 't_purchase': t_purchase,
               't_p_sale': t_p_sale, 't_item': t_item, 't_customer': t_customer,
               't_total_payment': t_total_payment,
               't_journal_entry': t_journal_entry, 'j_total_amount': j_total_amount,'calculate_current_stock_money_balance':calculate_current_stock_money_balance}

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
    payment_repoert = Payment_Entry.objects.select_related()
    myFilter = Payment_Filter(request.GET, queryset=payment_repoert)
    payment_repoert = myFilter.qs

    context = {'payment_repoert': payment_repoert, 'myFilter': myFilter}
    return render(request, 'core/reports/payment_report.html', context)


def stock_report(request):
    def calculate_total_purchase_value():
        # Sum up the total purchase amount for all items
        total_purchase_value = PurchaseItem.objects.aggregate(total=models.Sum('total_amt'))['total']
        return total_purchase_value or 0

    def calculate_total_sales_value():
        # Sum up the total sales amount for all items
        total_sales_value = SaleItem.objects.aggregate(total=models.Sum('total_amt'))['total']
        return total_sales_value or 0
    def calculate_current_stock_money_balance():
        # Calculate the total purchase value
        total_purchase_value = calculate_total_purchase_value()

        # Calculate the total sales value
        total_sales_value = calculate_total_sales_value()

        # Calculate the total current stock money balance
        current_stock_money_balance = total_purchase_value - total_sales_value

        return current_stock_money_balance
        # Calculate the total current stock money balance
    stock_report = Inventory.objects.select_related()

    context = {'stock_report': stock_report,'calculate_current_stock_money_balance':calculate_current_stock_money_balance}
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


def opening_balance_report(request):
    # Get all opening balances
    opening_balances = OpeningBalance.objects.all()

    return render(request, 'core/reports/opening_balance_report.html', {'opening_balances': opening_balances})
def customer_total_report_summary(request):
    customer_ids = SaleItem.objects.values_list('sales_invoice__customer_name_id', flat=True).distinct()
    c_balance_report = {}

    for customer_id in customer_ids:
        customer = Customer.objects.get(id=customer_id)
        customer_name = customer.customer_name
        customer_mobile = customer.customer_mobile
        sales_representative_name = customer.sales_representative.name if customer.sales_representative else None

        sale_items = SaleItem.objects.filter(sales_invoice__customer_name_id=customer_id)
        payments = Payment_Entry.objects.filter(sales_invoice__customer_name_id=customer_id).order_by('-payment_date')

        total_invoice_amount = sum(Decimal(sale_item.total_amt) for sale_item in sale_items)
        total_paid_amount = sum(Decimal(payment.paid_amount) for payment in payments)
        actual_credit = total_invoice_amount - total_paid_amount

        last_payment = payments.first()
        balance_before_last_payment = actual_credit + Decimal(last_payment.paid_amount) if last_payment else actual_credit

        # Fetch opening balance for the customer and convert it to Decimal
        opening_balance = OpeningBalance.objects.filter(customer_id=customer_id).aggregate(total=Sum('balance_amount'))['total'] or Decimal('0')

        # Convert opening_balance to Decimal
        opening_balance = Decimal(str(opening_balance))

        # Calculate final_balance by adding actual_credit to opening_balance
        final_balance = opening_balance + actual_credit

        c_balance_report[customer_name] = {
            'total_invoice_amount': total_invoice_amount,
            'total_paid_amount': total_paid_amount,
            'actual_credit': actual_credit,
            'last_payment': last_payment.paid_amount if last_payment else Decimal('0'),
            'balance_before_last_payment': balance_before_last_payment,
            'opening_balance': opening_balance,
            'final_balance': final_balance,
            'phone_number': customer_mobile,
            'sales_representative_name': sales_representative_name  # Include sales representative's name
        }

    context = {'c_balance_report': c_balance_report}
    return render(request, 'core/reports/total_customer_summary_report.html', context)


def item_balance(request):
    items = Inventory.objects.values('item__item_code', 'item__name', 'warehouse__name').annotate(
        pur_qty=Sum('pur_qty'),
        sale_qty=Sum('sale_qty'),
        return_qty=Sum('return_qty')
    )

    for item in items:
        if item['pur_qty'] and item['sale_qty'] and item['return_qty'] is not None:
            item['balance'] = item['pur_qty'] - item['sale_qty'] + item['return_qty']
        else:
            item['balance'] = item['pur_qty']

    context = {'items': items}
    return render(request, 'core/reports/item_balance.html', context)



def employee_list(request):
    employees = Employee.objects.all()

    # Fetch salary details for each employee
    employee_salary_details = {}
    for employee in employees:
        try:
            salary = Salary.objects.filter(employee=employee).order_by('-date').first()
            employee_salary_details[employee.id] = salary
        except Salary.DoesNotExist:
            # Handle the case when no salary entry is found for an employee
            employee_salary_details[employee.id] = None

    context = {
        'employees': employees,
        'employee_salary_details': employee_salary_details,
    }

    return render(request, 'core/reports/employee_list.html', context)


def journal_entry_list(request):
    t_journal_entry = JournalEntry.objects.select_related().count()
    j_total_amount = JournalEntry.objects.values_list().aggregate(Sum('amount'))
    entries = JournalEntry.objects.select_related()
    context = {'t_journal_entry': t_journal_entry, 'j_total_amount': j_total_amount, 'entries': entries}

    return render(request, 'core/reports/jourrnal_entry_list.html', context)


from django.core.exceptions import ObjectDoesNotExist


def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    try:
        latest_salary = Salary.objects.filter(employee_id=employee).latest('date')
        salary = str(latest_salary.amount)
    except ObjectDoesNotExist:
        salary = '0'

    context = {
        'employee': employee,
        'salary': salary
    }
    return render(request, 'core/reports/employee_detail.html', context=context)


from django.db.models import Sum, F


def single_sale(request, pk_test):
    try:
        s_invoice_list = SaleInvoice.objects.get(id=pk_test)
        s_item_list = SaleItem.objects.filter(sales_invoice=pk_test)
        total_sold_qty = s_item_list.aggregate(total_qty=Sum('qty'))['total_qty'] or 0

        # Get the customer associated with the invoice
        customer = s_invoice_list.customer_name

        # Calculate the total invoice amount for the customer
        total_invoice_amount = sum(
            sale_item.total_amt for sale_item in SaleItem.objects.filter(sales_invoice__customer_name=customer)
        )

        # Calculate the total paid amount for the customer
        total_paid_amount = sum(
            payment.paid_amount for payment in Payment_Entry.objects.filter(sales_invoice__customer_name=customer)
        )

        # Calculate the actual credit for the customer
        actual_credit = total_invoice_amount - total_paid_amount

        # Calculate the total for each invoice
        invoice_total = sum(s_item.sub_total for s_item in s_item_list)

        # Calculate the total for each invoice
        actual_invoice_total = sum(s_item.total_amt for s_item in s_item_list)

        # Calculate the total invoice discount
        invoice_discount = invoice_total - actual_invoice_total

        context = {
            's_invoice_list': s_invoice_list,
            's_item_list': s_item_list,
            'total_sold_qty': total_sold_qty,
            'total_invoice_amount': total_invoice_amount,
            'actual_credit': actual_credit,
            'invoice_total': invoice_total,  # Add invoice total to the context
            'invoice_discount': invoice_discount,  # Add invoice discount to the context
            'actual_invoice_total': actual_invoice_total
        }

        return render(request, 'core/reports/single_sale_report.html', context)
    except:
        return render(request, 'core/reports/single_sale_report.html', )


def user_profile(request):
    us_p = User.objects.all()
    context = {'us_p': us_p}
    return render(request, 'core/reports/users-profile.html', context)


def price_list(request):
    us_p = Item.objects.select_related()
    context = {'us_p': us_p}
    return render(request, 'core/reports/price_list.html', context)


def attendance_list(request):
    attendances = Attendance.objects.all()
    return render(request, 'core/reports/attendance_list.html', {'attendances': attendances})

def transaction_detail(request):
    # Retrieve the transaction object from the database
    t_all= Transaction.objects.select_related()

    # Render the template with the transaction details
    return render(request, 'core/reports/transaction_detail.html', {'t_all':t_all})