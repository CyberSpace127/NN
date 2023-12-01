import json
from typing import Dict, Any, List

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum

from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils import timezone
from .models import Barchasi, Student

def staff_home(request):
    staff = get_object_or_404(Staff, admin=request.user)
    total_students = Student.objects.filter(st_id=staff).count()
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()
    subjects = Subject.objects.filter(staff=staff)
    total_subject = subjects.count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name)
        attendance_list.append(attendance_count)
    context = {
        'page_title': 'RJU PANEL - ' + str(staff.admin.last_name) + ' (' + str(staff.course) + ')',
        'Enterprises': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list,
        'natija': "Natijalarni ko'rish"
    }
    return render(request, 'staff_template/home_content.html', context)


def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Take Attendance'
    }

    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt
def get_students(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        students = Student.objects.filter(
            course_id=subject.course.id, session=session)
        student_data = []
        for student in students:
            data = {
                    "id": student.id,
                    "name": student.admin.last_name + " " + student.admin.first_name
                    }
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e



@csrf_exempt
def save_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    students = json.loads(student_data)
    try:
        session = get_object_or_404(Session, id=session_id)
        subject = get_object_or_404(Subject, id=subject_id)

        # Check if an attendance object already exists for the given date and session
        attendance, created = Attendance.objects.get_or_create(session=session, subject=subject, date=date)

        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get('id'))

            # Check if an attendance report already exists for the student and the attendance object
            attendance_report, report_created = AttendanceReport.objects.get_or_create(student=student, attendance=attendance)

            # Update the status only if the attendance report was newly created
            if report_created:
                attendance_report.status = student_dict.get('status')
                attendance_report.save()

    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_update_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Update Attendance'
    }

    return render(request, 'staff_template/staff_update_attendance.html', context)


@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        student_data = []
        for attendance in attendance_data:
            data = {"id": attendance.student.admin.id,
                    "name": attendance.student.admin.last_name + " " + attendance.student.admin.first_name,
                    "status": attendance.status}
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    students = json.loads(student_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for student_dict in students:
            student = get_object_or_404(
                Student, admin_id=student_dict.get('id'))
            attendance_report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
            attendance_report.status = student_dict.get('status')
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff),
        'page_title': 'Apply for Leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "Could not apply!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Add Feedback'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_feedback.html", context)


