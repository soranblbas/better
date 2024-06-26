import calendar
from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Sum
from django.utils.crypto import get_random_string
import secrets
from django.core.exceptions import ValidationError


class Warehouse(models.Model):
    name = models.CharField(max_length=50)
    address = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'المستودعات'

    def __str__(self):
        return self.name


# Vendor
class Vendor(models.Model):
    full_name = models.CharField(max_length=50)
    # photo = models.ImageField(upload_to="vendor/")
    address = models.TextField(blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    status = models.BooleanField(default=False, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = ' الموردين'

    def __str__(self):
        return self.full_name


class SalesRepresentative(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True,blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    joining_date = models.DateField(null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'المندوب'
# Customer
class Customer(models.Model):
    customer_name = models.CharField(max_length=50, blank=True)
    customer_mobile = models.CharField(max_length=50, blank=True)
    customer_address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    sales_representative = models.ForeignKey(SalesRepresentative, on_delete=models.SET_NULL, null=True, blank=True)

    note = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'الزبائن'

    def __str__(self):
        return self.customer_name


class SaleInvoice(models.Model):
    STATUS = (
        ('مدفوع', 'مدفوع'),
        ('غير مدفوع', 'غير مدفوع'),
        ('المردود', 'المردود'),

    )
    STATUS1 = (
        ('IQD', 'IQD'),
        ('$', '$'),

    )
    invoice_number = models.CharField(max_length=8, unique=True, editable=False)
    customer_name = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS, default='مدفوع')
    note = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    price_type = models.CharField(max_length=10, choices=STATUS1, default='IQD')

    class Meta:
        verbose_name_plural = 'فاتورة البيع'

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate a random 8 character invoice number
            self.invoice_number = secrets.token_hex(4).upper()
            self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.customer_name}- {self.total_sales_amount()}"

    def total_sales_amount(self):
        total_sales_amount = self.saleitem_set.aggregate(total=Sum('total_amt'))['total']
        return total_sales_amount or 0

    def total_discount_amount(self):
        total_discount_amount = self.saleitem_set.aggregate(total=Sum('discount_value'))['total']
        return total_discount_amount or 0

    def total_sub_amount(self):
        total_sales_amount = self.saleitem_set.aggregate(total=Sum('sub_total'))['total']
        return total_sales_amount or 0

    # def clean(self):
    #     sale_items = self.saleitem_set.all()
    #     if not sale_items:
    #         raise ValidationError("At least one item must be selected for the invoice.")

class Payment_Entry(models.Model):
    Qst = (
        ('نقد', 'نقد'),
        ('قسطی ١', 'قسطی ١'),
        ('قسطی ٢', 'قسطی ٢'),
        ('قسطی ٣ ', 'قسطی ٣'),
        ('قسطی ٤', 'قسطی ٤'),
        ('قسطی ٥', 'قسطی ٥'),
        ('قسطی ٦ ', 'قسطی ٦'),
        ('قسطی ٧', 'قسطی ٧'),
        ('قسطی ٨', 'قسطی ٨'),
        ('قسطی ٩ ', 'قسطی ٩'),
        ('قسطی ١٠', 'قسطی ١٠'),
        ('قسطی ١١', 'قسطی ١١'),
        ('قسطی ١٢ ', 'قسطی ١٢'),
    )

    invoice_number = models.CharField(unique=True, editable=False, max_length=10)
    sales_invoice = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE)
    q_type = models.CharField(max_length=10, verbose_name="Payment type", choices=Qst, blank=False)

    paid_amount = models.FloatField(validators=[MinValueValidator(0.01)], default=1)

    discount_amount = models.FloatField(default=0)  # Add this field

    payment_date = models.DateTimeField(blank=False)
    note = models.CharField(max_length=100, blank=True)
    old_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0, editable=False)

    class Meta:
        verbose_name_plural = 'إدخال الدفع'

    def __str__(self):
        return str(self.invoice_number)

    def clean(self):
        if not self.q_type:
            raise ValidationError(' تکایە شێوازی پارەدان هەڵبژێرە؟')

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Get the highest existing invoice number
            highest = Payment_Entry.objects.aggregate(models.Max('invoice_number'))['invoice_number__max']
            if highest is None:
                # If no invoices exist yet, start at 100
                self.invoice_number = 'PINV-100'
            else:
                # Increment the highest invoice number by 1 and add prefix
                prefix, number = highest.split('-')
                self.invoice_number = prefix + '-' + str(int(number) + 1)

        # Apply discount if provided
        self.paid_amount -= self.discount_amount
        TotalPaidAmount.update_total_amount(self.paid_amount)  # Update the total paid amount


        super().save(*args, **kwargs)
    @staticmethod
    def total_paid_amount():
        # Aggregate the paid_amount across all Payment_Entry instances
        total_amount = Payment_Entry.objects.aggregate(total=models.Sum('paid_amount'))['total']
        return total_amount or 0

