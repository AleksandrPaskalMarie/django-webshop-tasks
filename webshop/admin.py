from django.contrib import admin
from .models import Manufacturer, Product

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'founded_year')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'manufacturer', 'price', 'stock_quantity', 'is_available')
