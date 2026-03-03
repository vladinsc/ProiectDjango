from django.conf import settings
from django.shortcuts import render
from django.core.exceptions import PermissionDenied


def custom_403_view(request, exception=None):
    current_count = request.session.get('403_counter', 0) + 1
    request.session['403_counter'] = current_count

    mesaj = ""
    if exception:
        mesaj = str(exception)

    if not mesaj:
        mesaj = "Nu aveti permisiunea de a accesa aceasta resursa."

    context = {
        'titlu': "",
        'mesaj_personalizat': mesaj,
        'count': current_count,
        'n_max': settings.N_MAX_403,
    }

    return render(request, 'Utils/403.html', context, status=403)


def test_interzis_view(request):
    raise PermissionDenied("Acesta este un mesaj de test pentru ruta /interzis/")