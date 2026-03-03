from django.db import models
from Account.models import UserProfile as User
from Products.models import Product, Category

class Vizualizare(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Vizualizari')
    produs = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='Vizualizari')
    data_vizualizare = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        super().save( *args, **kwargs)
        vizualizari_user = Vizualizare.objects.filter(user=self.user).order_by('-data_vizualizare')
        if vizualizari_user.count() > 5:
            de_sters = vizualizari_user[5:]
            ids_de_sters = [v.id for v in de_sters]
            Vizualizare.objects.filter(id__in=ids_de_sters).delete()
class Promotie(models.Model):
    nume = models.CharField(max_length=50)
    #user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Promotii', blank=True, null=True)
    cod = models.CharField(max_length=20, blank=True, null=True)
    valoare_discount = models.IntegerField(help_text="Procent reducere %")
    data_creare = models.DateTimeField(auto_now_add=True)
    data_expirare = models.DateField()
    subiect = models.CharField(max_length=200, blank=True, null=True)
    mesaj = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.nume
# class ProdusePromotie(models.Model):
#     produs = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ProdusePromotie')
#     promotie = models.ForeignKey(Promotie, on_delete=models.CASCADE, related_name='ProdusePromotie')
#     pk = models.CompositePrimaryKey("produs", "promotie", primary_key=True)
class CategoriePromotie(models.Model):
    categorie = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='CategoriePromotii')
    promotie = models.ForeignKey(Promotie, on_delete=models.CASCADE, related_name='CategoriiPromotie')
    pk= models.CompositePrimaryKey("categorie", "promotie", primary_key=True)




