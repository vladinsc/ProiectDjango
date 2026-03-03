
from django.contrib.auth import user_logged_out
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Permission
from .models import Profile, UserProfile
import logging

logger = logging.getLogger('django')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    print(instance)

@receiver(user_logged_out)
def remove_offer_permission(sender,user, request, **kwargs):
    try:
        content_type = ContentType.objects.get_for_model(UserProfile)
        permission = Permission.objects.get(
            codename='vizualizeaza_oferta',
            content_type=content_type
        )
        if user.has_perm('Account.vizualizeaza_oferta'):
            user.user_permissions.remove(permission)
            logger.log(f"Permisiunea de oferta a fost stearsa pentru {user.username}")
    except Exception as e:
        logger.error(f"Eroare la stergere permisiune: {e}")

