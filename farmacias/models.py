from django.db import models
from django.db import models

class Farmacia(models.Model):
    nombre = models.CharField(max_length=255)
    latitud = models.FloatField()
    longitud = models.FloatField()
    
    def __str__(self):
        return self.nombre
