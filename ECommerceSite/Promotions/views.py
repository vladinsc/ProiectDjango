from django.shortcuts import render, redirect
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import PromotieForm
from .models import Promotie, Vizualizare, CategoriePromotie
from Products.models import Category

def creare_promotie(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    if request.method == 'POST':
        form = PromotieForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            data_expirare = timezone.now().date() + timedelta(days=data['timp_promotie'])
            promotie = Promotie.objects.create(
                nume=data['nume_promotie'],
                data_expirare=data_expirare,
                cod=data['cod_promotional'],
                valoare_discount=data['valoare_discount'],
                subiect=data['subiect'],
                mesaj=data['mesaj']
            )

            #Email
            mails = []
            user = get_user_model()
            k=2
            cat_selectate = data['categorii']
            template_name = 'Promotions/promotie_personalizata.txt'
            for cat in cat_selectate:
                categorie = Category.objects.get(name=cat)
                CategoriePromotie.objects.create(categorie=categorie, promotie=promotie)
                users_target = user.objects.filter(
                    Vizualizari__produs__category__name=cat
                ).annotate(
                    nr_viz=Count('Vizualizari')
                ).filter(
                    nr_viz__gte=k  # au vazut minim K produse
                ).distinct()
                for user in users_target:
                    context = {
                        'username': user.username,
                        'subiect': data['subiect'],
                        'data_expirare': data_expirare,
                        'cod': data['cod_promotional'],
                        'discount': data['valoare_discount'],
                        'mesaj': data['mesaj'],
                        'categorie': cat
                    }
                    body_email = render_to_string(template_name, context)
                    mails.append((
                        data['subiect'],
                        body_email,
                        settings.EMAIL_HOST_USER,
                        [user.email]
                    ))
            if mails:
                send_mass_mail(tuple(mails), fail_silently=False)
                messages.success(request, f"Au fost trimise {len(mails)} email-uri.")
            else:
                messages.warning(request, "Niciun utilizator nu a indeplinit conditia K=2 pentru categoriile alese.")
        return redirect('promotii')
    return render(request, 'Promotions/promotii.html', context={'form': PromotieForm()})


