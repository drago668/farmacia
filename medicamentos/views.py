# medicamentos/views.py

from django.shortcuts import render
from .models import Medicamento
from django.db.models import F
from reportes.models import SearchTerm, SearchQuery
from .scraping import scrape_cruz_verde,scrape_la_rebaja

def buscar_medicamentos(request):
    # 1. Leer parámetros de la URL
    query = request.GET.get('query', '').strip()
    sort  = request.GET.get('sort', '')  
    fuente  = request.GET.get('fuente', '')    
    last = request.session.get('last_query', '')


    if query and query != last:
        Medicamento.objects.all().delete()
        scrape_cruz_verde(query)
        scrape_la_rebaja(query)
        request.session['last_query'] = query

        # Registrar o actualizar el término de búsqueda
        term_obj, created = SearchTerm.objects.get_or_create(term=query)
        term_obj.total_searches = F('total_searches') + 1
        term_obj.save()
        SearchQuery.objects.create(term=term_obj, sort_option=sort)

        # Recuperar todos los registros que coincidan con la búsqueda
        #medicamentos = Medicamento.objects.filter(nombre__icontains=query)
        request.session['last_query'] = query
    # 3. Cargar resultados de la BD
    medicamentos = Medicamento.objects.all()
    
    if fuente in ('CruzVerde', 'LaRebaja'):
        medicamentos = medicamentos.filter(fuente=fuente)
    # 4. Aplicar ordenamiento
    if sort == 'precio_asc':
        medicamentos = medicamentos.order_by('precio')
    elif sort == 'precio_desc':
        medicamentos = medicamentos.order_by('-precio')
    elif sort == 'laboratorio':
        medicamentos = medicamentos.order_by('laboratorio')
    
    # 5. Renderizar la plantilla
    return render(request, 'medicamentos/buscar.html',
    {   'medicamentos': medicamentos,
        'query': query,
        'sort': sort,
        'fuente': fuente,
    })
