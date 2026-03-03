from django import forms
import re
from datetime import date
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from envs.Djnago.Lib.random import choices


def validate_major(value):

    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError("Trebuie sa aveti peste 18 ani pentru a trimite un mesaj.")


def validate_no_links(value):

    if "http://" in value or "https://" in value:
        raise ValidationError("Textul nu poate contine link-uri (http/https).")


def validate_cnp_format(value):
    if not value:
        return
    if not value.isdigit():
        raise ValidationError("CNP-ul trebuie sa contina doar cifre.")
    if len(value) != 13:
        raise ValidationError("CNP-ul trebuie sa aiba exact 13 cifre.")
    if value[0] not in ['1', '2']:
        raise ValidationError("CNP-ul trebuie sa inceapa cu 1 sau 2 (conform cerintei).")

    an = int("19" + value[1:3])
    luna = int(value[3:5])
    zi = int(value[5:7])
    try:
        date(an, luna, zi)
    except ValueError:
        raise ValidationError("Cifrele din CNP nu formeaza o data valid.")


def validate_email_domain(value):
    
    domain = value.split('@')[-1]
    if domain in ['guerillamail.com', 'yopmail.com']:
        raise ValidationError("Nu sunt acceptate adrese de email temporare.")

def validate_text_format(value):

    if not value: return
    if not value[0].isupper():
        raise ValidationError("Textul trebuie sa inceapa cu litera mare.")
    if not re.match(r'^[a-zA-Z\s\-]+$', value):
        raise ValidationError("Textul poate contine doar litere, spatii si cratime.")


def validate_capitalization_after_sep(value):
    if not value: return
    parts = re.split(r'[\s\-]', value)
    for part in parts:
        if part and not part[0].isupper():
            raise ValidationError(f"Cuvântul '{part}' trebuie sa înceapa cu litera mare.")


def validate_message_content(value):

    words = re.findall(r'[a-zA-Z0-9]+', value)

    if not (5 <= len(words) <= 100):
        raise ValidationError(f"Mesajul trebuie sa aiba intre 5 si 100 de cuvinte. Are {len(words)}.")

    for word in words:
        if len(word) > 15:
            raise ValidationError(f"Cuvantul '{word}' este prea lung (max 15 caractere).")

    validate_no_links(value)
class ContactForm(forms.Form):

    nume = forms.CharField(
        required=True,
        max_length=10,
        label="Nume",
        widget=forms.TextInput(attrs={'class':'form-control'}))
    prenume = forms.CharField(required=True,
                              max_length=10,
                              label="Prenume",
                              widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(required=True,
                             label="Email",
                             validators=[validate_email_domain,])
    confirm_email = forms.EmailField(
        required=True,
        label="Confirmare E-mail"
    )
    cnp = forms.CharField(required=False,
                          max_length=13,
                          min_length=13,
                          label="CNP",
                          widget=forms.TextInput(attrs={'class':'form-control'}))
    data_nastere = forms.DateField(required=True,
                                label="Data Nastere",

                                widget=forms.TextInput(attrs={'class':'form-control', 'type': 'date'}))
    tip_mesaj = forms.ChoiceField(required=False,
                                choices=[('neselectat', 'Neselectat'),
                                        ('reclamatie', 'Reclamatie'),
                                        ('intrebare', 'Intrebare'),
                                        ('review', 'Review'),
                                        ('cerere', 'Cerere'),
                                        ('programare', 'Programare'),
                                    ],
                                initial='neselectat',
                                widget=forms.Select(attrs={'class':'form-control', 'type': 'dropdown'}),
                                label="Tip Mesaj",
                                  )
    subiect = forms.CharField(
        max_length=100,
        required=True,
        label="Subiect",
        validators=[validate_text_format, validate_no_links]
    )
    zile_asteptare = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=30,
        label="Minim zile asteptare",
        help_text="Pentru review-uri/cereri minimul este 4, pentru cereri/intrebari minimul este 2. Maximul e 30."
    )
    mesaj = forms.CharField(
        widget=forms.Textarea,
        required=True,
        label="Mesaj (Va rugam sa semnati cu numele dvs. la final)",
        validators=[validate_message_content]
    )
    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get('email')
        conf_email = cleaned_data.get('confirm_email')
        nume = cleaned_data.get('nume')
        prenume = cleaned_data.get('prenume')
        mesaj = cleaned_data.get('mesaj')
        tip_mesaj = cleaned_data.get('tip_mesaj')
        zile = cleaned_data.get('zile_asteptare')
        cnp = cleaned_data.get('cnp')
        dob = cleaned_data.get('data_nasterii')


        if email and conf_email and email != conf_email:
            self.add_error('confirm_email', "Confirmarea email-ului nu corespunde.")

        if mesaj and nume:
            last_word = mesaj.strip().split()[-1]
            if last_word != nume:
                self.add_error('mesaj', f"Mesajul trebuie sa se termine cu semnatura dvs. (Numele: {nume}).")

        if tip_mesaj == 'neselectat':
            self.add_error('tip_mesaj', "Va rugam sa selectati un tip de mesaj.")

        if zile and tip_mesaj:
            min_zile = 0
            if tip_mesaj in ['review', 'cerere']:
                min_zile = 4
            elif tip_mesaj == 'intrebare':
                min_zile = 2

            if zile < min_zile:
                self.add_error('zile_asteptare', f"Pentru '{tip_mesaj}', trebuie sa asteptati minim {min_zile} zile.")

        if cnp and dob:
            an_cnp = int("19" + cnp[1:3])
            luna_cnp = int(cnp[3:5])
            zi_cnp = int(cnp[5:7])

            if dob.year != an_cnp or dob.month != luna_cnp or dob.day != zi_cnp:
                self.add_error('cnp', "Data nasterii din CNP nu corespunde cu data nasterii introdusa.")

        return cleaned_data




