from django.contrib import admin
from .models import Medicamento

# Register your models here.}
@admin.register(Medicamento)
class SearchTermAdmin(admin.ModelAdmin):
    list_display = ('nombre','precio','laboratorio','sintomas','url')