# Unit


class Unit(models.Model):
    title = models.CharField(max_length=50)
    short_name = models.CharField(max_length=50)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'الوحدات'

    def __str__(self):
        return self.title


# Item Details
class Item(models.Model):
    PRICELIST = (
        # ('مفرد', 'مفرد'),
        ('جملة', 'جملة'),
        #
        # ('شراء', 'شراء'),
        # ('قسط', 'قسط'),

    )
    item_code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=30, default='Test')
    price = models.FloatField(default=1)
    price_list = models.CharField(max_length=30, choices=PRICELIST, default='مفرد')
    note = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'المواد'

    def __str__(self):
        return f"{self.item_code} - {self.price} - {self.price_list}"


# Purchase Invoice
class Purchase(models.Model):
    invoice_number = models.CharField(max_length=8, unique=True, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    note = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = ' فاتورة الشراء'

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate a random 8 character invoice number
            self.invoice_number = secrets.token_hex(4).upper()
        super().save(*args, **kwargs)

    def clean(self):
        if PurchaseItem.item is None:
            raise ValidationError('Please select an Item')

    def __str__(self):
        return f' {self.invoice_number}'

    def total_purchase_amount(self):
        total_purchase_amount = self.purchaseitem_set.aggregate(total=Sum('total_amt'))['total']
        return total_purchase_amount or 0




# Sales Item
class SaleItem(models.Model):
    sales_invoice = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, default="Test")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    qty = models.PositiveSmallIntegerField(default=1)
    total_amt = models.FloatField(editable=False, default=0)
    sale_date = models.DateTimeField(auto_now_add=True)
    is_returned = models.BooleanField(default=False)
    sub_total = models.FloatField(validators=[MinValueValidator(0.01)], default=0)
    discount_type = models.CharField(max_length=30, choices=(('amount', 'Amount'),
                                                             ('percentage', 'Percentage')),
                                      default='percentage', editable=False)
    discount_value = models.FloatField(blank=True, null=True, verbose_name='Discount Percentage')
    modified_price = models.FloatField(blank=True, null=True, verbose_name='Modified Price')  # Add this field

    def save(self, *args, **kwargs):
        if self.modified_price is not None:
            item_price = self.modified_price  # Use modified price if available
        else:
            item_price = self.item.price  # Otherwise, use original item price

        self.sub_total = item_price * self.qty

        if self.discount_type == 'percentage' and self.discount_value is not None:
            discount = self.sub_total * self.discount_value / 100
        else:
            discount = 0

        self.total_amt = self.sub_total - discount

        if self.is_returned and self.sales_invoice.status == "المردود":
            self.total_amt = -self.qty * item_price
        # else:
        #     self.total_amt = self.qty * item_price

        super().save(*args, **kwargs)

        try:
            inventory = Inventory.objects.filter(item__item_code=self.item.item_code,
                                                 warehouse__name=self.warehouse.name).latest('id')
        except Inventory.DoesNotExist:
            raise ValueError(f"{self.item} is not in stock")

        totalBal = inventory.total_bal_qty

        if self.is_returned and self.sales_invoice.status == "المردود":
            sale_qty = 0
            return_qty = self.qty
            totalBal += self.qty  # Add returned quantity to the balance
        else:
            sale_qty = self.qty
            return_qty = 0
            totalBal -= sale_qty  # Subtract sale quantity from the balance

        Inventory.objects.create(
            item=self.item,
            purchase=None,
            warehouse=self.warehouse,
            sale=self.sales_invoice,
            pur_qty=None,
            sale_qty=sale_qty,
            return_qty=return_qty,
            total_bal_qty=totalBal
        )

    def clean(self):
        if self.is_returned and self.qty == 0:
            raise ValidationError('Quantity should be greater than zero when returning items.')

        if self.is_returned and self.sales_invoice.status != "المردود":
            raise ValidationError('تکایە مەردود هەلبژيرە')

    class Meta:
        verbose_name_plural = ' بند المبيعات'


