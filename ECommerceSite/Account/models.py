from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class UserProfile(AbstractUser):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True,unique=True,null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    cod = models.CharField(max_length=100, null=True, blank=True)
    email_confirmat = models.BooleanField(default=False)
    blocat = models.BooleanField(default=False, help_text="Daca este bifat, utilizatorul nu se poate loga.")
    needs_profile_notification = models.BooleanField(default=False) #daca este True, user-ul va primii notificare cand se logheaza
    last_notification = models.DateTimeField(null=True, blank=True)
    class Meta:
        permissions = [
            ("vizualizeaza_oferta", "Poate vizualiza oferta speciala de reducere"),
        ]
    def __str__(self):
        return f"{self.username}"
    def is_member(self, group)->bool:
        if self.is_authenticated:
            return self.groups.filter(name=group).exists()
        return False


class Address(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='addresses', default=1)
    street = models.CharField(max_length=100, blank=True,unique=False)
    city = models.CharField(max_length=100, blank=True,unique=False)
    state = models.CharField(max_length=100, blank=True,unique=False)
    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}"

# class AdressUser(models.Model):
#     address = models.ForeignKey(Address, on_delete=models.CASCADE)
#     user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='addresses')
#     pk = models.CompositePrimaryKey('address', 'user', primary_key=True)
