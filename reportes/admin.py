# reportes/admin.py
from django.contrib import admin
from .models import SearchTerm, SearchQuery

@admin.register(SearchTerm)
class SearchTermAdmin(admin.ModelAdmin):
    list_display = ('term','total_searches','updated_on')

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('term','timestamp','sort_option')
    list_filter  = ('sort_option','timestamp')