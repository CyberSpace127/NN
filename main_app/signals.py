from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Barchasi
from django.db import connection

@receiver(post_save, sender=Barchasi)
def execute_query(sender, instance, **kwargs):
    id_rasxod = instance.id_rasxod.id
    id_tip_table = instance.id_tip_table.id
    id_student = instance.id_student.id if instance.id_student else None

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT fakt_pr_zatr as pr_zatr 
            FROM main_app_barchasi
            WHERE id_rasxod_id = %s
              AND id_tip_table_id = %s
              AND id_student_id = %s
              AND strftime('%%Y', data_date) = strftime('%%Y', 'now', '-1 year')
              AND strftime('%%m', data_date) = strftime('%%m', 'now');
        """, [id_rasxod, id_tip_table, id_student])
        result = cursor.fetchall()
    # Natijani ishlatish
