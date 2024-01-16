from django.contrib import admin
from .models import Unit, Warehouse, Counterparty, Good, Goods_in_stock, Sales, Documents, Doctype

admin.site.register(Unit)
admin.site.register(Warehouse)
admin.site.register(Counterparty)
admin.site.register(Good)
admin.site.register(Goods_in_stock)
# admin.site.register(Sales)
admin.site.register(Documents)
admin.site.register(Doctype)