
import os
from xml.etree.ElementTree import tostring

import django
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mass_mail
from django.contrib.auth import get_user_model
from Products.models import Product
from ECommerceSite.utils import trimite_mail_admin_custom
logger = logging.getLogger('django')
User = get_user_model()

def task_newsletter():
    timp_vechime = timezone.now() + timedelta(minutes= getattr(settings, 'SCHEDULER_USER_AGE_MINUTES', 60))
    users = User.objects.filter(email_confirmat=True, date_joined__lt=timp_vechime)
    produs = Product.objects.order_by('?').first() # alege produs random
    mesaje = []
    if produs:
        nume_produs = produs.name
        for user in users:
            subiect = f"Produsul saptamanii este aici!"
            mesaj = (f"Salut, {user.username}!\n"
                     f"Avem o reducere speciala la produsul saptamanii: {nume_produs} !\n\n"
                     f"Intra pe site pentru a verifica promotia.\n"
                     f"Zi frumoasa in continuare!")
            mesaje.append((subiect, mesaj, settings.EMAIL_HOST_USER, [user.email]))
    if mesaje:
        send_mass_mail(mesaje)
        logger.info(f"Promotia \"Produsul saptamanii\" s-a generat si trimis cu succes la {len(mesaje)} useri.")
    else:
        logger.info(f"Nu s-au gasit produse s-au useri pentru Produsul saptamanii")
def task_delete_unconfirmed_users():
    k_min_delete = getattr(settings, 'SCHEDULER_K_DELETE_AGE', 30)
    timp_limita = timezone.now() - timedelta(minutes=k_min_delete)
    users_to_delete = User.objects.filter(email_confirmat=False, date_joined__lt=timp_limita)
    if users_to_delete.exists():
        users_to_delete.delete()
        logger.info("Am sters utilizatorii neconfirmati")
    else:
        logger.info("Nu exista utilizatorii neconfirmati")
def task_raport_saptamanal():
    total_useri = User.objects.count()
    total_produse = Product.objects.count()
    msg = f"Saptamana {timezone.now().isocalendar()[1]}: Total Useri: {total_useri} | Total Produse: {total_produse}"
    trimite_mail_admin_custom("Raport Saptamanal :)",msg)
    logger.info(msg)
def task_raport_stoc():
    products = Product.objects.filter(stock__lte=5)
    products_names = [x.name for x in products]
    message = (f"Produse cu stoc super redus"
               f"{products_names}")
    subiect = "Produse cu stoc super redus"
    trimite_mail_admin_custom(subiect, message)