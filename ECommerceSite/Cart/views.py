from django.shortcuts import render
from Products.models import Product
import json


def viewcart(request):
    products = Product.objects.all()
    products_data = []
    for product in products:
        img_url = ""
        if product.images.first():
            img_url = product.images.first().image.url

        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'image': img_url,
            'slug': product.slug
        })

    context = {
        'products_json': json.dumps(products_data)
    }
    return render(request, 'Cart/viewcart.html', context=context)
# Create your views here.
