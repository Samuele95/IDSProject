from django.contrib import admin
from .models import User, Shop, FidelityProgram, Catalogue, Product, Transaction

# Register your models here.

admin.site.register(User)
admin.site.register(Shop)
admin.site.register(FidelityProgram)
admin.site.register(Catalogue)
admin.site.register(Product)
admin.site.register(Transaction)