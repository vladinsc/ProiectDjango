import os, shutil
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, ProductImage

def create_product_folder(sender, instance, created, **kwargs):
    if created:
        product_folder = os.path.join(settings.MEDIA_ROOT, 'products', str(instance.id), 'images')
        if not os.path.exists(product_folder):
            os.makedirs(product_folder)
            print(f"Created folder: {product_folder}")

# @receiver(post_save, sender=Product)
# def move_temp_images(sender, instance, created, **kwargs):
#     print("Signaled")
#     if created:
#         temp_folder = os.path.join(settings.MEDIA_ROOT, 'products', 'None')
#         product_folder = os.path.join(settings.MEDIA_ROOT, 'products', str(instance.id), 'images')
#         if os.path.exists(temp_folder):
#             os.makedirs(product_folder, exist_ok=True)
#             for filename in os.listdir(temp_folder):
#                 shutil.move(os.path.join(temp_folder, filename),
#                             os.path.join(product_folder, filename))
#                 print(f"Moved {filename} to {product_folder}")

