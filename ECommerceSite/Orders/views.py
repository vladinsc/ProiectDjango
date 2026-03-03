import json
import os
import time
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone

from weasyprint import HTML

from Products.models import Product
from Account.models import UserProfile, Address
from .models import Order, OrderItem  # Asigura-te ca sunt importate corect din fisierul tau


def place_order(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Trebuie sa fii logat!'}, status=403)

        try:
            data = json.loads(request.body)
            if not data:
                return JsonResponse({'status': 'error', 'message': 'Cosul este gol!'}, status=400)

            try:
                user_profile = UserProfile.objects.get(username=request.user.username)
            except UserProfile.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Profil utilizator inexistent!'}, status=400)

            order = Order.objects.create(
                user=user_profile,
                status=Order.StatusChoices.PENDING
            )

            items_for_invoice = []
            total_quantity = 0
            for prod_id, item_data in data.items():
                qty = item_data
                if isinstance(item_data, dict):
                    qty = item_data.get('qty', item_data.get('quantity', 0))

                qty = int(qty)
                if qty <= 0: continue

                try:
                    product = Product.objects.get(id=prod_id)

                    if product.stock < qty:
                        order.delete()
                        return JsonResponse({'status': 'error', 'message': f'Stoc insuficient pentru {product.name}'},
                                            status=400)

                    product.stock -= qty
                    product.save()

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty
                    )

                    subtotal = qty * product.price

                    total_quantity += qty

                    items_for_invoice.append({
                        'product_name': product.name,
                        'product_url': product.get_absolute_url(),
                        'price': float(product.price),
                        'quantity': qty,
                        'subtotal': float(subtotal)
                    })

                except Product.DoesNotExist:
                    continue

            total_price_calculated = sum(item['subtotal'] for item in items_for_invoice)

            context = {
                'order': order,
                'user_profile': user_profile,
                'user': request.user,
                'items': items_for_invoice,
                'total_price': total_price_calculated,
                'total_quantity': total_quantity,
                'admin_email': settings.EMAIL_HOST_USER,
                'domain': get_current_site(request).domain,
                'protocol': 'https' if request.is_secure() else 'http',
                'timestamp_date': timezone.now()
            }

            html_string = render_to_string('Cart/factura.html', context)
            timestamp = int(time.time())
            folder_path = os.path.join(settings.BASE_DIR, 'temporar-facturi', request.user.username)
            os.makedirs(folder_path, exist_ok=True)

            file_name = f"factura-{timestamp}.pdf"
            file_path = os.path.join(folder_path, file_name)

            HTML(string=html_string).write_pdf(file_path)


            email = EmailMessage(
                subject=f'Factura Comanda #{order.id}',
                body=f'Salut {request.user.first_name},\n\nComanda ta a fost inregistrata. Atasat gasesti factura.',
                from_email=settings.EMAIL_HOST_USER,
                to=[request.user.email],
            )
            email.attach_file(file_path)
            email.send(fail_silently=True)

            return JsonResponse({'status': 'success'})

        except Exception as e:
            print(f"Eroare: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Metoda invalida'}, status=405)