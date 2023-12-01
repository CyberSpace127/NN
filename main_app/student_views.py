import json
import math
from datetime import datetime

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from requests import Request
from .models import Organizations, MTU_Company, Korxon
from .forms import *
from .models import *
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncDate




def student_home(request):
    student = get_object_or_404(Student, admin=request.user)
    barchasi_dates = Barchasi.objects.filter(id_student=student.id).dates('data_date', 'day')
    for date in barchasi_dates:
        print(f"Student {student.admin.last_name}: {date} kuni 1 ta malumot bor.")
    total_subject = Subject.objects.filter(course=student.course).count()
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    total_present = AttendanceReport.objects.filter(student=student, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    subject_name = []
    data_present = []
    data_absent = []
    subjects = Subject.objects.filter(course=student.course)
    for subject in subjects:
        attendance = Attendance.objects.filter(subject=subject)
        present_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=True, student=student).count()
        absent_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=False, student=student).count()
        subject_name.append(subject.name)
        data_present.append(present_count)
        data_absent.append(absent_count)
    context = {
        'barchasi_dates': barchasi_dates,
        'total_attendance': total_attendance,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'total_subject': total_subject,
        'subjects': subjects,
        'data_present': data_present,
        'data_absent': data_absent,
        'data_name': subject_name,
        'page_title': 'Boshqaruv paneli'

    }
    return render(request, 'student_template/home_content.html', context)


@ csrf_exempt
def student_view_attendance(request):
    student = get_object_or_404(Student, admin=request.user)
    if request.method != 'POST':
        course = get_object_or_404(Course, id=student.course.id)
        context = {
            'subjects': Subject.objects.filter(course=course),
            'page_title': 'View Attendance'
        }
        return render(request, 'student_template/student_view_attendance.html', context)
    else:
        subject_id = request.POST.get('subject')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            subject = get_object_or_404(Subject, id=subject_id)
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            attendance = Attendance.objects.filter(
                date__range=(start_date, end_date), subject=subject)
            attendance_reports = AttendanceReport.objects.filter(
                attendance__in=attendance, student=student)
            json_data = []
            for report in attendance_reports:
                data = {
                    "date":  str(report.attendance.date),
                    "status": report.status
                }
                json_data.append(data)
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception as e:
            return None


def student_apply_leave(request):
    form = LeaveReportStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStudent.objects.filter(student=student),
        'page_title': 'Apply for leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('student_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_apply_leave.html", context)


