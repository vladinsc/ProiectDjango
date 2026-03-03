from django.contrib import admin
from Orders.models import Order, OrderItem
class OrderItemInline(admin.TabularInline):

    model = OrderItem
    extra = 1
    fields = ('product', 'quantity', 'get_product_price')
    readonly_fields = ('get_product_price',)
    def get_product_price(self, obj):
        if obj.product:
            return obj.product.price
        return 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Order Details', {
            'fields': ('user', 'adress','status','date')

        }),
    )
    inlines = [OrderItemInline]
    list_display = ('id', 'user', 'adress', 'get_total','status', 'date')
    list_filter = ('user',)
    list_editable = ('status', 'adress')
    search_fields = ('user__username','user__name', 'id')
    readonly_fields = ('date',)
