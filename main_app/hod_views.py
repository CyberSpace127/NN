import json
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from .models import Organizations, MTU_Company, Korxon
from .forms import OrganizationsForm, MTU_CompanyForm, KorxonForm
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required

def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    subjects = Subject.objects.all()
    total_subject = subjects.count()
    total_course = Course.objects.all().count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name[:7])
        attendance_list.append(attendance_count)
    context = {
        'page_title': "Admin Dashboard",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_course': total_course,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list

    }
    return render(request, 'hod_template/home_content.html', context)





# Ro'yxatni ko'rish (Read)
def nn_list(request):
    nn_list = Organizations.objects.all()
    return render(request, 'NN/nn_list.html', {'nn_list': nn_list})

# Ma'lumot qo'shish (Create)
def nn_create(request):
    if request.method == 'POST':
        form = OrganizationsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('nn_list')
    else:
        form = OrganizationsForm()
    return render(request, 'NN/nn_create.html', {'form': form})

# Ma'lumotni o'zgartirish (Update)
def nn_update(request, pk):
    nn = get_object_or_404(Organizations, pk=pk)
    if request.method == 'POST':
        form = OrganizationsForm(request.POST, instance=nn)
        if form.is_valid():
            form.save()
            return redirect('nn_list')
    else:
        form = OrganizationsForm(instance=nn)
    return render(request, 'NN/nn_update.html', {'form': form})

# Ma'lumotni o'chirish (Delete)
def nn_delete(request, pk):
    nn = get_object_or_404(Organizations, pk=pk)
    if request.method == 'POST':
        nn.delete()
        return redirect('nn_list')
    return render(request, 'NN/nn_confirm_delete.html', {'nn': nn})



# Company model uchun CRUD operatsiyalari

# Ro'yxatni ko'rish (Read)
def company_list(request):
    company_list = MTU_Company.objects.all()
    return render(request, 'MTU/company_list.html', {'company_list': company_list})

# Ma'lumot qo'shish (Create)
def company_create(request):
    if request.method == 'POST':
        form = MTU_CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_list')
    else:
        form = MTU_CompanyForm()
    return render(request, 'MTU/company_create.html', {'form': form})

# Ma'lumotni o'zgartirish (Update)
def company_update(request, pk):
    company = get_object_or_404(MTU_Company, pk=pk)
    if request.method == 'POST':
        form = MTU_CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_list')
    else:
        form = MTU_CompanyForm(instance=company)
    return render(request, 'MTU/company_update.html', {'form': form})

# Ma'lumotni o'chirish (Delete)
def company_delete(request, pk):
    company = get_object_or_404(MTU_Company, pk=pk)
    if request.method == 'POST':
        company.delete()
        return redirect('company_list')
    return render(request, 'MTU/company_delet.html', {'company': company})

# MiniCompany model uchun CRUD operatsiyalari

# Ro'yxatni ko'rish (Read)
def minicompany_list(request):
    minicompany_list = Korxon.objects.all()
    return render(request, 'Minicompany/minicompany_list.html', {'minicompany_list': minicompany_list})

# Ma'lumot qo'shish (Create)
def minicompany_create(request):
    if request.method == 'POST':
        form = KorxonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('minicompany_list')
    else:
        form = KorxonForm()
    return render(request, 'Minicompany/minicompany_create.html', {'form': form})

# Ma'lumotni o'zgartirish (Update)
def minicompany_update(request, pk):
    minicompany = get_object_or_404(Korxon, pk=pk)
    if request.method == 'POST':
        form = KorxonForm(request.POST, instance=minicompany)
        if form.is_valid():
            form.save()
            return redirect('minicompany_list')
    else:
        form = KorxonForm(instance=minicompany)
    return render(request, 'Minicompany/minicompany_update.html', {'form': form})

# Ma'lumotni o'chirish (Delete)
def minicompany_delete(request, pk):
    minicompany = get_object_or_404(Korxon, pk=pk)
    if request.method == 'POST':
        minicompany.delete()
        return redirect('minicompany_list')
    return render(request, 'Minicompany/minicompany_delete.html', {'minicompany': minicompany})


def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add RJU Staff'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.staff.course = course
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")

    return render(request, 'hod_template/add_staff_template.html', context)


def add_student(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Add Korxona staff'}
    if request.method == 'POST':
        if student_form.is_valid():
            last_name = student_form.cleaned_data.get('first_name')
            address = student_form.cleaned_data.get('address')
            email = student_form.cleaned_data.get('email')
            gender = student_form.cleaned_data.get('gender')
            password = student_form.cleaned_data.get('password')
            RJU_Staff = student_form.cleaned_data.get('st_id')
            passport = request.FILES['profile_pic']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, last_name=last_name, profile_pic=passport_url)
                user.gender = gender
                user.address = address
                user.student.st_id = RJU_Staff
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_student'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'hod_template/add_student_template.html', context)


