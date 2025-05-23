"""
URL configuration for farmacia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from medicamentos.views import buscar_medicamentos
from farmacias.views import mapa_farmacias
from reportes.views import estadisticas
from reportes.views import ReportDataView,ReportView,ReportesDataView,DashboardView,ChartDataView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', buscar_medicamentos, name='buscar_medicamentos'),
    path('mapa/', mapa_farmacias, name='mapa_farmacias'),
    path('estadisticas/', estadisticas, name='estadisticas'),
    path('reportes/', ReportView.as_view(), name='reportes'),
    #path('reportes/data/', ReportDataView.as_view(), name='reportes_data'),
    #path('reportes/data/', ReportesDataView.as_view(), name='reportes_data'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/data/', ChartDataView.as_view(), name='reportes_data'),
]
