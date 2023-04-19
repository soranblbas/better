from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.crypto import get_random_string
import secrets


# Vendor
class Vendor(models.Model):
    full_name = models.CharField(max_length=50)
    # photo = models.ImageField(upload_to="vendor/")
    address = models.TextField(blank=True)
    mobile = models.CharField(max_length=15, blank=True)
    status = models.BooleanField(default=False, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = '1. Vendors'

    def __str__(self):
        return self.full_name


# Customer
class Customer(models.Model):
    customer_name = models.CharField(max_length=50, blank=True)
    customer_mobile = models.CharField(max_length=50, blank=True)
    customer_address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = '2. Customers'

    def __str__(self):
        return self.customer_name


class SaleInvoice(models.Model):
    STATUS = (
        ('مدفوع', 'مدفوع'),
        ('غير مدفوع', 'غير مدفوع'),
    )
    invoice_number = models.CharField(max_length=8, unique=True, editable=False)
    customer_name = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = '3. Sale Invoice'

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate a random 8 character invoice number
            self.invoice_number = secrets.token_hex(4).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.customer_name}- {self.total_sales_amount()}"

    def total_sales_amount(self):
        total_sales_amount = self.saleitem_set.aggregate(total=Sum('total_amt'))['total']
        return total_sales_amount or 0


class Payment_Entry(models.Model):
    customer_name = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sales_invoice = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE)

    invoice_number = models.CharField(max_length=8, unique=True, editable=False)
    paid_amount = models.FloatField(blank=True)
    payment_date = models.DateTimeField(blank=True)
    note = models.TextField(blank=True)
    old_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0, editable=False)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate a random 8 character invoice number
            self.invoice_number = secrets.token_hex(4).upper()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = '8. Payment Entry'

    def __str__(self):
        return f"{self.invoice_number} - {self.paid_amount}"


# Sales Invoice


# Unit


class Unit(models.Model):
    title = models.CharField(max_length=50)
    short_name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = '5. Units'

    def __str__(self):
        return self.title


# Item Details
class Item(models.Model):
    PRICELIST = (
        ('مفرد', 'مفرد'),
        ('جملة', 'جملة'),

        ('شراء', 'شراء'),
    )

    name = models.CharField(max_length=255)
    price = models.PositiveIntegerField(default=1)
    price_list = models.CharField(max_length=8, choices=PRICELIST, default='مفرد')

    class Meta:
        verbose_name_plural = 'Items'

    def __str__(self):
        return f"{self.name} - {self.price} - {self.price_list}"


# class Price_List(models.Model):
#     price_list = models.CharField(max_length=50, blank=True)
#
#     def __str__(self):
#         return str(self.price_list)
#
#     class Meta:
#         verbose_name_plural = 'Price_List'
#
#
# # Price List
# class ItemPrice(models.Model):
#     # PRICELIST = (
#     #     ('مفرد', 'مفرد'),
#     #     ('جملة', 'جملة'),
#     #
#     #     ('شراء', 'شراء'),
#     # )
#
#     item = models.ForeignKey(Item, on_delete=models.CASCADE)
#     price_list = models.ForeignKey(Price_List, on_delete=models.CASCADE)
#     item_price = models.FloatField()
#
#     class Meta:
#         verbose_name_plural = '6. Item Price'
#
#     def __str__(self):
#         return f'{self.item_price},{self.price_list}'


# Purchase Invoice
class Purchase(models.Model):
    invoice_number = models.CharField(max_length=8, unique=True, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()

    class Meta:
        verbose_name_plural = '8. Purchase Invoice'

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


# payment entry


# Sales Item
class SaleItem(models.Model):
    sales_invoice = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE)

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    qty = models.PositiveSmallIntegerField(default=1)
    # item_price = models.ForeignKey(ItemPrice, on_delete=models.CASCADE)
    # price = models.FloatField()
    total_amt = models.FloatField(editable=False, default=0)
    sale_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        self.total_amt = self.qty * self.item.price
        # self.total_amt = self.total_amt - self.payment_entry.paid_amount
        # item_in_stock = PurchaseItem.objects.filter(item=self.item).first()
        # if item_in_stock:
        #     raise ValidationError("Quantity cannot be greater than the stock amount.")

        super(SaleItem, self).save(*args, **kwargs)

        try:
            inventory = Inventory.objects.filter(item__name=self.item.name).latest('id')
        except Inventory.DoesNotExist:
            raise ValueError(f"{self.item.name} is not in stock")

        totalBal = inventory.total_bal_qty
        if self.qty > totalBal:
            raise ValueError(
                f"Sorry, we don't have enough {self.item.name} in stock right now. "
                f"Please reduce your sale quantity to {totalBal} or less."
            )

        inventory = Inventory.objects.filter(item__name=self.item.name).order_by('-id').first()
        if inventory:
            totalBal = inventory.total_bal_qty - self.qty
        else:
            totalBal = 0

        Inventory.objects.create(
            item=self.item,
            purchase=None,
            sale=self.sales_invoice,
            pur_qty=None,
            sale_qty=self.qty,
            total_bal_qty=totalBal
        )

    def clean(self):
        if self.item.price_list != 'مفرد':
            raise ValidationError('Price list should  be " مفرد or جملة"')

    class Meta:
        verbose_name_plural = '9. Sales Item'


# Purchased Item
class PurchaseItem(models.Model):
    purchase_invoice = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    qty = models.FloatField()
    # item_price = models.ForeignKey(ItemPrice, on_delete=models.CASCADE)
    # price = models.FloatField()
    total_amt = models.FloatField(editable=False, default=0)
    pur_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.total_amt = self.qty * self.item.price
        super(PurchaseItem, self).save(*args, **kwargs)

        inventory = Inventory.objects.filter(item=self.item).order_by('-id').first()
        if inventory:
            totalBal = inventory.total_bal_qty + self.qty
        else:
            totalBal = self.qty
        Inventory.objects.create(
            item=self.item,
            purchase=self.purchase_invoice,
            sale=None,
            pur_qty=self.qty,
            sale_qty=None,
            total_bal_qty=totalBal
        )

    def clean(self):
        if self.item.price_list != 'شراء':
            raise ValidationError('Price list should be "شراء"')

    class Meta:
        verbose_name_plural = '9. Purchased Item'


# Inventories
class Inventory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, default=0, null=True)
    sale = models.ForeignKey(SaleInvoice, on_delete=models.CASCADE, default=0, null=True)
    pur_qty = models.FloatField(default=0, null=True)
    sale_qty = models.FloatField(default=0, null=True)
    total_bal_qty = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = '10. Stock Details'

    def __str__(self):
        return str(self.item)
