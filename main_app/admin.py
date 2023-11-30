from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.


class UserModel(UserAdmin):
    ordering = ('email',)


from django.contrib import admin
from .models import  Rasxod, TipTable, Barchasi


@admin.register(Barchasi)
class BarchasiAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_rasxod', 'pr_zatr', 'rasx_per', 'prognoz_zatr', 'prognoz_rasx_per', 'fakt_pr_zatr', 'fakt_rasx_per', 'data_date', 'id_tip_table')
    list_filter = ('id_rasxod', 'id_tip_table', 'data_date')



admin.site.register(Rasxod)
admin.site.register(TipTable)


admin.site.register(CustomUser, UserModel)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Session)
