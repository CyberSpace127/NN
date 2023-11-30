# resources.py
from import_export import resources
from .models import Barchasi

class BarchasiResource(resources.ModelResource):
    class Meta:
        model = Barchasi
