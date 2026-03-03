from django.db import models
from Account.models import UserProfile
from Products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='cart')
    def __str__(self):
        return f"{self.user}'s Cart"
    def get_total(self):
        return sum(item.subtotal() for item in self.items.all())
    def add_to_cart(self, product, quantity=1):
        product = Product.objects.get(pk=product)
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            item=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item
    def delete_item(self,product):
        try:
            cart_item = CartItem.objects.get(cart=self, item=product)
            cart_item.objects.delete()
        except CartItem.DoesNotExist:
            pass
    def remove_item(self, product, quantity=1):
        try:
            cart_item = CartItem.objects.get(cart=self, item=product)
            cart_item.decrease_quantity(quantity)
        except CartItem.DoesNotExist:
            pass

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    pk = models.CompositePrimaryKey("cart", "item", primary_key=True)
    def remove_from_cart(self):
        self.delete()
    def increase_quantity(self, quantity=1):
        self.quantity += quantity
        self.save()
        return self.quantity
    def decrease_quantity(self, quantity=1):
        self.quantity -= quantity
        if self.quantity == 0:
            self.remove_from_cart()
        else:
            self.save()
            return self.quantity
        return 0
    def subtotal(self):
        return self.item.price * self.quantity
    def __str__(self):
        return f"{self.item.name}: {self.subtotal()} RON"

# Create your models here.
