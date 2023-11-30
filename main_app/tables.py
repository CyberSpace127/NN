# myapp/tables.py
import django_tables2 as tables
from .models import Barchasi

class MyModelTable(tables.Table):
    class Meta:
        model = Barchasi
