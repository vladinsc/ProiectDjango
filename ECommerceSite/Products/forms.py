from django import forms
from .models import Category, Product, ProductImage
from django.core.exceptions import ValidationError
import re
from django.forms import inlineformset_factory

class ProductFilterForm(forms.Form):
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name)<3:
            raise forms.ValidationError("Cautarea dupa nume se face cu minim 3 caractere")
        return name
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        if min_price is not None and max_price is not None and min_price > max_price:
            raise forms.ValidationError("Pretul minim nu poate fi mai mare decat pretul maxim")
        return cleaned_data
    items_per_page = [("5", "5 pe pagina"), ("10", "10 pe pagina")]
    name = forms.CharField(
        required=False,
        label="Name",
        widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Name of your product',
               }),
        validators=[clean_name],)
    stoc = forms.ChoiceField(
        required=False,
        label="Disponibilitate",
        choices=[("", "Toate"),
            ("IN", "In Stoc"),
            ("LOW", "Stoc Redus"),
            ("OUT", "Out of stock")],
        widget = forms.Select(attrs={'class': 'form-control', 'type': 'dropdown'}),
    )
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        label="Pret Minim",
        widget=forms.NumberInput(attrs={'placeholder': '0.00'})
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        label="Pret Maxim",
        widget=forms.NumberInput(attrs={'placeholder': '0.00'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Toate Categoriile",
        label="Categorie",
        widget = forms.Select(attrs={'class': 'form-control', 'type': 'dropdown'}),
    )
    items_per_page = forms.ChoiceField(
        choices=items_per_page,
        required=False,
        initial='10',
        label="Afișeaza x produse pe pagina"
    )


def valideaza_pozitiv(value):
    if value <= 0:
        raise ValidationError("Valoarea trebuie sa fie strict mai mare decat 0.")
def valideaza_fara_simboluri(value):
    if re.search(r'[@#$]', value):
        raise ValidationError("Textul nu poate contine simbolurile @, # sau $.")
class ProductForm(forms.ModelForm):
    pret_achizitie = forms.DecimalField(
        label="Pret Achizitie (RON)",
        help_text="Pretul cu care a fost cumparat produsul de la furnizor.",
        validators=[valideaza_pozitiv]
    )

    adaos_comercial = forms.IntegerField(
        label="Adaos Comercial (%)",
        help_text="Procentul de profit adaugat (ex: 20 pentru 20%).",
        min_value=0

    )

    class Meta:
        model = Product

        exclude = ['price','sku','slug']


        labels = {
            'nume': 'Denumire Oficiala Produs',
            'descriere': 'Specificatii Tehnice',
            'stoc': 'Cantitate Disponibila'
        }


        help_texts = {
            'nume': 'Introduceti numele complet fara prescurtari.',
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].validators = [valideaza_pozitiv]
        self.fields['name'].validators.append(valideaza_fara_simboluri)

    def clean_descriere(self):
        descriere = self.cleaned_data.get('descriere')
        if len(descriere) < 10:
            raise ValidationError("Specificatiile tehnice trebuie sa contina minim 10 caractere.")
        if "spam" in descriere.lower():
            raise ValidationError("Descrierea contine cuvinte nepermise.")
        return descriere

    def clean_adaos_comercial(self):
        adaos = self.cleaned_data.get('adaos_comercial')
        if adaos > 300:
            raise ValidationError("Adaosul comercial nu poate depasi 300% conform politicii magazinului.")
        return adaos

    def clean_nume(self):
        nume = self.cleaned_data.get('nume')
        if nume and nume[0].islower():
            raise ValidationError("Denumirea produsului trebuie sa inceapa cu litera mare.")
        return nume


    def clean(self):
        cleaned_data = super().clean()
        pret_achizitie = cleaned_data.get('pret_achizitie')
        adaos = cleaned_data.get('adaos_comercial')
        descriere = cleaned_data.get('descriere')

        if pret_achizitie and adaos:
            if pret_achizitie < 10 and adaos < 50:
                raise ValidationError(
                    "Pentru produsele ieftine (sub 10 RON), adaosul comercial trebuie sa fie de minim 50% pentru a acoperi costurile."
                )

        if pret_achizitie and descriere:
            if pret_achizitie > 1000 and len(descriere) < 50:
                raise ValidationError(
                    "Pentru produse scumpe (peste 1000 RON), este necesara o descriere detaliata (minim 50 caractere)."
                )

        return cleaned_data

ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=['image'],
    extra=3,
    can_delete=False
)
