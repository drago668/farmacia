from django.contrib import admin
from .models import Farmacia

@admin.register(Farmacia)
class FarmaciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'latitud', 'longitud')