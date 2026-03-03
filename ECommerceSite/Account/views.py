from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .forms import UserRegisterForm, UserUpdateForm, UserAuthForm
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import UserProfile
from django.core.cache import cache
from ECommerceSite.utils import trimite_mail_admin_custom
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            messages.debug(request, f"Generare cod pentru userul {user_form.cleaned_data['username']}")
            user.cod = str(uuid.uuid4())
            user.email_confirmat = False
            user.save()
            try:
                relative_link = reverse('confirma_email', args=[user.cod])
                link = request.build_absolute_uri(relative_link)
                context = {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'confirmation_link': link
                }
                html_content = render_to_string('Account/confirmation_email.html', context)
                text_content = strip_tags(html_content)

                email = send_mail(
                    subject='Confirmare Cont',
                    message=text_content,
                    html_message=html_content,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.success(request, "Cont creat! Verifica email-ul pentru confirmare.")
            except Exception as e:
                print("------------------------------------------------")
                print("EROARE DETALIATA:", e)
                print("------------------------------------------------")
                messages.warning(request, f"Cont creat, dar email-ul nu a putut fi trimis: {e}")
            return redirect('login')
    else:
        user_form = UserRegisterForm()

    context = {'user_form': user_form}
    return render(request,'Account/register.html', context)
def confirm_email_view(request, cod):
    user = get_object_or_404(UserProfile, cod=cod)

    if user.email_confirmat:
        messages.info(request, "Acest cont este deja confirmat.")
    else:
        user.email_confirmat = True
        user.cod = None
        user.save()
        messages.success(request, "Email confirmat cu succes! Acum te poti loga.")

    return render(request, 'Account/email_confirmat_succes.html')
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        passw = request.POST.get('password')

        user = authenticate(request, username=username, password=passw)
        if user is None:
            ip_address = get_client_ip(request)
            cache_key = f"login_fail_{ip_address}_{username}"
            attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, attempts, 120)

            if attempts >= 3:
                # Trimitem mail la admini
                msg = f"Utilizatorul '{username}' a esuat logarea de {attempts} ori in ultimele 2 minute. IP: {ip_address}"

                trimite_mail_admin_custom(
                    subiect="Logari suspecte",
                    mesaj_text=msg
                )
            messages.error(request, "Username sau parola gresita.")
        else:

            # Login reusit stergem incercarile esuate
            ip_address = get_client_ip(request)
            cache.delete(f"login_fail_{ip_address}_{username}")
            if user.blocat:
                messages.error(request, "Contul tau a fost blocat. Contacteaza un moderator.")
                return render(request, 'Account/login.html')
            if not user.email_confirmat:
                messages.error(request, "Nu te poți loga până nu confirmi adresa de e-mail.")
                return redirect('login')
            login(request, user)
            return redirect('home')
    form = UserAuthForm
    return render(request, 'Account/login.html',{'form':form} )
def index(request):

    if request.user.is_authenticated:
        user_update_form = UserUpdateForm(instance=request.user)
        context = {'user_update_form': user_update_form}
        return render(request, 'Account/index.html', context=context)
    return redirect('login')
@login_required()
def updateUserProfile(request):

    if request.user.is_authenticated:
        if request.method == 'POST':
            user_form = UserUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                if user_form.has_changed():
                    user_form.save()
                    messages.success(request, f'Your account has been updated!')
                else:
                    messages.warning(request, f'nu ai schimbat nimic!')

            else:
                messages.error(request, user_form.errors)
            return redirect('account')
@login_required
def claim_offer(request):
    content_type = ContentType.objects.get_for_model(UserProfile)
    permission = Permission.objects.get(
        codename='vizualizeaza_oferta',
        content_type=content_type
    )
    request.user.user_permissions.add(permission)
    messages.info(request,"Oferta a fost creditata")
    return redirect('pagina_oferta')
@login_required()
def pagina_oferta(request):
    if not request.user.has_perm('Account.vizualizeaza_oferta'):
        context = {
            'titlu': 'Eroare afisare oferta',
            'mesaj_personalizat': 'Nu ai voie sa vizualizezi oferta, ai trisat (trebuia sa dai click pe banner).',
        }
        return render(request, 'Utils/403.html', context, status=403)
    return render(request, 'Products/oferta.html')