def student_feedback(request):
    form = FeedbackStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStudent.objects.filter(student=student),
        'page_title': 'Student Feedback'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Feedback submitted for review")
                return redirect(reverse('student_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_feedback.html", context)


def student_view_profile(request):
    student = get_object_or_404(Student, admin=request.user)
    form = StudentEditForm(request.POST or None, request.FILES or None,
                           instance=student)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = student.admin
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
                student.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('student_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "student_template/student_view_profile.html", context)


@csrf_exempt
def student_fcmtoken(request):
    token = request.POST.get('token')
    student_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        student_user.fcm_token = token
        student_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def student_view_notification(request):
    student = get_object_or_404(Student, admin=request.user)
    notifications = NotificationStudent.objects.filter(student=student)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "student_template/student_view_notification.html", context)


def student_view_result(request):
    student = get_object_or_404(Student, admin=request.user)
    results = StudentResult.objects.filter(student=student)
    context = {
        'results': results,
        'page_title': "View Results"
    }
    return render(request, "student_template/student_view_result.html", context)




def organizations_view(request, organizations_id):
    organizations = Organizations.objects.get(pk=organizations_id)
    mtu_companies = MTU_Company.objects.filter(organizations=organizations)
    korxons = Korxon.objects.filter(mtu_company__in=mtu_companies)

    context = {
        'organizations': organizations,
        'mtu_companies': mtu_companies,
        'korxons': korxons,
    }

    return render(request, 'student_template/org.html', context)


# ============================================= NEW =========================================== #

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Barchasi
from django.db.models import Sum
from django.shortcuts import render
from datetime import datetime
from main_app.models import Barchasi

# List view for Barchasi
#class MiniTable(ListView):
#    model = Barchasi
#    template_name = 'bigtable.html'
#    context_object_name = 'barchasi_objects'

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
def MiniTable(request):
    student = get_object_or_404(Student, admin=request.user.id)
    if request.user != student.admin:
        return HttpResponse('Ruxsat berilmagan', status=401)

    # Foydalanuvchi tomonidan tanlangan oy va yilni olish
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    id_rasxod_values = Barchasi.objects.values_list('id_rasxod', flat=True).distinct()
    id_tip_table_values = Barchasi.objects.values_list('id_tip_table', flat=True).distinct()
    id_student_values = Barchasi.objects.values_list('id_student', flat=True).distinct()
    results = {}
    # Tanlangan oy va yil asosida ma'lumotlarni bazadan olish
    # PEREVOZKA
    perv1 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values('pr_zatr')
    perv2 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values('rasx_per') 
    perv3 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values('всего') 
    perv4 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values('prognoz_zatr') 
    perv5 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values('prognoz_rasx_per') 
    perv6 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values('prognoz_всего') 
    perv7 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values('fakt_pr_zatr') 
    perv8 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values('fakt_rasx_per') 
    perv9 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values('fakt_всего') 
    perv10 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values('с_начала_год') 
    perv11 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values('к_прогнозу')
    # PVD
    pv1 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values('pr_zatr')
    pv2 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values('rasx_per') 
    pv3 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values('всего') 
    pv4 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values('prognoz_zatr') 
    pv5 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values('prognoz_rasx_per') 
    pv6 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values('prognoz_всего') 
    pv7 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values('fakt_pr_zatr') 
    pv8 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values('fakt_rasx_per') 
    pv9 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values('fakt_всего') 
    pv10 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values('с_начала_год') 
    pv11 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values('к_прогнозу')  

    v1 = Barchasi.objects.filter(id_student_id=student, data_date__month=selected_month, data_date__year=selected_year).values('vsego_pr_zatr').distinct()
    v2 = Barchasi.objects.filter(id_student_id=student, data_date__month=selected_month, data_date__year=selected_year).values('vsego_rasx_per').distinct()
    v3 = Barchasi.objects.filter(id_student_id=student, data_date__month=selected_month, data_date__year=selected_year).values('vsego_всего').distinct()
    v4 = Barchasi.objects.filter(id_student_id=student, data_date__month=selected_month, data_date__year=selected_year).values('vsego_prognoz_zatr').distinct()
    v5 = Barchasi.objects.filter(id_student_id=student, data_date__month=selected_month, data_date__year=selected_year).values('vsego_prognoz_rasx_per').distinct()
    v6 = Barchasi.objects.filter(id_student_id=student, data_date__month=selected_month, data_date__year=selected_year).values('vsego_prognoz_всего').distinct()
    v7 = Barchasi.objects.filter(id_student_id=student, data_date__month=selected_month, data_date__year=selected_year).values('vsego_fakt_pr_zatr').distinct()
    v8 = Barchasi.objects.filter(id_student_id=student, data_date__month=selected_month, data_date__year=selected_year).values('vsego_fakt_rasx_per').distinct()
    v9 = Barchasi.objects.filter(id_student_id=student, data_date__month=selected_month, data_date__year=selected_year).values('vsego_fakt_всего').distinct()
    v10 = Barchasi.objects.filter(id_student_id=student, data_date__month=selected_month, data_date__year=selected_year).values('vsego_с_начала_год').distinct()
    v11 = Barchasi.objects.filter(id_student_id=student, data_date__month=selected_month, data_date__year=selected_year).values('vsego_к_прогнозу').distinct()
    # oyldingi yilning malumotlarini chiqarish

    select_month = request.POST.get('month')
    select_year = request.POST.get('year')
    if select_year is not None:
        select_year = int(select_year) - 1
    perevozka1 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_pr_zatr')
    perevozka2 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_rasx_per')
    perevozka3 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=select_year).values_list('fakt_всего')


    pvd1 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_pr_zatr')
    pvd2 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_rasx_per')
    pvd3 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=select_year).values_list('fakt_всего')



    # snachalo godu
    perv3_values = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
    perevozka3_values = Barchasi.objects.filter(id_student_id=student, id_tip_table=1,  data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True)
    
    perv3_v = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
    pvd3_values = Barchasi.objects.filter(id_student_id=student, id_tip_table=2,  data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True)


    rezult = []
    for perv, perev in zip(perv3_values, perevozka3_values):
        rezult.append(perev - perv)

    pvd = []
    for perv, perev in zip(perv3_v, pvd3_values):
        pvd.append(perev - perv)


    # perevozka_kprognozu 
    kp1 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True) 
    kp2 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_всего', flat=True) 
    
    kpragnozu = []
    for perv, perev in zip(kp2, kp1):
        kpragnozu.append(perev - perv)


    
    # vsegoning pr_zatr
    vsego_pr_zatr = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_pr_zatr', flat=True)
    vsego_pasx_per = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_pr_zatr', flat=True)
    
    vsego_pr_zatr_1 = []
    for perv, perev in zip(vsego_pr_zatr, vsego_pasx_per):
        vsego_pr_zatr_1.append(perev + perv)




    # vsegoning rasx_peri
    vsego_pr_zatr = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_rasx_per', flat=True)
    vsego_pasx_per = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_rasx_per', flat=True)

    vsego_fakt_rasx_per = []
    for perv, perev in zip(vsego_pr_zatr, vsego_pasx_per):
        vsego_fakt_rasx_per.append(perev + perv)

    # vsegoning zames vsegosi
    vsego_pr_zatr = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
    vsego_pasx_per = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)

    vsego_zames_всего = []
    for perv, perev in zip(vsego_pr_zatr, vsego_pasx_per):
        vsego_zames_всего.append(perev + perv)

    
    # vsego prognoz pr_zatr
    prg1 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_zatr', flat=True) 
    prg2 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_zatr', flat=True) 
    
    vsego_prognoz_pr_zatr = []
    for perv, perev in zip(prg2, prg1):
        vsego_prognoz_pr_zatr.append(perev + perv)

    
    # vsego prognoz_rasx_per
    rsx1 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_rasx_per', flat=True) 
    rsx2 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_rasx_per', flat=True) 
    
    vsego_prognoz_rasx_per = []
    for perv, perev in zip(rsx1, rsx2):
        vsego_prognoz_rasx_per.append(perev + perv)

    
    # vsego prognoz_всего 
    vpv1 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_всего', flat=True) 
    vpv2 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('prognoz_всего', flat=True) 
    
    vsego_prognoz_всего = []
    for perv, perev in zip(vpv1, vpv2):
        vsego_prognoz_всего.append(perev + perv)

    # vsego fakt_przatr
    vfpz1 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_pr_zatr', flat=True) 
    vfpz2 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_pr_zatr', flat=True) 
    
    vsego_fakt_przatr = []
    for perv, perev in zip(vfpz1, vfpz2):
        vsego_fakt_przatr.append(perev + perv)

    
    # vsego fakt_rasx_per
    vfrp1 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_rasx_per', flat=True) 
    vfrp2 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_rasx_per', flat=True) 
    
    vsego_fakt_rasx_per1 = []
    for perv, perev in zip(vfrp1, vfrp2):
        vsego_fakt_rasx_per1.append(perev + perv)


    # vsego fakt_всего
    vfv1 = Barchasi.objects.filter(id_student_id=student, id_tip_table=1, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True) 
    vfv2 = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True) 
    
    vsego_fakt_всего1 = []
    for perv, perev in zip(vfv1, vfv2):
        vsego_fakt_всего1.append(perev + perv)

    

    

    # vsego snachalo godu

    с_начала_год = [sn - gd for sn, gd in zip(vsego_fakt_всего1, vsego_zames_всего)]

    # vsego к_прогнозу

    к_прогнозу = [vg - kv for vg, kv in zip(vsego_fakt_всего1, vsego_prognoz_всего)]

    # PVD-Snachalo goda
    now_pvd_snachala_goda = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=selected_month, data_date__year=selected_year).values_list('fakt_всего', flat=True)
    old_pvd_snachala_goda = Barchasi.objects.filter(id_student_id=student, id_tip_table=2, data_date__month=select_month, data_date__year=select_year).values_list('fakt_всего', flat=True)
    
    pvd_с_начала_год = [sn - gd for sn, gd in zip(now_pvd_snachala_goda, old_pvd_snachala_goda)]



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
        'pvd_с_начала_год': pvd_с_начала_год,
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
        'pv1': pv1,
        'pv2': pv2,
        'pv3': pv3,
        'pv4': pv4,
        'pv5': pv5,
        'pv6': pv6,
        'pv7': pv7,
        'pv8': pv8,
        'pv9': pv9,
        'pv10': pv10,
        'pv11': pv11,
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
    return render(request, "te.html", context)



















