from django.db import models
import Products.models as ProductModels
from Account.models import UserProfile, Address
class Order(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    adress = models.ForeignKey(Address, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(auto_now=True)
    class StatusChoices(models.TextChoices):
        PLACED = 'Placed'
        CONFIRMED = 'Confirmed'
        PENDING = 'Pending'
        COMPLETED = 'Completed'
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    def get_total(self):
        summ=0
        for item in self.items.all():
            summ+=item.product.price*item.quantity
        return summ
class OrderItem(models.Model):
    product = models.ForeignKey(ProductModels.Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField(default=1)
    pk = models.CompositePrimaryKey("product", "order", primary_key=True)
