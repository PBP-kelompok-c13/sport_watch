# checkout/models.py
from django.conf import settings
from django.db import models

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product_id = models.CharField(max_length=64)  #Reference ke shop
    name_snapshot = models.CharField(max_length=200)
    price_snapshot = models.IntegerField()   # simpan harga saat ditambahkan
    qty = models.PositiveIntegerField(default=1)

class Order(models.Model):
    ORDER_STATUS = [('NEW','NEW'),('PAID','PAID'),('CANCELLED','CANCELLED')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=12, choices=ORDER_STATUS, default='NEW')
    subtotal = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)
    tax = models.IntegerField(default=0)
    shipping = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.CharField(max_length=64)
    name_snapshot = models.CharField(max_length=200)
    price_snapshot = models.IntegerField()
    qty = models.PositiveIntegerField()

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=12, default='PENDING')  #PENDING/SUCCESS/FAILED
    provider = models.CharField(max_length=50, default='DUMMY')
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