def add_course(request):
    form = CourseForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add RJU NAME'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course()
                course.name = name
                course.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_RJU'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_course_template.html', context)


def add_subject(request):
    form = SubjectForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject()
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_subject'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_subject_template.html', context)


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': 'Manage Staff'
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_student(request):
    students = CustomUser.objects.filter(user_type=3)
    context = {
        'students': students,
        'page_title': 'Manage Students'
    }
    return render(request, "hod_template/manage_student.html", context)


def manage_course(request):
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Manage Courses'
    }
    return render(request, "hod_template/manage_course.html", context)


def manage_subject(request):
    subjects = Subject.objects.all()
    context = {
        'subjects': subjects,
        'page_title': 'Manage Subjects'
    }
    return render(request, "hod_template/manage_subject.html", context)


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    form = StaffForm(request.POST or None, instance=staff)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Edit Staff'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=staff.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                staff.course = course
                user.save()
                staff.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:
        user = CustomUser.objects.get(id=staff_id)
        staff = Staff.objects.get(id=user.id)
        return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        'form': form,
        'student_id': student_id,
        'page_title': 'Edit Student'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            session = form.cleaned_data.get('session')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                student.session = session
                user.gender = gender
                user.address = address
                student.course = course
                user.save()
                student.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_student', args=[student_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "hod_template/edit_student_template.html", context)


def edit_course(request, course_id):
    instance = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Edit Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course.objects.get(id=course_id)
                course.name = name
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)


def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Edit Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject.objects.get(id=subject_id)
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'hod_template/edit_subject_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Created")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Manage Sessions'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Edit Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Session Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def student_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStudent.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Student Feedback Messages'
        }
        return render(request, 'hod_template/student_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStudent, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def staff_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Staff Feedback Messages'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Staff'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_student_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Students'
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    subjects = Subject.objects.all()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'View Attendance'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify_staff(request):
    staff = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Send Notifications To Staff",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


def admin_notify_student(request):
    student = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Send Notifications To Students",
        'students': student
    }
    return render(request, "hod_template/student_notification.html", context)