def get_za_mes_pr_zatr(self):
    current_year = timezone.now().year
    current_month = timezone.now().month
    last_year = current_year - 1

    barchasi = Barchasi.objects.filter(
        data_date__year=last_year,
        data_date__month=current_month
    ).values('id_rasxod_id', 'id_tip_table_id', 'id_student_id', 'fakt_pr_zatr')

    pr_zatr = [(item['id_rasxod_id'], item['id_tip_table_id'], item['id_student_id'], item['fakt_pr_zatr']) for item in barchasi]
        
    return pr_zatr




























from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Barchasi, Student
from .serializers import BarchasiSerializer

class MiniTableView(APIView):
    def get(self, request, format=None):
        student = get_object_or_404(Student, admin=request.user.id)
        if request.user != student.admin:
            return HttpResponse('Ruxsat berilmagan', status=401)

        # Get all distinct Barchasi objects
        table = Barchasi.objects.all().distinct()

        serializer = BarchasiSerializer(table, many=True)
        return Response(serializer.data)







from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# List view for Barchasi
class BarchasiListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Barchasi
    template_name = 'te.html'
    context_object_name = 'barchasi_objects'
    def test_func(self):
        obj = self.get_queryset()
        return any(o.id_student == self.request.user for o in obj)

# Detail view for Barchasi
class BarchasiDetailView(DetailView):
    model = Barchasi
    template_name = 'sidebar/barchasi_detail.html'
    context_object_name = 'barchasi'

