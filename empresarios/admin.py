from django.contrib import admin
from .models import Empresa, Documento, Metricas


# Register your models here.
admin.site.register(Empresa)
admin.site.register(Documento)
admin.site.register(Metricas)
