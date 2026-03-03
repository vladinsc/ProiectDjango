from django.db import models
from uuid import uuid4

from django.urls import reverse
from django.utils.text import slugify
from Account.models import UserProfile

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True,blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    def __str__(self):
        return self.name
def product_image_path(instance, filename):
    product_id = instance.product.id if instance.product and instance.product.id else 'temp'
    return f'products/{instance.product.id}/images/{filename}'
class Product(models.Model):

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    sku = models.CharField(max_length=51, unique=True, blank=True)
    stock = models.PositiveIntegerField(default=1)
    description = models.TextField()
    #image = models.ImageField(upload_to=product_image_path, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} {self.name} {self.category} {self.date_added}"
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"{self.slug[:40]}-{str(uuid4())[:10].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product', args=[self.slug])
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
        "price": float(self.price),
        "category": self.category.name,
        "slug": self.slug,
        "stock": self.stock,
            "description": self.description,
            #"date_added": self.date_added,
        "url": self.get_absolute_url(),

        }
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_path)
    def __str__(self):
        return f"Image for {self.product.name}"
    def save(self, *args, **kwargs):
        if not self.product.id:
            self.product.save()
        super().save(*args, **kwargs)