# Create view for Barchasi
from django.urls import reverse_lazy
from .models import Barchasi
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import Barchasi
from .forms import BarchasiForm

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Barchasi
from .forms import BarchasiForm
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Barchasi, Student, Staff
from .forms import BarchasiForm


@login_required
def create(request):
    if request.method == 'POST':
        form = BarchasiForm(request.POST)
        if form.is_valid():
            barchasi = form.save(commit=False)
            if request.user.user_type:
                barchasi.created_by_student = request.user.student
                barchasi.id_student = request.user.student
            elif request.user.user_type:
                barchasi.created_by_staff = request.user.staff
                barchasi.id_staff = request.user.staff
            barchasi.save()
            return HttpResponseRedirect('/student/Mini_Table/')  # o'zgartirishingiz kerak bo'lgan joy
    else:
        form = BarchasiForm()

    return render(request, 'sidebar/barchasi_form.html', {'form': form})  # o'zgartirishingiz kerak bo'lgan joy

    


# Update view for Barchasi
from django.shortcuts import render, get_object_or_404, redirect
from .models import Barchasi
from .forms import BarchasiForm  # Replace with the actual form

def barchasi_update(request, pk):
    barchasi = get_object_or_404(Barchasi, pk=pk)
    
    if request.method == "POST":
        form = BarchasiForm(request.POST, instance=barchasi)
        if form.is_valid():
            barchasi = form.save()
            return redirect('barchasi_detail', pk=barchasi.pk)  # Redirect to the detail view
    else:
        form = BarchasiForm(instance=barchasi)
    
    return render(request, 'sidebar/barchasi_form.html', {'form': form})

# Delete view for Barchasi
class BarchasiDeleteView(DeleteView):
    model = Barchasi
    template_name = 'sidebar/barchasi_confirm_delete.html'
    success_url = reverse_lazy('barchasi_list')












# ========================================= XISOBLASH ==================================== # 


# views.py



from django.shortcuts import render, get_object_or_404, redirect
from .models import Rasxod, TipTable
from .forms import RasxodForm, TipTableForm  # You'll need to create these forms as well




def rasxod_list(request):
    rasxods = Rasxod.objects.all()
    return render(request, 'Tip_ras/rasxod_list.html', {'rasxods': rasxods})

def rasxod_detail(request, pk):
    rasxod = get_object_or_404(Rasxod, pk=pk)
    return render(request, 'Tip_ras/rasxod_detail.html', {'rasxod': rasxod})

def rasxod_create(request):
    if request.method == 'POST':
        form = RasxodForm(request.POST)
        if form.is_valid():
            rasxod = form.save()
            return redirect('rasxod_detail', pk=rasxod.pk)
    else:
        form = RasxodForm()
    return render(request, 'Tip_ras/rasxod_form.html', {'form': form})

def rasxod_update(request, pk):
    rasxod = get_object_or_404(Rasxod, pk=pk)
    if request.method == 'POST':
        form = RasxodForm(request.POST, instance=rasxod)
        if form.is_valid():
            rasxod = form.save()
            return redirect('rasxod_detail', pk=rasxod.pk)
    else:
        form = RasxodForm(instance=rasxod)
    return render(request, 'Tip_ras/rasxod_form.html', {'form': form})

