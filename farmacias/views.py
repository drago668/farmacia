import folium
from django.shortcuts import render
from .models import Farmacia  # Asegúrate de tener un modelo Farmacia

def mapa_farmacias(request):
    # Crear el mapa centrado en una ubicación inicial
    map = folium.Map(location=[4.8166, -74.3545], zoom_start=15)
    # Obtener todas las farmacias de la base de datos
    farmacias = Farmacia.objects.all()
    # Agregar marcadores para cada farmacia
    for farmacia in farmacias:
        print(f"Nombre: {farmacia.nombre}, Coordenadas: {farmacia.latitud}, {farmacia.longitud}")
        folium.Marker(
            location=[farmacia.latitud, farmacia.longitud],
            popup=farmacia.nombre,
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(map)
    
    # Convertir el mapa a HTML para la plantilla
    map_html = map._repr_html_()
    return render(request, 'farmacias/mapa.html', {'map': map_html})