def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None,instance=staff)
    context = {'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = staff.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                staff.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff=staff)
    sessions = Session.objects.all()
    context = {
        'page_title': 'Result Upload',
        'subjects': subjects,
        'sessions': sessions
    }
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_list')
            subject_id = request.POST.get('subject')
            test = request.POST.get('test')
            exam = request.POST.get('exam')
            student = get_object_or_404(Student, id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            try:
                data = StudentResult.objects.get(
                    student=student, subject=subject)
                data.exam = exam
                data.test = test
                data.save()
                messages.success(request, "Scores Updated")
            except:
                result = StudentResult(student=student, subject=subject, test=test, exam=exam)
                result.save()
                messages.success(request, "Scores Saved")
        except Exception as e:
            messages.warning(request, "Error Occured While Processing Form")
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_student_result(request):
    try:
        subject_id = request.POST.get('subject')
        student_id = request.POST.get('student')
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        result = StudentResult.objects.get(student=student, subject=subject)
        result_data = {
            'exam': result.exam,
            'test': result.test
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse('False')













######### CREATE VIEWS #############
@login_required
def create_rju_table(request):
    if request.method == 'POST':
        form = RjuForm(request.POST)
        if form.is_valid():
            barchasi = form.save(commit=False)
            if request.user.user_type:
                barchasi.created_by_staff = request.user.staff
                barchasi.id_staff = request.user.staff
            elif request.user.user_type:
                barchasi.created_by_student = request.user.student
                barchasi.id_student = request.user.student
            barchasi.save()
            return HttpResponseRedirect('/Rrju_table/')  # o'zgartirishingiz kerak bo'lgan joy
    else:
        form = RjuForm()

    return render(request, 'staff_template/new_table.html', {'form': form})  # o'zgartirishingiz kerak bo'lgan joy



######## Yaratilgan malumotlarni chiqarish #######


@login_required
def Rju_table(request):
    staff = get_object_or_404(Staff, admin=request.user.id)
    if request.user != staff.admin:
        return HttpResponse('Ruxsat berilmagan', status=401)
    month = request.GET.get('month')
    year = request.GET.get('year')
    if month and year:
        maqsadli_sana = f"{year}-{month}-01"  # Tanlangan yil va oydan sana yaratamiz
        table = Barchasi.objects.filter(Q(id_staff=staff) & Q(data_date=maqsadli_sana))
    else:
        # Tanlanmagan yil va oy uchun barchasi
        table = Barchasi.objects.filter(id_staff=staff)
    context = {
        'table': table,
        'page_title': "Natijalarni ko'rish"
    }
    return render(request, "staff_template/create_table.html", context)










######## RJR o'zining Korxonalarini Ko'ra olishi #########

from django.shortcuts import render
from .models import Student

@login_required
def Rju_manage_student(request):
    staff = get_object_or_404(Staff, admin=request.user.id)
    if request.user != staff.admin:
        return HttpResponse('Ruxsat berilmagan', status=401)
    table = Student.objects.filter(st_id=staff)
    context = {
        'table': table,
        'page_title': "Natijalarni ko'rish"
    }
    return render(request, "staff_template/manage_entrprises.html", context)



########### API chiqarish uchun #########
"""""
from django.db.models import Sum
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Barchasi, Student, Staff

class Rju_BarchasiDataView(APIView):
    def get(self, request):
        data = {}
        staff = Staff.objects.get(admin=request.user)
        staff_data = {}
        for id_rasxod_id in range(1, 14):  # Iterate over id_rasxod_id values from 1 to 13
            total_pr_zatr_1 = Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id, id_tip_table_id=1).aggregate(Sum('pr_zatr'))
            total_pr_zatr_2 = Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id, id_tip_table_id=2).aggregate(Sum('pr_zatr'))
            total_rasx_per_1 = Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id, id_tip_table_id=1).aggregate(Sum('rasx_per'))
            total_rasx_per_2 = Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id, id_tip_table_id=2).aggregate(Sum('rasx_per'))
            total_prognoz_zatr_1 = Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id, id_tip_table_id=1).aggregate(Sum('prognoz_zatr'))
            total_prognoz_zatr_2 = Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id, id_tip_table_id=2).aggregate(Sum('prognoz_zatr'))
            total_prognoz_rasx_per_1 = Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id, id_tip_table_id=1).aggregate(Sum('prognoz_rasx_per'))
            total_prognoz_rasx_per_2 = Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id, id_tip_table_id=2).aggregate(Sum('prognoz_rasx_per'))
            total_fakt_pr_zatr_1 = Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id, id_tip_table_id=1).aggregate(Sum('fakt_pr_zatr'))
            total_fakt_pr_zatr_2 = Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id, id_tip_table_id=2).aggregate(Sum('fakt_pr_zatr'))
            total_fakt_rasx_per_1 = Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id, id_tip_table_id=1).aggregate(Sum('fakt_rasx_per'))
            total_fakt_rasx_per_2 = Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id, id_tip_table_id=2).aggregate(Sum('fakt_rasx_per'))
            if total_pr_zatr_1['pr_zatr__sum'] is None:
                total_pr_zatr_1['pr_zatr__sum'] = 0.0
            if total_pr_zatr_2['pr_zatr__sum'] is None:
                total_pr_zatr_2['pr_zatr__sum'] = 0.0
            if total_rasx_per_1['rasx_per__sum'] is None:
                total_rasx_per_1['rasx_per__sum'] = 0.0
            if total_rasx_per_2['rasx_per__sum'] is None:
                total_rasx_per_2['rasx_per__sum'] = 0.0
            if total_prognoz_zatr_1['prognoz_zatr__sum'] is None:
                total_prognoz_zatr_1['prognoz_zatr__sum'] = 0.0
            if total_prognoz_zatr_2['prognoz_zatr__sum'] is None:
                total_prognoz_zatr_2['prognoz_zatr__sum'] = 0.0
            if total_prognoz_rasx_per_1['prognoz_rasx_per__sum'] is None:
                total_prognoz_rasx_per_1['prognoz_rasx_per__sum'] = 0.0
            if total_prognoz_rasx_per_2['prognoz_rasx_per__sum'] is None:
                total_prognoz_rasx_per_2['prognoz_rasx_per__sum'] = 0.0
            if total_fakt_pr_zatr_1['fakt_pr_zatr__sum'] is None:
                total_fakt_pr_zatr_1['fakt_pr_zatr__sum'] = 0.0
            if total_fakt_pr_zatr_2['fakt_pr_zatr__sum'] is None:
                total_fakt_pr_zatr_2['fakt_pr_zatr__sum'] = 0.0
            if total_fakt_rasx_per_1['fakt_rasx_per__sum'] is None:
                total_fakt_rasx_per_1['fakt_rasx_per__sum'] = 0.0
            if total_fakt_rasx_per_2['fakt_rasx_per__sum'] is None:
                total_fakt_rasx_per_2['fakt_rasx_per__sum'] = 0.0
            za_mes_pr_zatr = total_pr_zatr_1['pr_zatr__sum'] + total_pr_zatr_2['pr_zatr__sum']
            za_mes_rasx_per = total_rasx_per_1['rasx_per__sum'] + total_rasx_per_2['rasx_per__sum']
            prognoz_pr_zatr = total_prognoz_zatr_1['prognoz_zatr__sum'] + total_prognoz_zatr_2['prognoz_zatr__sum']
            prognoz_rasx_per = total_prognoz_rasx_per_1['prognoz_rasx_per__sum'] + total_prognoz_rasx_per_2['prognoz_rasx_per__sum']
            fakt_pr_zatr = total_fakt_pr_zatr_1['fakt_pr_zatr__sum'] + total_fakt_pr_zatr_2['fakt_pr_zatr__sum']
            fakt_rasx_per = total_fakt_rasx_per_1['fakt_rasx_per__sum'] + total_fakt_rasx_per_2['fakt_rasx_per__sum']
            za_mes_vsego = za_mes_pr_zatr + za_mes_rasx_per
            prognoz_vsego = prognoz_pr_zatr + prognoz_rasx_per
            fakt_vsego = fakt_pr_zatr + fakt_rasx_per
            с_начала_год = fakt_vsego - za_mes_vsego
            k_prognozu = fakt_vsego - prognoz_vsego
            staff_data[id_rasxod_id] = {
                'vsego_pr_zatr': za_mes_pr_zatr,
                'vsego_rasx_per': za_mes_rasx_per,
                'vsego_всего': za_mes_vsego,
                'prognoz_pr_zatr': prognoz_pr_zatr,
                'prognoz_rasx_per': prognoz_rasx_per,
                'prognoz_vsego': prognoz_vsego,
                'fakt_pr_zatr': fakt_pr_zatr,
                'fakt_rasx_per': fakt_rasx_per,
                'fakt_vsego': fakt_vsego,
                'с_начала_год': с_начала_год,
                'k_prognozu': k_prognozu
            }
            Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id).update(vsego_pr_zatr=za_mes_pr_zatr)
            Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id).update(vsego_rasx_per=za_mes_rasx_per)
            Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id).update(vsego_prognoz_zatr=prognoz_pr_zatr)
            Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id).update(vsego_prognoz_rasx_per=prognoz_rasx_per)
            Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id).update(vsego_fakt_pr_zatr=fakt_pr_zatr)
            Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id).update(vsego_fakt_rasx_per=fakt_rasx_per)
            Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id).update(vsego_всего=za_mes_vsego)
            Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id).update(vsego_prognoz_всего=prognoz_vsego)
            Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id).update(vsego_fakt_всего=fakt_vsego)
            Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id).update(vsego_с_начала_год=с_начала_год)
            Barchasi.objects.filter(created_by_staff=staff, id_rasxod_id=id_rasxod_id).update(vsego_к_прогнозу=k_prognozu)
        data[staff.id] = staff_data
        return JsonResponse(data)
"""""



@login_required
def create_staff_table(request):
    if request.method == 'POST':
        form = BarchasiForm(request.POST)
        if form.is_valid():
            barchasi = form.save(commit=False)
            if request.user.user_type:
                barchasi.created_by_staff = request.user.staff
                barchasi.id_staff = request.user.staff
            elif request.user.user_type:
                barchasi.created_by_student = request.user.student
                barchasi.id_student = request.user.student
            barchasi.save()
            return HttpResponseRedirect('/Rrju_table/')  # o'zgartirishingiz kerak bo'lgan joy
    else:
        form = BarchasiForm()

    return render(request, 'staff_template/new_table.html', {'form': form})  # o'zgartirishingiz kerak bo'lgan joy
















################## START BIG TABLE RJU #####################

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Barchasi, Staff
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import F
from django.db.models.functions import ExtractYear, ExtractMonth
from main_app.models import Student, Barchasi
from datetime import datetime




























































from django.views.generic import TemplateView

class BIG(TemplateView):
    template_name = 'Table/zadaniya.html'

######################### START BIG TABLE RJU-KORXONA ################################


######################### END BIG TABLE RJU-KORXONA ################################


@login_required
def BIG_T(request, month=None):
    staff = get_object_or_404(Staff, admin=request.user.id)
    if request.user != staff.admin:
        return HttpResponse('Ruxsat berilmagan', status=401)
    
    current_year = datetime.now().year
    current_month = datetime.now().month

    table = Barchasi.objects.filter(id_staff_id=staff).values('vsego_fakt_всего').distinct()
    table1 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table_id=1)
    table2 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table_id=2)
    perevozka = [item.fakt_всего for item in table1 if item.fakt_всего is not None]
    pvd = [item.fakt_всего for item in table2 if item.fakt_всего is not None]
    student_name = Student.objects.filter(st_id=staff)


    test = Barchasi.objects.filter(id_student__in=student_name).values('vsego_fakt_всего').distinct()
    test2 = Barchasi.objects.filter(id_student__in=student_name).values('fakt_всего').distinct()
    test3 = Barchasi.objects.filter(id_student__in=student_name).values('vsego_fakt_всего').distinct()
    table1_current_month = Barchasi.objects.filter(data_date__year=current_year, data_date__month=current_month)


    fakt_vsego_current_month = [item.fakt_всего for item in table1_current_month if item.fakt_всего is not None]

    # Initialize an empty list to hold all results


    context = {
        'table': table,
        'perevozka': perevozka,
        'pvd': pvd,
        'student_name': student_name,
        'test': test,
        'test2': test2,
        'test3': test3,
        'fakt_vsego_current_month': fakt_vsego_current_month,
        'page_title': "Natijalarni ko'rish"
    }
    
    return render(request, "zadaniya.html", context)








#==========================================================================================================#
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum

from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils import timezone
from django.db.models import Q
from .models import Barchasi, Student
from django.db.models import Max

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Student, Barchasi
from itertools import chain


@login_required
@csrf_exempt
def Rju_table(request):
    staff = get_object_or_404(Staff, admin=request.user.id)
    if request.user != staff.admin:
        return HttpResponse('Ruxsat berilmagan', status=401)

    # Foydalanuvchi tomonidan tanlangan oy va yilni olish
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    id_rasxod_values = Barchasi.objects.values_list('id_rasxod', flat=True).distinct()
    id_tip_table_values = Barchasi.objects.values_list('id_tip_table', flat=True).distinct()
    id_student_values = Barchasi.objects.values_list('id_student', flat=True).distinct()
    results = {}
    # Tanlangan oy va yil asosida ma'lumotlarni bazadan olish
    perv1 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('pr_zatr')
    perv2 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('rasx_per') 
    perv3 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('всего') 
    perv4 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('prognoz_zatr') 
    perv5 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('prognoz_rasx_per') 
    perv6 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('prognoz_всего') 
    perv7 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('fakt_pr_zatr') 
    perv8 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('fakt_rasx_per') 
    perv9 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('fakt_всего') 
    perv10 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('с_начала_год') 
    perv11 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('к_прогнозу') 

    v1 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('vsego_pr_zatr').distinct()
    v2 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('vsego_rasx_per').distinct()
    v3 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('vsego_всего').distinct()
    v4 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('vsego_prognoz_zatr').distinct()
    v5 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('vsego_prognoz_rasx_per').distinct()
    v6 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('vsego_prognoz_всего').distinct()
    v7 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('vsego_fakt_pr_zatr').distinct()
    v8 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('vsego_fakt_rasx_per').distinct()
    v9 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('vsego_fakt_всего').distinct()
    v10 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('vsego_с_начала_год').distinct()
    v11 = Barchasi.objects.filter(id_staff_id=staff, data_date__month=selected_month, data_date__year=selected_year).values('vsego_к_прогнозу').distinct()


    # oyldingi yilning malumotlarini chiqarish

    select_month = request.POST.get('month')
    select_year = request.POST.get('year')
    if select_year is not None:
        select_year = int(select_year) - 1
    perevozka1 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_pr_zatr')
    perevozka2 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_rasx_per')
    perevozka3 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=selected_month, data_date__year=select_year).values_list('fakt_всего')


    pvd1 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_pr_zatr')
    pvd2 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_rasx_per')
    pvd3 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего')



    # snachalo godu
    perv3_values = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
    perevozka3_values = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1,  data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True)
    
    perv3_v = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
    pvd3_values = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2,  data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True)


    rezult = []
    for perv, perev in zip(perv3_values, perevozka3_values):
        rezult.append(perev - perv)

    pvd = []
    for perv, perev in zip(perv3_v, pvd3_values):
        pvd.append(perev - perv)


    # perevozka_kprognozu 
    kp1 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True) 
    kp2 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_всего', flat=True) 
    
    kpragnozu = []
    for perv, perev in zip(kp2, kp1):
        kpragnozu.append(perev - perv)


    
    # vsegoning pr_zatr
    vsego_pr_zatr = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_pr_zatr', flat=True)
    vsego_pasx_per = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_pr_zatr', flat=True)
    
    vsego_pr_zatr_1 = []
    for perv, perev in zip(vsego_pr_zatr, vsego_pasx_per):
        vsego_pr_zatr_1.append(perev + perv)


    

    # vsegoning rasx_peri
    vsego_pr_zatr = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_rasx_per', flat=True)
    vsego_pasx_per = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_rasx_per', flat=True)

    vsego_fakt_rasx_per = []
    for perv, perev in zip(vsego_pr_zatr, vsego_pasx_per):
        vsego_fakt_rasx_per.append(perev + perv)

    # vsegoning zames vsegosi
    vsego_pr_zatr = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
    vsego_pasx_per = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)

    vsego_zames_всего = []
    for perv, perev in zip(vsego_pr_zatr, vsego_pasx_per):
        vsego_zames_всего.append(perev + perv)

    
    # vsego prognoz pr_zatr
    prg1 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_zatr', flat=True) 
    prg2 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_zatr', flat=True) 
    
    vsego_prognoz_pr_zatr = []
    for perv, perev in zip(prg2, prg1):
        vsego_prognoz_pr_zatr.append(perev + perv)

    
    # vsego prognoz_rasx_per
    rsx1 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_rasx_per', flat=True) 
    rsx2 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_rasx_per', flat=True) 
    
    vsego_prognoz_rasx_per = []
    for perv, perev in zip(rsx1, rsx2):
        vsego_prognoz_rasx_per.append(perev + perv)

    
    # vsego prognoz_всего 
    vpv1 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_всего', flat=True) 
    vpv2 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_всего', flat=True) 
    
    vsego_prognoz_всего = []
    for perv, perev in zip(vpv1, vpv2):
        vsego_prognoz_всего.append(perev + perv)

    # vsego fakt_przatr
    vfpz1 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_pr_zatr', flat=True) 
    vfpz2 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_pr_zatr', flat=True) 
    
    vsego_fakt_przatr = []
    for perv, perev in zip(vfpz1, vfpz2):
        vsego_fakt_przatr.append(perev + perv)

    
    # vsego fakt_rasx_per
    vfrp1 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_rasx_per', flat=True) 
    vfrp2 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_rasx_per', flat=True) 
    
    vsego_fakt_rasx_per1 = []
    for perv, perev in zip(vfrp1, vfrp2):
        vsego_fakt_rasx_per1.append(perev + perv)


    # vsego fakt_всего
    vfv1 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True) 
    vfv2 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True) 
    
    vsego_fakt_всего1 = []
    for perv, perev in zip(vfv1, vfv2):
        vsego_fakt_всего1.append(perev + perv)

    

    

    # vsego snachalo godu

    с_начала_год = [sn - gd for sn, gd in zip(vsego_fakt_всего1, vsego_zames_всего)]

    # vsego к_прогнозу

    к_прогнозу = [vg - kv for vg, kv in zip(vsego_fakt_всего1, vsego_prognoz_всего)]

     

 




    context = {
        'perevozka1': perevozka1,
        'perevozka2': perevozka2,
        'perevozka3': perevozka3,
        'rezult': rezult,
        'pvd': pvd,
        'kpragnozu': kpragnozu,
        'vsego_pr_zatr_1': vsego_pr_zatr_1,
        'vsego_fakt_rasx_per': vsego_fakt_rasx_per,
        'vsego_zames_всего': vsego_zames_всего,
        'vsego_prognoz_pr_zatr': vsego_prognoz_pr_zatr,
        'vsego_prognoz_rasx_per': vsego_prognoz_rasx_per,
        'vsego_prognoz_всего':vsego_prognoz_всего,
        'vsego_fakt_przatr': vsego_fakt_przatr,
        'vsego_fakt_rasx_per1': vsego_fakt_rasx_per1,
        'vsego_fakt_всего1': vsego_fakt_всего1,
        'с_начала_год': с_начала_год,
        'к_прогнозу': к_прогнозу,
        'pvd1': pvd1,
        'pvd2': pvd2,
        'pvd3': pvd3,
        'perv1': perv1,
        'perv2': perv2,
        'perv3': perv3,
        'perv4': perv4,
        'perv5': perv5,
        'perv6': perv6,
        'perv7': perv7,
        'perv8': perv8,
        'perv9': perv9,
        'perv10': perv10,
        'perv11': perv11,
        'v1': v1,
        'v2': v2,
        'v3': v3,
        'v4': v4,
        'v5': v5,
        'v6': v6,
        'v7': v7,
        'v8': v8,
        'v9': v9,
        'v10': v10,
        'v11': v11,
        'page_title': "Natijalarni ko'rish"
    }
    return render(request, "staff_template/create_table.html", context)





