def rasxod_delete(request, pk):
    rasxod = get_object_or_404(Rasxod, pk=pk)
    rasxod.delete()
    return redirect('rasxod_list')














#################################################################################################################



from django.shortcuts import render, get_object_or_404, redirect
from .models import TipTable
from .forms import TipTableForm # You'll need to create this form if it doesn't exist yet




# List view for Barchasi
#class tiptable_list(ListView):
#    model = TipTable
#    template_name = 'Tip_ras/tiptable_list.html'
#    context_object_name = 'tiptables'


def tiptable_list(request):
    tiptable = TipTable.objects.all()
    return render(request, 'Tip_ras/tiptable_list.html', {'tiptable': tiptable})
#def tiptable_list(request):
#    models = TipTable
#    tiptables = TipTable.objects.all()
#    return render(request, 'Tip_ras/tiptable_list.html', {'tiptables': tiptables})

def tiptable_detail(request, pk):
    tiptable = get_object_or_404(TipTable, pk=pk)
    return render(request, 'Tip_ras/tiptable_detail.html', {'tiptable': tiptable})

def tiptable_create(request):
    if request.method == 'POST':
        form = TipTableForm(request.POST)
        if form.is_valid():
            tiptable = form.save()
            return redirect('tiptable_detail', pk=tiptable.pk)
    else:
        form = TipTableForm()
    return render(request, 'Tip_ras/tiptable_form.html', {'form': form})

def tiptable_update(request, pk):
    tiptable = get_object_or_404(TipTable, pk=pk)
    if request.method == 'POST':
        form = TipTableForm(request.POST, instance=tiptable)
        if form.is_valid():
            tiptable = form.save()
            return redirect('tiptable_detail', pk=tiptable.pk)
    else:
        form = TipTableForm(instance=tiptable)
    return render(request, 'Tip_ras/tiptable_form.html', {'form': form})

def tiptable_delete(request, pk):
    tiptable = get_object_or_404(TipTable, pk=pk)
    tiptable.delete()
    return redirect('tiptable_list')






from django.shortcuts import render, get_object_or_404, redirect
from .models import IZ_prognoz
from .forms import IZPrognozForm

# Create your views here.
def iz_prognoz_list(request):
    prognozs = IZ_prognoz.objects.all()
    return render(request, 'prognoz/iz_prognoz_list.html', {'prognozs': prognozs})

def iz_prognoz_detail(request, pk):
    prognoz = get_object_or_404(IZ_prognoz, pk=pk)
    return render(request, 'prognoz/iz_prognoz_detail.html', {'prognoz': prognoz})

def iz_prognoz_new(request):
    if request.method == "POST":
        form = IZPrognozForm(request.POST)
        if form.is_valid():
            prognoz = form.save(commit=False)
            prognoz.save()
            return redirect('iz_prognoz_detail', pk=prognoz.pk)
    else:
        form = IZPrognozForm()
    return render(request, 'prognoz/iz_prognoz_edit.html', {'form': form})

def iz_prognoz_edit(request, pk):
    prognoz = get_object_or_404(IZ_prognoz, pk=pk)
    if request.method == "POST":
        form = IZPrognozForm(request.POST, instance=prognoz)
        if form.is_valid():
            prognoz = form.save(commit=False)
            prognoz.save()
            return redirect('iz_prognoz_detail', pk=prognoz.pk)
    else:
        form = IZPrognozForm(instance=prognoz)
    return render(request, 'prognoz/iz_prognoz_edit.html', {'form': form})

def iz_prognoz_delete(request, pk):
    prognoz = get_object_or_404(IZ_prognoz, pk=pk)
    if request.method == "POST":
        prognoz.delete()
        return redirect('iz_prognoz_list')
    return render(request, 'prognoz/iz_prognoz_confirm_delete.html', {'prognoz': prognoz})


from django.shortcuts import render

def Space(request):
    return render(request, 'prognoz/test.html')




from django.shortcuts import render
from .models import Barchasi

