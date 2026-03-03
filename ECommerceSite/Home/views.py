from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import datetime
from .middlewares import Accesari
from Products.models import Category
import os
import time
import json
import re
from django.contrib import messages
from django.conf import settings
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from .forms import ContactForm
def afis_data(mod=None):
    luni = ['Ianuarie', 'Februarie' , 'Martie', 'Aprilie', 'Mai', 'Iunie', 'Iulie', 'August', 'Septembrie', 'Octombrie', 'Noiembrie', 'Decembrie']
    zile= ['Luni', 'Marti', 'Miercuri', 'Joi', 'Vineri', 'Sambata', 'Duminica']
    now = datetime.datetime.now()
    now = datetime.datetime.now()
    zi_sapt = zile[now.weekday()]
    zi_luna = now.day
    luna = luni[now.month - 1]
    an = now.year
    ora = now.strftime("%H:%M:%S")
    if mod == "zi":
        return f"<h2>Data si ora</h2><p>{zi_sapt}, {zi_luna} {luna} {an}</p>"
    elif mod == "timp":
        return f"<h2>Data si ora</h2><p>{ora}</p>"
    else:
        return f"<h2>Data si ora</h2><p>{zi_sapt}, {zi_luna} {luna} {an} - {ora}</p>"


def home(request):
    return render(request, 'Home/home.html')
# Create your views here.
@login_required()
def info(request):
    is_admin_site = request.user.is_authenticated and request.user.groups.filter(name='Administratori_Site').exists()

    if not is_admin_site:
        context = {
            'titlu': 'Acces Refuzat',
            'mesaj_personalizat': 'Doar administratorii site-ului pot vedea informatiile sistemului.',
        }
        return render(request, 'Utils/403.html', context, status=403)
    data = request.GET.get('data')
    mod = ''
    if data is not None:
        mod = afis_data(data)
    return render(request, 'Home/info.html', context={'mod': mod,})
@login_required()
def log(request):
    is_admin_site = request.user.is_authenticated and request.user.groups.filter(name='Administratori_Site').exists()
    if not is_admin_site:
        context = {
            'titlu': 'Acces Refuzat',
            'mesaj_personalizat': 'Nu aveti permisiunea sa accesati log-urile.',
        }
        return render(request, 'Utils/403.html', context, status=403)
    ultimele = request.GET.get('ultimele')
    accesari = request.GET.get('accesari')
    if ultimele is not None:
        ultimele = int(ultimele)
        listaacc = Accesari[-ultimele:]
    else:
        if accesari is not None:
            accesari = int(accesari)
            listaacc = Accesari[:accesari]
        else:
            listaacc = Accesari
    return render(request, 'Home/log.html', context={'listaacc': listaacc})





def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            dob = data['data_nastere']
            today = date.today()
            rdelta = relativedelta(today, dob)
            varsta_str = f"{rdelta.years} ani și {rdelta.months} luni"
            raw_mesaj = data['mesaj']
            clean_mesaj = raw_mesaj.replace('\n', ' ').replace('\r', ' ')
            clean_mesaj = re.sub(r'\s+', ' ', clean_mesaj)
            def cap_after_punct(match):
                return match.group(0).upper()
            clean_mesaj = re.sub(r'([.?!]|\.\.\.)\s*([a-z])', cap_after_punct, clean_mesaj)
            is_urgent = False
            tip = data['tip_mesaj']
            zile = data['zile_asteptare']
            limit_req = 4 if tip in ['review', 'cerere'] else (2 if tip == 'intrebare' else 0)
            if limit_req > 0 and zile == limit_req:
                is_urgent = True
            del data['confirm_email']
            del data['data_nastere']
            final_data = {
                **data,  # Restul campurilor
                'mesaj': clean_mesaj,
                'varsta': varsta_str,
                'urgent': is_urgent,
                'time_received': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'user_ip': request.META.get('REMOTE_ADDR'),
            }
            folder_path = os.path.join(settings.BASE_DIR, 'Mesaje')
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            timestamp = int(time.time())
            urgent_suffix = "_urgent" if is_urgent else ""
            filename = f"mesaj_{timestamp}{urgent_suffix}.json"
            file_path = os.path.join(folder_path, filename)

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(final_data, f, indent=4, ensure_ascii=False)
                messages.success(request, "Mesajul a fost trimis cu succes!")
                form = ContactForm()
            except Exception as e:
                messages.error(request, f"Eroare la salvarea mesajului: {e}")

    else:
        form = ContactForm()

    return render(request, 'Home/contact.html', {'form': form})