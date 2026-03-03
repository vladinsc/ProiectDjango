import urllib.parse
import datetime

Accesari = []

def get_ip(request):
    req_headers = request.META
    str_lista_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if str_lista_ip:
        return str_lista_ip.split(',')[-1].strip()
    else:
        return request.META.get('REMOTE_ADDR')


class Accesare:
    _id = 0
    _nraccesariTotal = 0

    def __init__(self, ip_client, url):
        Accesare._id += 1
        self.id = Accesare._id
        self.ip_client = ip_client
        self.url = url
        self.data = datetime.datetime.now()
        self.nr_accesari = 1
        Accesare._nraccesariTotal += 1


    def lista_parametri(self):
        query = urllib.parse.urlparse(self.url).query
        params = urllib.parse.parse_qs(query)
        return [(k, v[0] if v else None) for k, v in params.items()]
    def url(self):
        return self.url
    def data(self, format_str="%d-%m-%Y %H:%M:%S"):
        return self.data.strftime(format_str)
    def pagina(self):
        return urllib.parse.urlparse(self.url).path

class AccesareMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_ip(request)
        url = request.get_full_path()
        accesare = Accesare(ip, url)
        Accesari.append(accesare)
        response = self.get_response(request)
        return response