def kpf(request):
    try:
        barchasi_objects = Barchasi.objects.all()

        for barchasi in barchasi_objects:
            # Ensure the fields are not None before performing calculations
            if all([barchasi.pr_zatr, barchasi.rasx_per, barchasi.prognoz_zatr, barchasi.prognoz_rasx_per, barchasi.fakt_pr_zatr, barchasi.fakt_rasx_per]):
                # Calculate the total
                barchasi.всего = barchasi.pr_zatr + barchasi.rasx_per

                # Calculate the total for prognoz
                barchasi.prognoz_всего = barchasi.prognoz_zatr + barchasi.prognoz_rasx_per

                # Calculate the total for fakt
                barchasi.fakt_всего = barchasi.fakt_pr_zatr + barchasi.fakt_rasx_per

                # Calculate k_prognozu
                barchasi.к_прогнозу = barchasi.fakt_всего - barchasi.prognoz_всего

                # Calculate nachala_god
                barchasi.с_начала_год = barchasi.fakt_всего - barchasi.всего

                # Save the changes
                barchasi.save()
            else:
                print(f"Skipping object with id {barchasi.id} due to None fields.")

    except Exception as e:
        print(f"An error occurred: {e}")

    return render(request, 'sidebar/barchasi_list.html', {'barchasi_objects': barchasi_objects})







#================= vsegosi ===================#

# List view for Barchasi

 
def your_view(request):
    start_of_month = datetime.now().replace(day=1)
    end_of_month = datetime.now()

    id_rasxod_values = Barchasi.objects.values_list('id_rasxod', flat=True).distinct()
    results = {}

    for id_rasxod in id_rasxod_values:
        queryset1 = Barchasi.objects.filter(id_rasxod_id=id_rasxod, id_tip_table_id=1, data_date__range=[start_of_month, end_of_month])
        queryset2 = Barchasi.objects.filter(id_rasxod_id=id_rasxod, id_tip_table_id=2, data_date__range=[start_of_month, end_of_month])

        sum_pr_zatr_1 = queryset1.aggregate(sum_pr_zatr=Sum('pr_zatr'))['sum_pr_zatr'] or 0
        sum_pr_zatr_2 = queryset2.aggregate(sum_pr_zatr=Sum('pr_zatr'))['sum_pr_zatr'] or 0

        sum_rasx_per_1 = queryset1.aggregate(sum_rasx_per=Sum('rasx_per'))['sum_rasx_per'] or 0
        sum_rasx_per_2 = queryset2.aggregate(sum_rasx_per=Sum('rasx_per'))['sum_rasx_per'] or 0

        sum_prognoz_zatr_1 = queryset1.aggregate(sum_prognoz_zatr=Sum('prognoz_zatr'))['sum_prognoz_zatr'] or 0
        sum_prognoz_zatr_2 = queryset2.aggregate(sum_prognoz_zatr=Sum('prognoz_zatr'))['sum_prognoz_zatr'] or 0

        sum_prognoz_rasx_per_1 = queryset1.aggregate(sum_prognoz_rasx_per=Sum('prognoz_rasx_per'))['sum_prognoz_rasx_per'] or 0
        sum_prognoz_rasx_per_2 = queryset2.aggregate(sum_prognoz_rasx_per=Sum('prognoz_rasx_per'))['sum_prognoz_rasx_per'] or 0

        sum_fakt_pr_zatr_1 = queryset1.aggregate(sum_fakt_pr_zatr=Sum('fakt_pr_zatr'))['sum_fakt_pr_zatr'] or 0
        sum_fakt_pr_zatr_2 = queryset2.aggregate(sum_fakt_pr_zatr=Sum('fakt_pr_zatr'))['sum_fakt_pr_zatr'] or 0

        sum_fakt_rasx_per_1 = queryset1.aggregate(sum_fakt_rasx_per=Sum('fakt_rasx_per'))['sum_fakt_rasx_per'] or 0
        sum_fakt_rasx_per_2 = queryset2.aggregate(sum_fakt_rasx_per=Sum('fakt_rasx_per'))['sum_fakt_rasx_per'] or 0

        results[id_rasxod] = {
            'zaMesPrZatr': sum_pr_zatr_1 + sum_pr_zatr_2,
            'zaMesRasxPer': sum_rasx_per_1 + sum_rasx_per_2,
            'prognozPrZatr': sum_prognoz_zatr_1 + sum_prognoz_zatr_2,
            'prognozRasxPer': sum_prognoz_rasx_per_1 + sum_prognoz_rasx_per_2,
            'faktPrZatr': sum_fakt_pr_zatr_1 + sum_fakt_pr_zatr_2,
            'faktRasxPer': sum_fakt_rasx_per_1 + sum_fakt_rasx_per_2,
        }
        всего = 0
        prognoz_всего = 0
        fakt_всего = 0
        for id_rasxod, data in results.items():
            всего += data['zaMesPrZatr'] + data['zaMesRasxPer']
            prognoz_всего += data['prognozPrZatr'] + data['prognozRasxPer']
            fakt_всего += data['faktPrZatr'] + data['faktRasxPer']
            с_начала_год = всего - fakt_всего
            к_прогнозу = prognoz_всего - fakt_всего
    return render(request, 'bigtable.html', {'results': results, 'vsego': всего, 'prognoz_vsego': prognoz_всего, 'fakt_vsego': fakt_всего, 's_nachala_god': с_начала_год, 'k_prognozu': к_прогнозу})