# Purchased Item
class PurchaseItem(models.Model):
    purchase_invoice = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE,default="Test")  # Add this field

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    qty = models.FloatField()
    # item_price = models.ForeignKey(ItemPrice, on_delete=models.CASCADE)
    # price = models.PositiveSmallIntegerField(default=1)
    total_amt = models.FloatField(editable=False, default=0)
    pur_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        self.total_amt = self.qty * self.item.price
        super(PurchaseItem, self).save(*args, **kwargs)

        inventory = Inventory.objects.filter(item__item_code=self.item.item_code, warehouse__name=self.warehouse).order_by(
            '-id').first()
        if inventory:
            totalBal = inventory.total_bal_qty + self.qty
        else:
            totalBal = self.qty
        Inventory.objects.create(
            item=self.item,
            purchase=self.purchase_invoice,
            warehouse=self.warehouse,
            sale=None,
            pur_qty=self.qty,
            sale_qty=None,
            total_bal_qty=totalBal
        )

    # def clean(self):
    #     if self.item.price_list != 'شراء':
    #         raise ValidationError('Price list should be "شراء"')

    class Meta:
        verbose_name_plural = ' العنصر الذي تم شراؤه'


# Inventories
class Inventory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, default=0, null=True)
    sale = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE, default=0, null=True)
    pur_qty = models.FloatField(default=0, null=True)
    sale_qty = models.FloatField(default=0, null=True)
    total_bal_qty = models.FloatField(default=0)
    return_qty = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = ' تفاصيل المخزون'

    def __str__(self):
        return str(self.item)
    #
    # def calculate_balance_quantity(self):
    #     # Calculate the total balance quantity based on the purchase and sale quantities
    #     if self.purchase and self.sale:
    #         self.total_bal_qty = self.pur_qty - self.sale_qty
    #     elif self.purchase:
    #         self.total_bal_qty = self.pur_qty
    #     elif self.sale:
    #         self.total_bal_qty = -self.sale_qty
    #     else:
    #         self.total_bal_qty = 0
    #
    #     return self.total_bal_qty


class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birthdate = models.DateField()
    phone_number = models.CharField(max_length=20)
    relative_phone_number = models.CharField(max_length=20)
    hire_date = models.DateField()
    job_title = models.CharField(max_length=50)
    department = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name_plural = ' الموظفون'


from decimal import Decimal


