from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import Review, Product

def _recalc(product: Product):
    agg = product.reviews.aggregate(avg=Avg("rating"), cnt=Count("id"))
    product.rating_avg = agg["avg"] or 0
    product.rating_count = agg["cnt"] or 0
    product.save(update_fields=["rating_avg", "rating_count"])

@receiver(post_save, sender=Review)
def review_saved(sender, instance, **kwargs):
    _recalc(instance.product)

@receiver(post_delete, sender=Review)
def review_deleted(sender, instance, **kwargs):
    _recalc(instance.product)