from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = 'Tip_ras/basess.html'



@login_required
def Rb(request):
    table = get_object_or_404(Barchasi, created_by_student_id=request.user.id)
    if request.user != table.created_by_student_id:
        return HttpResponse('Ruxsat berilmagan', status=401)
    results = StudentResult.objects.filter(student=table)
    tables = Barchasi.objects.filter(id_student_id=table)
    context = {
        'tables': tables,
        'results': results,
        'page_title': "Natijalarni ko'rish"
    }
    return render(request, "tb.html", context)





from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Barchasi
from .serializers import BarchasiSerializer

class BarchasiViewSet(viewsets.ModelViewSet):
    serializer_class = BarchasiSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Barchasi.objects.filter(Student=self.request.user)



from django.db.models import Sum
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Barchasi, Student
from django.db.models import Sum
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Barchasi, Student



"""""
class BarchasiDataView(APIView):
    def get(self, request):
        now = datetime.now()
        month = now.month
        year =  now.year

        data = {}

        # Get the current logged in student
        student = Student.objects.get(admin=request.user)

        student_data = {}

        for id_rasxod_id in range(1, 14):  # Iterate over id_rasxod_id values from 1 to 13
            total_pr_zatr_1 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=1, data_date__year=year, data_date__month=month).aggregate(Sum('pr_zatr'))
            total_pr_zatr_2 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=2, data_date__year=year, data_date__month=month).aggregate(Sum('pr_zatr'))

            total_rasx_per_1 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=1, data_date__year=year, data_date__month=month).aggregate(Sum('rasx_per'))
            total_rasx_per_2 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=2, data_date__year=year, data_date__month=month).aggregate(Sum('rasx_per'))

            total_prognoz_zatr_1 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=1, data_date__year=year, data_date__month=month).aggregate(Sum('prognoz_zatr'))
            total_prognoz_zatr_2 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=2, data_date__year=year, data_date__month=month).aggregate(Sum('prognoz_zatr'))
            
            total_prognoz_rasx_per_1 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=1, data_date__year=year, data_date__month=month).aggregate(Sum('prognoz_rasx_per'))
            total_prognoz_rasx_per_2 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=2, data_date__year=year, data_date__month=month).aggregate(Sum('prognoz_rasx_per'))
            
            total_fakt_pr_zatr_1 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=1, data_date__year=year, data_date__month=month).aggregate(Sum('fakt_pr_zatr'))
            total_fakt_pr_zatr_2 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=2, data_date__year=year, data_date__month=month).aggregate(Sum('fakt_pr_zatr'))

            total_fakt_rasx_per_1 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=1, data_date__year=year, data_date__month=month).aggregate(Sum('fakt_rasx_per'))
            total_fakt_rasx_per_2 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=2, data_date__year=year, data_date__month=month).aggregate(Sum('fakt_rasx_per'))


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

            student_data[id_rasxod_id] = {
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
            Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id).update(vsego_pr_zatr=za_mes_pr_zatr)
            Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id).update(vsego_rasx_per=za_mes_rasx_per)
            Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id).update(vsego_prognoz_zatr=prognoz_pr_zatr)
            Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id).update(vsego_prognoz_rasx_per=prognoz_rasx_per)
            Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id).update(vsego_fakt_pr_zatr=fakt_pr_zatr)
            Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id).update(vsego_fakt_rasx_per=fakt_rasx_per)
            Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id).update(vsego_всего=za_mes_vsego)
            Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id).update(vsego_prognoz_всего=prognoz_vsego)
            Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id).update(vsego_fakt_всего=fakt_vsego)
            Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id).update(vsego_с_начала_год=с_начала_год)
            Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id).update(vsego_к_прогнозу=k_prognozu)

        data[student.id] = student_data

        

        return Response(data)
"""""



###########################################################################################################
from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from .models import Barchasi, Student

