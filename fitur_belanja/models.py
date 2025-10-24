# fitur_belanja/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from shop.models import Product

User = settings.AUTH_USER_MODEL

class Cart(models.Model):
    user         = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    session_key  = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at   = models.DateTimeField(default=timezone.now)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user","session_key"])]

    def __str__(self): return f"Cart({self.pk})"
    @property
    def item_count(self): return sum(i.qty for i in self.items.all())
    @property
    def total(self): return sum(i.subtotal for i in self.items.select_related("product"))

class CartItem(models.Model):
    cart        = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product     = models.ForeignKey(Product, on_delete=models.CASCADE,  related_name='cart_items',
    null=True, blank=True, )
    qty         = models.PositiveIntegerField(default=1)
    unit_price  = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # cache harga saat add

    class Meta:
        unique_together = ("cart","product")

    @property
    def subtotal(self): return self.qty * self.unit_price
