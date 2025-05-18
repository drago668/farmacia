from django.db import models

# Create your models here.

from django.db import models

class Medicamento(models.Model):
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    laboratorio = models.CharField(max_length=255)
    sintomas = models.TextField()
    url = models.URLField()
    imagen_url = models.URLField(blank=True)  # nuevo campo
    fuente     = models.CharField(max_length=50, default='CruzVerde')    # ← nuevo


    def __str__(self):
        return self.nombre