class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    fines = models.DecimalField(max_digits=30, decimal_places=2, default=0, blank=True)
    slfa = models.DecimalField(max_digits=30, decimal_places=2, default=0, blank=True)

    amount = models.DecimalField(max_digits=30, decimal_places=2)
    final_amount = models.DecimalField(max_digits=30, decimal_places=2, default=0, blank=True, null=True)
    date = models.DateField()  # Remove auto_now=True
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.employee} - {self.amount} - {self.date}"

    def absent_days(self):
        # Calculate the number of absent days for the employee
        return Attendance.objects.filter(employee=self.employee, status='Absent').count()

    @property
    def amount_deducted_per_day(self):
        # Calculate the amount deducted per absent day
        total_salary = self.amount - self.fines - self.slfa
        days_in_month = calendar.monthrange(self.date.year, self.date.month)[1] if self.date else 0
        daily_salary = total_salary / Decimal(days_in_month) if days_in_month > 0 else 0

        # Format the daily_salary to display only two digits after the decimal point
        return '{:.4f}'.format(daily_salary)

    def save(self, *args, **kwargs):
        # Convert float fields (if necessary) to Decimal before calculating final_amount
        self.fines = Decimal(str(self.fines))
        self.slfa = Decimal(str(self.slfa))
        self.amount = Decimal(str(self.amount))

        # Calculate the final salary after subtracting fines and slfa
        total_salary = self.amount - self.fines - self.slfa

        # Calculate the number of absent days for the employee
        absent_days = Attendance.objects.filter(employee=self.employee, status='Absent').count()

        # Get the number of days in the corresponding month if self.date is set
        days_in_month = 0
        if self.date:
            days_in_month = calendar.monthrange(self.date.year, self.date.month)[1]

        # Calculate the daily salary by dividing the total salary by the total days in the month (if available)
        daily_salary = total_salary / Decimal(days_in_month) if days_in_month > 0 else 0

        # Update the final_amount to be the daily salary multiplied by the number of absent days
        self.final_amount = total_salary - (daily_salary * absent_days)

        # Save the salary entry
        with transaction.atomic():
            super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = ' الرواتب'


class JournalEntry(models.Model):
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=30, decimal_places=2)
    description = models.TextField()
    type = models.CharField(max_length=30, default='IQD', choices=(
        ('IQD', 'IQD'),
        ('$', 'Dollar'),

    ))

    def __str__(self):
        return f"{self.date} - {self.amount} - {self.description}"

    class Meta:
        verbose_name_plural = ' المصاريف'


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now)
    status = models.CharField(max_length=30, choices=(
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Sick', 'Sick'),
    ))
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.status}"

    class Meta:
        verbose_name_plural = ' الغيابات'


class OpeningBalance(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='opening_balances')
    balance_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Opening Balance for {self.customer.customer_name}: {self.balance_amount} ({self.date_created})"
    class Meta:
        verbose_name_plural = ' رصيد افتتاحي'


class ChartOfAccounts(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الحساب")

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = ' اسم الحساب'
class Account(models.Model):
    chart_of_account = models.ForeignKey(ChartOfAccounts, on_delete=models.CASCADE, verbose_name="القائمة")
    name = models.CharField(max_length=100, verbose_name="اسم الحساب")

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'الحساب'
class TotalPaidAmount(models.Model):
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def __str__(self):
        return self.total_amount
    @classmethod
    def get_total_amount(cls):
        total_paid_amount = cls.objects.first()
        if total_paid_amount:
            return total_paid_amount.total_amount
        return 0

    @classmethod
    def update_total_amount(cls, amount):
        total_paid_amount = cls.objects.first()
        if total_paid_amount:
            total_paid_amount.total_amount = float(total_paid_amount.total_amount) + amount
            total_paid_amount.save()
        else:
            cls.objects.create(total_amount=amount)

    @classmethod
    def deduct_amount(cls, amount):
        total_paid_amount = cls.objects.first()
        if total_paid_amount:
            total_paid_amount.total_amount -= amount
            if total_paid_amount.total_amount < 0:
                total_paid_amount.total_amount = 0
            total_paid_amount.save()
    class Meta:
        verbose_name_plural = 'اجمال الدفع'
class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name="الحساب")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ")
    date = models.DateField(auto_now_add=True, verbose_name="التاريخ")

    def __str__(self):
        return f"{self.account} - {self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the transaction first
        TotalPaidAmount.deduct_amount(self.amount)  # Deduct the transaction amount from the total paid amount
    class Meta:
        verbose_name_plural = 'تحويل فلوس'