import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View, TemplateView
from .models import SearchTerm

from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count
from .models import SearchTerm, SearchQuery
from django.utils import timezone
from datetime import  timedelta
from django.db.models.functions import TruncDate


def estadisticas(request):
    # Datos ficticios
    labels = ['Paracetamol', 'Ibuprofeno', 'Amoxicilina']
    sizes = [40, 35, 25]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    ax.axis('equal')

    # Convertir gráfico a imagen
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    return render(request, 'reportes/estadisticas.html', {'chart': img_base64})

class ReportView(TemplateView):
    template_name = 'reportes/reportes.html'


    
class ReportDataView(View):
    def get(self, request):
        stats = SearchTerm.objects.order_by('-total_searches')[:10]
        data = {
            'labels': [s.term for s in stats],
            'data': [s.total_searches for s in stats],
        }
        return JsonResponse(data)
    
class ReportesDataView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Aquí obtienes tus datos tal y como ya lo haces para cada gráfico
            term_labels   = ['aspirina', 'ibuprofeno', 'paracetamol']  # ej. ['aspirina','paracetamol',...]
            term_counts   = [120, 85, 60]  # ej. [123, 98, ...]
            cat_labels    = ['analgésicos', 'antiinflamatorios']  # ej. ['analgésicos','antibióticos',...]
            cat_counts    = [180, 85]
            ts_labels     = ['2025-01', '2025-02', '2025-03']  # ej. ['2025-01','2025-02',...]
            ts_counts     = [50, 75, 90]

            return JsonResponse({
                "term_labels": term_labels,
                "term_counts": term_counts,
                "cat_labels": cat_labels,
                "cat_counts": cat_counts,
                "ts_labels": ts_labels,
                "ts_counts": ts_counts,
            })
        except Exception as e:
            # Para depurar, devuelve el mensaje de la excepción en JSON
            return JsonResponse({
                "error": str(e),
            }, status=500)





class DashboardView(TemplateView):
    template_name = 'reportes/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_searches'] = SearchQuery.objects.count()
        context['unique_terms'] = SearchTerm.objects.count()
        return context

class ChartDataView(View):
    """Devuelve JSON para Chart.js"""
    def get(self, request, *args, **kwargs):
        try:
            # Top terms
            top = SearchTerm.objects.order_by('-total_searches')[:10]
            term_labels = [t.term for t in top]
            term_counts = [t.total_searches for t in top]
            # Categories
            cats = SearchTerm.objects.values('category').annotate(count=Count('id')).order_by('-count')
            cat_labels = [c['category'] or 'Sin categoría' for c in cats]
            cat_counts = [c['count'] for c in cats]
            # Time series últimos 30 días
            since = timezone.now() - timedelta(days=30)
            qs = (SearchQuery.objects
                  .filter(timestamp__gte=since)
                  .annotate(day=TruncDate('timestamp'))
                  .values('day')
                  .annotate(count=Count('id'))
                  .order_by('day'))
            ts_labels = [x['day'].strftime('%Y-%m-%d') for x in qs]
            ts_counts = [x['count'] for x in qs]

            return JsonResponse({
                'term_labels': term_labels,
                'term_counts': term_counts,
                'cat_labels': cat_labels,
                'cat_counts': cat_counts,
                'ts_labels': ts_labels,
                'ts_counts': ts_counts,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)