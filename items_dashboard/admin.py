from django.contrib import admin
from .models import Item, Tag


# Register your models here.
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)


class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "SKU", "category", "stock_status", "available_stock")


admin.site.register(Item, ItemAdmin)
admin.site.register(Tag, TagAdmin)
