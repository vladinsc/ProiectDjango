from uuid import uuid4
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Case, When, IntegerField
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Products.models import Product, Category
from Cart.models import Cart
from Promotions.models import Vizualizare
from .forms import ProductFilterForm, ProductForm, ProductImageFormSet
import os
from django.conf import settings
from django.utils.text import slugify
import logging
from ECommerceSite.utils import trimite_mail_admin_custom


# TO DO ADD CACHING
logger = logging.getLogger('django')

def index(request, category_slug=None):
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    sort = request.GET.get('sort','a')
    products = Product.objects.all().select_related('category').annotate(
        is_out_of_stock=Case(
            When(stock=0, then=1),
            default=0,
            output_field=IntegerField(),
        )
    ).order_by('is_out_of_stock', 'name')
    current_category = None

#Filtre
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        print(current_category)
        products = products.filter(category=current_category)
        print(products)
    form = ProductFilterForm(request.GET or None)
    paginator = Paginator(products, 5)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        form_category = cleaned_data.get('category')
        if current_category and form_category and form_category != current_category:
            messages.error(request,
                           "Sunteti deja pe o pagina de categorie")
        elif not current_category and form_category:
            products = products.filter(category=form_category)
        print(products)
        if cleaned_data.get('name'):
            products = products.filter(name__icontains=cleaned_data.get('name'))
        if cleaned_data.get('min_price'):
            products = products.filter(price__gte=cleaned_data.get('min_price'))

        if cleaned_data.get('max_price'):
            products = products.filter(price__lte=cleaned_data.get('max_price'))
        if cleaned_data.get('stoc'):
            disp = cleaned_data.get('stoc')
            print(disp)
            if disp == "":
                pass
            if disp == "IN":
                products = products.filter(stock__gte=10)
            if disp == "LOW":
                products = products.filter(stock__lte=10)
            if disp == "OUT":
                products = products.filter(stock__exact=0)
        if 'items_per_page' in request.GET and form.cleaned_data.get('items_per_page') and form.cleaned_data.get('items_per_page')!= "None" :
            messages.warning(request,
                             "in urma repaginarii e posibil sa fi sarit peste unele produse sau ca ar putea sa le vada din nou pe cele deja vizualizate")
        default_items_per_page = ProductFilterForm.base_fields['items_per_page'].initial
        items_per_page = form.cleaned_data.get('items_per_page', default_items_per_page)
        paginator = Paginator(products, items_per_page)
    if sort == 'a':
        products = products.order_by('price')
    elif sort == 'd':
        products = products.order_by('-price')
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    items_per_page = ProductFilterForm.base_fields['items_per_page'].initial
    import json
    products_js = [p.to_json() for p in products]
    context = {
        'products': page_obj,
        'current_category': current_category,
        'previous_items_per_page': items_per_page,
        'form': form,
        'query_params': request.GET.urlencode(),
        'products_js':json.dumps(products_js, cls=DjangoJSONEncoder),
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'Products/_product_list_partial.html', context)
    return render(request, 'Products/index.html', context=context)

def product(request,slug):
    product = get_object_or_404(Product, slug=slug)
    if request.user.is_authenticated:
        try:
            Vizualizare.objects.create(user=request.user, produs=product)
        except Exception as e:
            print(e)

    id = int(product.id)
    print(id)
    id = str(id)
    print(id)
    imagesurls = f".{settings.MEDIA_URL}products/{id}/images/"
    print(imagesurls)
    imageurls=[f"{settings.MEDIA_URL}products/{id}/images/{filename}" for filename in os.listdir(str(imagesurls))]
    print(imageurls)
    import json
    products_js = [product.to_json()]

    return render(request, 'Products/product-page.html', {'id':id, 'imagesurls':imageurls, 'product': product, 'products_js': json.dumps(products_js, cls=DjangoJSONEncoder)})

@login_required
def addToCartView(request, prodid):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.add_to_cart(prodid)
    messages.success(request, "Product added to cart!")
    return redirect(request.META.get('HTTP_REFERER', 'cart'))
@login_required()
def addProductView(request):
    if not request.user.has_perm('Products.add_product'):
        context = {
            'titlu': 'Eroare adaugare produse',
            'mesaj_personalizat': 'Nu ai permisiunea sa adaugi produse.',
        }
        return render(request, 'Utils/403.html', context, status=403)

    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)
        try:

            if form.is_valid() and formset.is_valid():

                product = form.save(commit=False)
                pret_achizitie = form.cleaned_data['pret_achizitie']
                messages.debug(request, f"Se proceseaza produsul")
                adaos = form.cleaned_data['adaos_comercial']
                product.price = pret_achizitie * (1 + adaos / 100)
                product.slug = slugify(product.name)
                product.sku = f"{product.slug[:40]}-{str(uuid4())[:10].upper()}"
                logger.debug(f"Calcul pret: Achizitie={pret_achizitie}, Adaos={adaos}, Final={product.price}")
                product.save()
                formset.instance = product
                formset.save()

                messages.success(request, f"Produsul '{product.name}' a fost adaugat cu succes!")
                return redirect('products')
            else:
                messages.error(request, "Exista erori in formular. Verifica datele.")
        except Exception as e:
            error_message = str(e)
            html_error = f"""
                    <div style="background-color: red; color: white; padding: 15px;">
                        <h3>Detalii Eroare:</h3>
                        <pre>{error_message}</pre>
                    </div>
                    """
            trimite_mail_admin_custom(
                subiect=f"Eroare Critica in Adaugare Produs: {type(e).__name__}",
                mesaj_text=f"A aparut o eroare: {error_message}",
                continut_html_extra=html_error
            )
    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    context = {
        'form': form,
        'formset': formset
    }
    return render(request, 'Products/add_product.html', context)