@csrf_exempt
def send_student_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Student, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('student_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': student.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStudent(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Student Management System",
                'body': message,
                'click_action': reverse('staff_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': staff.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(staff=staff, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff'))


def delete_student(request, student_id):
    student = get_object_or_404(CustomUser, student__id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect(reverse('manage_student'))


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some students are assigned to this course already. Kindly change the affected student course and try again")
    return redirect(reverse('manage_course'))


def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect(reverse('manage_subject'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Session deleted successfully!")
    except Exception:
        messages.error(
            request, "There are students assigned to this session. Please move them to another session.")
    return redirect(reverse('manage_session'))














from django.shortcuts import render
from .models import Barchasi, Staff

def staff_barchasi(request):
    staffs = Staff.objects.all()
    context_list = []
    for staff in staffs:
        students = staff.students.all()  # get all students related to this staff
        for student in students:
            barchasi_1 = Barchasi.objects.filter(id_staff=staff.id, id_tip_table=1).values_list('fakt_всего', flat=True)
            barchasi_2 = Barchasi.objects.filter(id_staff=staff.id, id_tip_table=2).values_list('fakt_всего', flat=True)
            barchasi_3 = Barchasi.objects.filter(staff=staff, id_tip_table=1).values_list('vsego_fakt_всего', flat=True)
            barchasi_4 = Barchasi.objects.filter(student=student, id_tip_table=1).values_list('fakt_всего', flat=True)
            barchasi_5 = Barchasi.objects.filter(student=student, id_tip_table=2).values_list('fakt_всего', flat=True)
            barchasi_6 = Barchasi.objects.filter(student=student, id_tip_table=2).values_list('vsego_fakt_всего', flat=True)
            
            context = {
                'staff': staff,
                'student': student,
                'barchasi_1': barchasi_1,
                'barchasi_2': barchasi_2,
                'barchasi_3': barchasi_3,
                'barchasi_4': barchasi_4,
                'barchasi_5': barchasi_5,
                'barchasi_5': barchasi_5,
                }
            context_list.append(context)
    return render(request, 'hod_template/admin_table.html', {'context_list': context_list})





def staff_barchasi(request):
    staffs = Staff.objects.all()
    context_list = []
    for staff in staffs:
        students = staff.students.all()  # get all students related to this staff
        for student in students:
            barchasi_1 = Barchasi.objects.filter(staff=staff, id_tip_table=1).values_list('vsego_fakt_всего', flat=True)
            barchasi_2 = Barchasi.objects.filter(student=student, id_tip_table=2).values_list('vsego_fakt_всего', flat=True)


            context = {
                'staff': staff,
                'student': student,
                'barchasi_1': barchasi_1,
                'barchasi_2': barchasi_2
            }
            context_list.append(context)
    return render(request, 'hod_template/admin_table.html', {'context_list': context_list})





from django.shortcuts import render
from .models import Staff, Student, Barchasi
from datetime import datetime

def staff_student_data(request):
    month = request.GET.get('month', datetime.now().month)
    year = request.GET.get('year', datetime.now().year)

    data = []
    staffs = Staff.objects.all()
    for staff in staffs:
        staff_data = {}
        staff_data['staff_name'] = str(staff)
        staff_barchasi = Barchasi.objects.filter(id_staff=staff, data_date__year=year, data_date__month=month)
        staff_data['staff_barchasi_1_fakt'] = staff_barchasi.filter(id_tip_table=1).values_list('fakt_всего', flat=True)
        staff_data['staff_barchasi_2_fakt'] = staff_barchasi.filter(id_tip_table=2).values_list('fakt_всего', flat=True)
        staff_data['staff_vsego_fakt'] = staff_barchasi.values_list('vsego_fakt_всего', flat=True).distinct()

        students = Student.objects.filter(st_id=staff)
        student_data = []
        for student in students:
            student_dict = {}
            student_dict['student_name'] = str(student)
            student_barchasi = Barchasi.objects.filter(id_student=student, data_date__year=year, data_date__month=month)
            student_dict['student_barchasi_1_fakt'] = student_barchasi.filter(id_tip_table=1).values_list('fakt_всего', flat=True)
            student_dict['student_barchasi_2_fakt'] = student_barchasi.filter(id_tip_table=2).values_list('fakt_всего', flat=True)
            student_dict['student_vsego_fakt'] = student_barchasi.values_list('vsego_fakt_всего', flat=True).distinct()
            student_data.append(student_dict)

        staff_data['students'] = student_data
        data.append(staff_data)

    return render(request, 'hod_template/admin_table.html', {'data': data, 'month': month, 'year': year})



























from rest_framework import viewsets
from .models import Staff, Student, Barchasi
from .serializers import StaffSerializer, StudentSerializer, BarchasiSerializer

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class BarchasiViewSet(viewsets.ModelViewSet):
    queryset = Barchasi.objects.all()
    serializer_class = BarchasiSerializer












from rest_framework import viewsets
from rest_framework.response import Response
from .models import Staff, Student, Barchasi
from .serializers import StaffSerializer, StudentSerializer, BarchasiSerializer

class StaffStudentData(viewsets.ViewSet):
    def list(self, request):
        month = request.GET.get('month', datetime.now().month)
        year = request.GET.get('year', datetime.now().year)

        data = []
        staffs = Staff.objects.all()
        for staff in staffs:
            staff_data = {}
            staff_data['staff_name'] = str(staff)
            staff_barchasi = Barchasi.objects.filter(id_staff=staff, data_date__year=year, data_date__month=month)
            staff_data['staff_barchasi_1_fakt'] = staff_barchasi.filter(id_tip_table=1).values_list('fakt_всего', flat=True)
            staff_data['staff_barchasi_2_fakt'] = staff_barchasi.filter(id_tip_table=2).values_list('fakt_всего', flat=True)
            staff_data['staff_vsego_fakt'] = staff_barchasi.values_list('vsego_fakt_всего', flat=True).distinct()

            students = Student.objects.filter(st_id=staff)
            student_data = []
            for student in students:
                student_dict = {}
                student_dict['student_name'] = str(student)
                student_barchasi = Barchasi.objects.filter(id_student=student, data_date__year=year, data_date__month=month)
                student_dict['student_barchasi_1_fakt'] = student_barchasi.filter(id_tip_table=1).values_list('fakt_всего', flat=True)
                student_dict['student_barchasi_2_fakt'] = student_barchasi.filter(id_tip_table=2).values_list('fakt_всего', flat=True)
                student_dict['student_vsego_fakt'] = student_barchasi.values_list('vsego_fakt_всего', flat=True).distinct()
                student_data.append(student_dict)

            staff_data['students'] = student_data
            data.append(staff_data)

        return Response(data)




from django.views.generic import (View, TemplateView, ListView, DetailView,
                                  CreateView, UpdateView, DeleteView)
from . import models

# CLASS BASED VIEWS
# IndexView
class APIALL(TemplateView):
    template_name = 'hod_template/api_all.html'























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
def GIGTABLE(request):
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
   
    # o'tgan yil va oy
    select_month = request.POST.get('month')
    select_year = request.POST.get('year')
    if select_year is not None:
        select_year = int(select_year) - 1

    staff = Staff.objects.all()
    staffs = Staff.objects.all()  
    for staff in staffs: 
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
        'students': students,
        'student_perevozka': student_perevozka,
        'page_title': "Natijalarni ko'rish",
    }
    
    return render(request, "hod_template/sum_table.html",  context)