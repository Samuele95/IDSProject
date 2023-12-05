from django.contrib import admin
from .models import User, Shop, FidelityProgram, Catalogue

# Register your models here.

admin.site.register(User)
admin.site.register(Shop)
admin.site.register(FidelityProgram)
admin.site.register(Catalogue)