from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Barchasi, Staff
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import F
from django.db.models.functions import ExtractYear, ExtractMonth
from main_app.models import Student, Barchasi
from datetime import datetime


@csrf_exempt
@login_required
def Rju_big_table(request, month=None):
    staff = get_object_or_404(Staff, admin=request.user.id)
    if request.user != staff.admin:
        return HttpResponse('Ruxsat berilmagan', status=401)
    
    # ozirgi yil va oy
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
   
    # o'tgan yil va oy
    select_month = request.POST.get('month')
    select_year = request.POST.get('year')
    if select_year is not None:
        select_year = int(select_year) - 1
     
    
    # 2022 o'tgan yil va oyning malumotlari
    data = [] 
   
    vsego_pr_zatr = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
    vsego_pasx_per = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
    
    vsego_zames_всего = []
    for perv, perev in zip(vsego_pr_zatr, vsego_pasx_per):
        vsego_zames_всего.append(perev + perv)
    

    # xozirgi yilning malumotlari
    vfv1 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True) 
    vfv2 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True) 
    
    vsego_fakt_всего1 = []
    for perv, perev in zip(vfv1, vfv2):
        vsego_fakt_всего1.append(perev + perv)


    # xozirgi yil va oldingi yilning raznitsasi
    с_начала_год = [sn - gd for sn, gd in zip(vsego_fakt_всего1, vsego_zames_всего)]
     
    
    # data ga 3 ta o'zgaruvchidagi barcha qiymatlarni q'shish
    data.extend([vsego_zames_всего, vsego_fakt_всего1, с_начала_год])





    ## PEREVOZKA ##
    staff_perevozka_pvd_old = Barchasi.objects.filter(id_staff_id=staff,  id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
    staff_perevozka_pvd_now = Barchasi.objects.filter(id_staff_id=staff,  id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True)
    
    
    staff_perevozka_raznitsa = []
    for perv, perev in zip(staff_perevozka_pvd_now, staff_perevozka_pvd_old):
        staff_perevozka_raznitsa.append(perev - perv)

    output = []
    for i in range(14):
        if i < len(staff_perevozka_pvd_old):
            output.append(staff_perevozka_pvd_old[i])
        if i < len(staff_perevozka_pvd_now):
            output.append(staff_perevozka_pvd_now[i])
        if i < len(staff_perevozka_raznitsa):
            output.append(staff_perevozka_raznitsa[i])
    

    ## PVD ##
    staff_pvd_old = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
    staff_pvd_now = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True)
    
    staff_pvd_raznitsa = []
    for perv, perev in zip(staff_pvd_now, staff_pvd_old):
        staff_pvd_raznitsa.append(perev - perv)

    staff_pvd = []
    for i in range(14):
        if i < len(staff_pvd_old):
            output.append(staff_pvd_old[i])
        if i < len(staff_pvd_now):
            output.append(staff_pvd_now[i])
        if i < len(staff_pvd_raznitsa):
            output.append(staff_pvd_raznitsa[i])



    ## staff vsego ##

    staff_vsego1 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True) 
    staff_vsego2 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True) 
    
    staff_vsego3 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True) 
    staff_vsego4 = Barchasi.objects.filter(id_staff_id=staff, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True) 

    staff_vsego_fakt_всего1 = []
    for perv, perev in zip(staff_vsego1, staff_vsego2):
        staff_vsego_fakt_всего1.append(perev + perv)
    
    staff_vsego_fakt_всего2 = []
    for perv, perev in zip(staff_vsego3, staff_vsego4):
        staff_vsego_fakt_всего2.append(perev + perv)

    
    staff_vsego_raznitsa = []
    for perv, perev in zip(staff_vsego_fakt_всего2, staff_vsego_fakt_всего1):
        staff_vsego_raznitsa.append(perev - perv)

    
    


    staff_vsego = []
    for i in range(14):
        if i < len(staff_vsego_fakt_всего2):
            staff_vsego.append(staff_vsego_fakt_всего2[i])
        if i < len(staff_vsego_fakt_всего1):
            staff_vsego.append(staff_vsego_fakt_всего1[i])
        if i < len(staff_vsego_raznitsa):
            staff_vsego.append(staff_vsego_raznitsa[i])









    student = Student.objects.filter(st_id=staff)
     
    # 2022 oldingi yilning fakt malumotlari 
    R_bt_vfv1 = Barchasi.objects.filter(id_student__in=student, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True) 
    R_bt_vfv2 = Barchasi.objects.filter(id_student__in=student, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True) 
    
    student_vsego_fakt_всего = []
    for perv, perev in zip(R_bt_vfv1, R_bt_vfv2):
        student_vsego_fakt_всего.append(perev + perv)

    
    ## STUDNET PEREVZOKA  ADN PVD ##

    students = Student.objects.filter(st_id=staff)
    student_perevozka_dict = {}
    for index, student in enumerate(students):
        student_perevozka = []
        student_vsego_vsego = []
        student_vsego_vsego_2 = []
        #Perevozka calculations
        student_perevozka_pvd_old = Barchasi.objects.filter(id_student=student, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
        student_perevozka_pvd_now = Barchasi.objects.filter(id_student=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True)
        # PVD calculations
        student_pvd_old = Barchasi.objects.filter(id_student=student, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
        student_pvd_now = Barchasi.objects.filter(id_student=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True)
        # VSEGO calculations
        student_vsego1 = Barchasi.objects.filter(id_student=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True) 
        student_vsego2 = Barchasi.objects.filter(id_student=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True) 
        student_vsego3 = Barchasi.objects.filter(id_student=student, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True) 
        student_vsego4 = Barchasi.objects.filter(id_student=student, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
  

        #vsego
        for perv, perev in zip(student_vsego1, student_vsego2):
            student_vsego_vsego.append(perev + perv)

        for perv, perev in zip(student_vsego3, student_vsego4):
            student_vsego_vsego_2.append(perev + perv)

        student_vsego_raznitsa = []
        for perv, perev in zip(student_vsego_vsego_2, student_vsego_vsego):
            student_vsego_raznitsa.append(perev - perv)
        
        #perevozka and pvd 
        student_perevozka_raznitsa = []
        for perv, perev in zip(student_perevozka_pvd_old, student_perevozka_pvd_now):
            student_perevozka_raznitsa.append(perev - perv)

        student_pvd_raznitsa = []
        for perv, perev in zip(student_pvd_old, student_pvd_now):
            student_pvd_raznitsa.append(perev - perv)

        for i in range(14):
            # Perevozka calculations
            if i < len(student_perevozka_pvd_old):
               student_perevozka.append(student_perevozka_pvd_old[i])
            if i < len(student_perevozka_pvd_now):
               student_perevozka.append(student_perevozka_pvd_now[i])
            if i < len(student_perevozka_raznitsa):
                student_perevozka.append(student_perevozka_raznitsa[i])

            # PVD calculations
        for i in range(14):
            if i < len(student_pvd_old):
               student_perevozka.append(student_pvd_old[i])
            if i < len(student_pvd_now):
               student_perevozka.append(student_pvd_now[i])
            if i < len(student_pvd_raznitsa):
               student_perevozka.append(student_pvd_raznitsa[i])
        
            # VSEGO calculations
        for i in range(14):
            if i < len(student_vsego_vsego_2):
                student_perevozka.append(student_vsego_vsego_2[i])
            if i < len(student_vsego_vsego):
                student_perevozka.append(student_vsego_vsego[i])
            if i < len(student_vsego_raznitsa):
                student_perevozka.append(student_vsego_raznitsa[i])

        student_perevozka_dict[student] = student_perevozka
       
         
        # print(f"Index: {index+1}")
        # print(f"Last Name: {student.admin.last_name}")
        # print(f"Student Perevozka: {student_perevozka}")

    all_sum = {}
    for student, perevozka in student_perevozka_dict.items():
        for i in range(len(perevozka)):
            if i % 3 == 2:  # agar bu uchinchi indeks bo'lsa
                all_sum[i] = 0  # uchinchi indeksdagi qiymatni hisoblamasdan 0 qo'yamiz
            else:
                if i not in all_sum:
                    all_sum[i] = perevozka[i]
                else:
                    all_sum[i] += perevozka[i]
    for i in range(0, len(all_sum), 3):  # har bir uchinchi indeks uchun
        if i+2 in all_sum:  # agar uchinchi indeks mavjud bo'lsa
             all_sum[i+2] = all_sum.get(i+1, 0) - all_sum.get(i, 0)  # ikkinchi indeksdagi qiymatni birinchi indeksdagi qiymatdan ayirib, natijani uchinchi indeksda saqlaymiz


    print(all_sum)
 
    context = {
        'all_sum': all_sum.values,
        'student_perevozka_items': student_perevozka_dict,
        'range': range(14),
        'output': output,
        'staff_pvd': staff_pvd,
        'staff_vsego': staff_vsego,
        'students': students,
        'student_perevozka': student_perevozka,
      #  'student_pvd': student_pvd,
      #  'student_vsego_sikl': student_vsego_sikl,

        'data': data,
        'vsego_zames_всего': vsego_zames_всего,
        'vsego_fakt_всего1': vsego_fakt_всего1,
        'с_начала_год': с_начала_год,
        'page_title': "Natijalarni ko'rish",
    }
    
    return render(request, "staff_template/korxona_table.html",  context)












from datetime import datetime
from .models import Barchasi
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from itertools import zip_longest




@csrf_exempt
@login_required
def ForTest(request, month=None):
    staff = get_object_or_404(Staff, admin=request.user.id)
    if request.user != staff.admin:
        return HttpResponse('Ruxsat berilmagan', status=401)
    output = []
    start_year = int(request.GET.get('start_year', datetime.now().year))
    start_month = int(request.GET.get('start_month', datetime.now().month))
    end_year = int(request.GET.get('end_year', datetime.now().year))
    end_month = int(request.GET.get('end_month', datetime.now().month))

    start_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 1)

    barchasi_list = Barchasi.objects.filter(data_date__range=[start_date, end_date])
    students = Student.objects.filter(st_id=staff)
    student_perevozka_dict = {}
    for index, student in enumerate(students):
        student_perevozka = []
        for b in barchasi_list:
            old_fakt_vsego = Barchasi.objects.filter(id_student=student, id_tip_table=1, data_date__year=start_year-1, data_date__month=start_month).values_list('fakt_всего', flat=True)
            now_fakt_vsego = Barchasi.objects.filter(id_student=student, id_tip_table=1, data_date__year=start_year, data_date__month=start_month).values_list('fakt_всего', flat=True)
            student_perevozka_raznitsa = []
        for perv, perev in zip(old_fakt_vsego, now_fakt_vsego):
            student_perevozka_raznitsa.append(perev - perv)
        


        for i in range(14):
            # Perevozka calculations
            if i < len(old_fakt_vsego):
                student_perevozka.append(old_fakt_vsego[i])
            if i < len(now_fakt_vsego):
                student_perevozka.append(now_fakt_vsego[i])
            if i < len(student_perevozka_raznitsa):
                student_perevozka.append(student_perevozka_raznitsa[i])


        student_perevozka_dict[student] = student_perevozka
    all_sum = {}
    for student, perevozka in student_perevozka_dict.items():
        for i in range(len(perevozka)):
            if i % 3 == 2:  # agar bu uchinchi indeks bo'lsa
                all_sum[i] = 0  # uchinchi indeksdagi qiymatni hisoblamasdan 0 qo'yamiz
            else:
                if i not in all_sum:
                    all_sum[i] = perevozka[i]
                else:
                    all_sum[i] += perevozka[i]
    for i in range(0, len(all_sum), 3):  # har bir uchinchi indeks uchun
        if i+2 in all_sum:  # agar uchinchi indeks mavjud bo'lsa
            all_sum[i+2] = all_sum.get(i+1, 0) - all_sum.get(i, 0)  # ikkinchi indeksdagi qiymatni birinchi indeksdagi qiymatdan ayirib, natijani uchinchi indeksda saqlaymiz
    

    print(all_sum)
 
    context = {
        'all_sum': all_sum.values,
        'student_perevozka_items': student_perevozka_dict,
        'range': range(14),
        'output': output,
        'students': students,
        'student_perevozka': student_perevozka,
        'page_title': "Natijalarni ko'rish",
    }
    
    return render(request, "staff_template/for_test.html",  context)




from rest_framework import serializers, viewsets, filters
from .models import Barchasi

class BarchasiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barchasi
        fields = '__all__'

from django_filters.rest_framework import DateFromToRangeFilter
from django_filters.rest_framework import DjangoFilterBackend

class BarchasiViewSet(viewsets.ModelViewSet):
    queryset = Barchasi.objects.all()
    serializer_class = BarchasiSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'data_date': ['gte', 'lte'],
    }


        






    #     # xozirgi yil va oy uchun 
    # nstart_date = datetime.now() - timedelta(days=365)
    # nend_date = datetime.now()
    #     # oldingi yil va oy uchun  
    # ostart_date = datetime.now() - timedelta(days=730)
    # oend_date = datetime.now() - timedelta(days=365)

    # students = Student.objects.filter(st_id=staff)
    # student_perevozka_dict = {}
    # for index, student in enumerate(students):
    #     student_perevozka = []
    #     student_vsego_vsego = []
    #     student_vsego_vsego_2 = []
    #     #Perevozka calculations
    #     student_perevozka_pvd_old = Barchasi.objects.filter(id_student=student, id_tip_table=1, data_date__range=(ostart_date, oend_date)).values_list('fakt_всего', flat=True)
    #     student_perevozka_pvd_now = Barchasi.objects.filter(id_student=student, id_tip_table=1, data_date__range=(nstart_date, nend_date)).values_list('fakt_всего', flat=True)
    #      # PVD calculations
    #     student_pvd_old = Barchasi.objects.filter(id_student=student, id_tip_table=2, data_date__range=(ostart_date, oend_date)).values_list('fakt_всего', flat=True)
    #     student_pvd_now = Barchasi.objects.filter(id_student=student, id_tip_table=2, data_date__range=(nstart_date, nend_date)).values_list('fakt_всего', flat=True)
    #     # VSEGO calculations
    #     student_vsego1 = Barchasi.objects.filter(id_student=student, id_tip_table=1, data_date__range=(nstart_date, nend_date)).values_list('fakt_всего', flat=True) 
    #     student_vsego2 = Barchasi.objects.filter(id_student=student, id_tip_table=2, data_date__range=(nstart_date, nend_date)).values_list('fakt_всего', flat=True) 
    #     student_vsego3 = Barchasi.objects.filter(id_student=student, id_tip_table=1, data_date__range=(ostart_date, oend_date)).values_list('fakt_всего', flat=True) 
    #     student_vsego4 = Barchasi.objects.filter(id_student=student, id_tip_table=2, data_date__range=(ostart_date, oend_date)).values_list('fakt_всего', flat=True)
  

        # #vsego
        # for perv, perev in zip(student_vsego1, student_vsego2):
        #     student_vsego_vsego.append(perev + perv)

        # for perv, perev in zip(student_vsego3, student_vsego4):
        #     student_vsego_vsego_2.append(perev + perv)

        # student_vsego_raznitsa = []
        # for perv, perev in zip(student_vsego_vsego_2, student_vsego_vsego):
        #     student_vsego_raznitsa.append(perev - perv)

        # #perevozka and pvd 
        # student_perevozka_raznitsa = []
        # for perv, perev in zip(student_perevozka_pvd_old, student_perevozka_pvd_now):
        #     student_perevozka_raznitsa.append(perev - perv)
        # student_pvd_raznitsa = []
        # for perv, perev in zip(student_pvd_old, student_pvd_now):
        #     student_pvd_raznitsa.append(perev - perv)

        # for i in range(14):
        #     # Perevozka calculations
        #     if i < len(student_perevozka_pvd_old):
        #         student_perevozka.append(student_perevozka_pvd_old[i])
        #     if i < len(student_perevozka_pvd_now):
        #         student_perevozka.append(student_perevozka_pvd_now[i])
        #     if i < len(student_perevozka_raznitsa):
        #             student_perevozka.append(student_perevozka_raznitsa[i])
        #     # PVD calculations
        # for i in range(14):
        #     if i < len(student_pvd_old):
        #        student_perevozka.append(student_pvd_old[i])
        #     if i < len(student_pvd_now):
        #        student_perevozka.append(student_pvd_now[i])
        #     if i < len(student_pvd_raznitsa):
        #        student_perevozka.append(student_pvd_raznitsa[i])
        
        #     # VSEGO calculations
        # for i in range(14):
        #     if i < len(student_vsego_vsego_2):
        #         student_perevozka.append(student_vsego_vsego_2[i])
        #     if i < len(student_vsego_vsego):
        #         student_perevozka.append(student_vsego_vsego[i])
        #     if i < len(student_vsego_raznitsa):
        #         student_perevozka.append(student_vsego_raznitsa[i])
        
    #     student_perevozka_dict[student] = student_perevozka
    # all_sum = {}
    # for student, perevozka in student_perevozka_dict.items():
    #     for i in range(len(perevozka)):
    #         if i % 3 == 2:  # agar bu uchinchi indeks bo'lsa
    #             all_sum[i] = 0  # uchinchi indeksdagi qiymatni hisoblamasdan 0 qo'yamiz
    #         else:
    #             if i not in all_sum:
    #                 all_sum[i] = perevozka[i]
    #             else:
    #                 all_sum[i] += perevozka[i]
    # for i in range(0, len(all_sum), 3):  # har bir uchinchi indeks uchun
    #     if i+2 in all_sum:  # agar uchinchi indeks mavjud bo'lsa
    #         all_sum[i+2] = all_sum.get(i+1, 0) - all_sum.get(i, 0)  # ikkinchi indeksdagi qiymatni birinchi indeksdagi qiymatdan ayirib, natijani uchinchi indeksda saqlaymiz


    # print(all_sum)
 
    # context = {
    #     'all_sum': all_sum.values,
    #     'student_perevozka_items': student_perevozka_dict,
    #     'range': range(14),
    #     'output': output,
    #     'students': students,
    #     'student_perevozka': student_perevozka,
    #     'page_title': "Natijalarni ko'rish",
    # }
    
    # return render(request, "staff_template/for_test.html",  context)








########################### DRF API ###########################
