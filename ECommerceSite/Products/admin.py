from django.contrib import admin
from .models import Category, Product, ProductImage
from django.utils.html import format_html




class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "sku", "date_added",)
    search_fields = ('name', 'sku')
    list_filter = ('category',)
    list_per_page = 5
    ordering = ('date_added','-price')
    inlines = [ProductImageInline]
    fieldsets = (
        ('Required Fields', {
            'fields': ('name', 'price', 'category', 'sku')
        }),
        ('Optional Fields', {
            'classes': ('collapse',),
            'fields': ('description', 'stock',),
        }),
    )
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.images.all.image.url)
        return "-"

    image_tag.short_description = 'Image'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_per_page = 5
#admin.site.register(Category, CategoryAdmin)
# Register your models here.
