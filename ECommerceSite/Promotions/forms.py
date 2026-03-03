from django import forms



class PromotieForm(forms.Form):
    nume_promotie = forms.CharField(max_length=100, label="Nume Intern Promotie")
    subiect = forms.CharField(max_length=200, label="Subiect Email")
    mesaj = forms.CharField(widget=forms.Textarea, label="Mesaj Custom")
    timp_promotie = forms.IntegerField(min_value=1, label="Valabilitate (zile)")
    cod_promotional = forms.CharField(max_length=20, initial="PROMO25")
    valoare_discount = forms.IntegerField(min_value=1, max_value=100, label="Discount (%)", required=True)

    CATEGORII_CHOICES = [
        ('Vinyls', 'Vinyls'),
        ('CDs', 'CDs'),
        ('Cassetes', 'Cassetes'),
    ]

    categorii = forms.MultipleChoiceField(
        choices=CATEGORII_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Categorii Tinta",
        initial=('CDs',),
    )