def barchasi_data(request):
    current_year = timezone.now().year
    current_month = timezone.now().month

    data = {}

    for student in Student.objects.all():  # Iterate over all students
        student_data = {}

        for id_rasxod_id in range(1, 14):  # Iterate over id_rasxod_id values from 1 to 13
            total_pr_zatr_1 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=1, data_date__year=current_year, data_date__month=current_month).aggregate(Sum('pr_zatr'))
            total_pr_zatr_2 = Barchasi.objects.filter(created_by_student=student, id_rasxod_id=id_rasxod_id, id_tip_table_id=2, data_date__year=current_year, data_date__month=current_month).aggregate(Sum('pr_zatr'))

            if total_pr_zatr_1['pr_zatr__sum'] is None:
                total_pr_zatr_1['pr_zatr__sum'] = 0.0

            if total_pr_zatr_2['pr_zatr__sum'] is None:
                total_pr_zatr_2['pr_zatr__sum'] = 0.0

            total_pr_zatr = total_pr_zatr_1['pr_zatr__sum'] + total_pr_zatr_2['pr_zatr__sum']

            student_data[id_rasxod_id] = total_pr_zatr

        data[student.id] = student_data

    return render(request, 'te.html', {'data': data})








from django.http import JsonResponse
from .models import Barchasi

def calculate(request):
    id_tip_table = request.GET.get('id_tip_table')
    id_rasxod = request.GET.get('id_rasxod')
    data_date = request.GET.get('data_date')
    pr_zatr = request.GET.get('pr_zatr')
    rasx_per = request.GET.get('rasx_per')

    if id_tip_table is not None and id_rasxod is not None:
        id_tip_table = Barchasi.objects.get(id=id_tip_table).id_tip_table
        id_rasxod = Barchasi.objects.get(id=id_rasxod).id_rasxod

    if pr_zatr is not None and rasx_per is not None:
        pr_zatr = float(pr_zatr)
        rasx_per = float(rasx_per)
        # Perform your calculation here
        result = pr_zatr + rasx_per
    else:
        result = 'Missing parameters'
    return JsonResponse({'result': result})
    
    
    
    

from django.shortcuts import render
from django.views import View

class TableView(View):
    def get(self, request, *args, **kwargs):
        form = AjaxForm()
        return render(request, 'student_template/xisoblash.html', {'form': form})
    

class TR(TemplateView):
    template_name = 'tr.html'























from django.http import JsonResponse
from django.db.models import Sum
from .models import Barchasi

def get_fakt_pr_zatr(request):
    id_rasxod_id = 1
    id_tip_table_id = 1
    id_student_id = 1

    last_year = Barchasi.objects.filter(
        id_rasxod_id=id_rasxod_id,
        id_tip_table_id=id_tip_table_id,
        id_student_id=id_student_id,
        data_date__year=(Barchasi.objects.latest('data_date').data_date.year - 1),
        data_date__month=Barchasi.objects.latest('data_date').data_date.month
    ).aggregate(Sum('fakt_pr_zatr'))

    response_data = {'pr_zatr': last_year['fakt_pr_zatr__sum'] or 0}
    return render(request, 'te.html', response_data)











from django.shortcuts import render
from .models import Barchasi

def calculate_and_render_table(request):
    # Ma'lumotlarni hisoblash
    queryset_1 = Barchasi.objects.filter(id_tip_table=1)
    fakt_vsego_1 = sum([item.fakt_всего for item in queryset_1])

    perevozka1 = Barchasi.objects.filter(id_tip_table=1).values_list('fakt_pr_zatr')
    perevozka2 = Barchasi.objects.filter(id_tip_table=1).values_list('fakt_rasx_per')
    perevozka3 = Barchasi.objects.filter(id_tip_table=1).values_list('fakt_всего')

    pvd1 = Barchasi.objects.filter(id_tip_table=2).values_list('fakt_pr_zatr')
    pvd2 = Barchasi.objects.filter(id_tip_table=2).values_list('fakt_rasx_per')
    pvd3 = Barchasi.objects.filter(id_tip_table=2).values_list('fakt_всего')
    #fakt_vsego_2 = sum([item.fakt_всего for item in queryset_2])

    pr_zatr_values = [item.pr_zatr for item in Barchasi.objects.all()]

    # Table.html ga ma'lumotlarni o'tkazish
    context = {
        'perevozka1': perevozka1,
        'perevozka2': perevozka2,
        'perevozka3': perevozka3,
        'pvd1': pvd1,
        'pvd2': pvd2,
        'pvd3': pvd3,
    }
    return render(request, 'te.html', context)