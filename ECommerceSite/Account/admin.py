from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, Address

class AdressStackedInline(admin.StackedInline):
    model = Address
    extra = 1

@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ("id", "name", "username", "email")
    search_fields = ('name', 'username')

    list_per_page = 5
    ordering = ('id',)
    fieldsets = UserAdmin.fieldsets + (
        ('Required Fields', {
            'fields': ("name", "email_confirmat", "phone_number","blocat")
        }),
        ('Optional Fields', {
            'classes': ('collapse',),
            'fields': ('date_of_birth', 'cod'),
        }),
    )
    inlines = [AdressStackedInline]

    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name='Moderatori').exists() and not request.user.is_superuser:

            all_fields = [f.name for f in self.model._meta.fields]

            editable_fields = ['blocat']

            readonly = [f for f in all_fields if f not in editable_fields]


            return readonly
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Required Fields', {
            'fields': ("street", "city", "state", 'user')
        }),
    )
    list_display = ("id", "street", "city", "state",'user')
    search_fields = ('street', 'city', 'state','user')
    list_per_page = 5
# Register your models here.


