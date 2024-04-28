from django.contrib import admin
from bikeapp.models import Product,Cart,Order

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display =['name' ,'price' ,'pdetails','is_active']
    list_filter =['cat','is_active']

admin.site.register(Product,ProductAdmin)
admin.site.register(Cart)
admin.site.register(Order)

