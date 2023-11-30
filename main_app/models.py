from django.db import models
from django.urls import reverse
# Create your models here.
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import datetime
from django.db.models import Sum
from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.db.models import ExpressionWrapper, DecimalField
from django.db.models import Model, ForeignKey, DecimalField, DateField, CASCADE, SET_NULL, Sum
from django.utils import timezone  
from django.db.models import Q
from datetime import timedelta


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "HOD"), (2, "Staff"), (3, "Student"))
    GENDER = [("M", "Male"), ("F", "Female")]
    
    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField()
    address = models.TextField()
    fcm_token = models.TextField(default="")  # For firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.last_name + ", " + self.first_name


class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)



class Course(models.Model):
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name





class Staff(models.Model):
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.admin.last_name + " " + self.admin.first_name


class Student(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True, blank=True)
    st_id = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=False)
    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name 
    
    



class Subject(models.Model):
    name = models.CharField(max_length=120)
    staff = models.ForeignKey(Staff,on_delete=models.CASCADE,)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Staff.objects.create(admin=instance)
        if instance.user_type == 3:
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.staff.save()
    if instance.user_type == 3:
        instance.student.save()







# models.py

from django.db import models

class Organizations(models.Model):
    origanizations_name = models.CharField(max_length=255)

    def __str__(self):
        return self.origanizations_name

class MTU_Company(models.Model):
    mtu_name = models.CharField(max_length=255)
    organizations = models.ForeignKey(Organizations, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.mtu_name

class Korxon(models.Model):
    korxona_name = models.CharField(max_length=255)
    mtu_company = models.ForeignKey(MTU_Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.korxona_name




class Rasxod(models.Model):
    name_rasxod = models.CharField(max_length=255, null=None)

    def __str__(self):
        return self.name_rasxod
    
    
class TipTable(models.Model):
    name_type = models.CharField(max_length=255, default='default')

    def __str__(self):
        return self.name_type

class IZ_prognoz(models.Model):
    name_prognoz = models.CharField(max_length=255, default='default')

    def __str__(self):
        return self.name_prognoz


class Barchasi(models.Model):
    id_tip_table = models.ForeignKey(TipTable, on_delete=models.CASCADE)
    id_rasxod = models.ForeignKey(Rasxod, on_delete=models.CASCADE)
    data_date = models.DateField()
    pr_zatr = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rasx_per = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prognoz_zatr = models.DecimalField(max_digits=10, decimal_places=2)
    prognoz_rasx_per =  models.DecimalField(max_digits=10, decimal_places=2)
    fakt_pr_zatr =  models.DecimalField(max_digits=10, decimal_places=2)
    fakt_rasx_per =  models.DecimalField(max_digits=10, decimal_places=2)
    всего = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prognoz_всего = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fakt_всего = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    с_начала_год = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    к_прогнозу = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    id_student = models.ForeignKey(Student, on_delete=models.CASCADE,  null=True, blank=True)
    id_staff = models.ForeignKey(Staff, on_delete=models.CASCADE,  null=True, blank=True)
    created_by_student = models.ForeignKey(Student, related_name='created_barchasi', on_delete=models.SET_NULL, blank=False, null=True)
    created_by_staff = models.ForeignKey(Staff, related_name='created_barchasi', on_delete=models.SET_NULL, blank=False, null=True)


    vsego_pr_zatr = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vsego_rasx_per = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vsego_prognoz_zatr = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vsego_prognoz_rasx_per =  models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vsego_fakt_pr_zatr =  models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vsego_fakt_rasx_per =  models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vsego_всего = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vsego_prognoz_всего = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vsego_fakt_всего = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vsego_с_начала_год =models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vsego_к_прогнозу = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def calculate_fields(self):
        if all([self.prognoz_zatr, self.prognoz_rasx_per, self.fakt_pr_zatr, self.fakt_rasx_per]):
            self.prognoz_всего = self.prognoz_zatr + self.prognoz_rasx_per
            self.fakt_всего = self.fakt_pr_zatr + self.fakt_rasx_per
            self.к_прогнозу = self.fakt_всего - self.prognoz_всего


    def save(self, *args, **kwargs):
        self.calculate_fields()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.id_rasxod} - {self.id_tip_table} - {self.id_student} - {self.id_staff}'
    


