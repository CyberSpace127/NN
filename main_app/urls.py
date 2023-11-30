from django.urls import path
from django.urls import path, include
from main_app.EditResultView import EditResultView
from .views import  *
from . import views
from . import hod_views, staff_views, student_views, views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .student_views import MiniTableView


urlpatterns = [
    path("", views.login_page, name='login_page'),
    path("get_attendance", views.get_attendance, name='get_attendance'),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name='showFirebaseJS'),
    path("doLogin/", views.doLogin, name='user_login'),
    path("logout_user/", views.logout_user, name='user_logout'),
    path("admin/home/", hod_views.admin_home, name='admin_home'),
    path("staff/add", hod_views.add_staff, name='add_staff'),
    path('nn/', hod_views.nn_list, name='nn_list'),
    path('nn/create/', hod_views.nn_create, name='nn_create'),
    path('nn/update/<int:pk>/', hod_views.nn_update, name='nn_update'),
    path('nn/delete/<int:pk>/', hod_views.nn_delete, name='nn_delete'),
    path('company/', hod_views.company_list, name='company_list'),
    path('company/create/', hod_views.company_create, name='company_create'),
    path('company/update/<int:pk>/', hod_views.company_update, name='company_update'),
    path('company/delete/<int:pk>/', hod_views.company_delete, name='company_delete'),
    path('minicompany/', hod_views.minicompany_list, name='minicompany_list'),
    path('minicompany/create/', hod_views.minicompany_create, name='minicompany_create'),
    path('minicompany/update/<int:pk>/', hod_views.minicompany_update, name='minicompany_update'),
    path('minicompany/delete/<int:pk>/', hod_views.minicompany_delete, name='minicompany_delete'),
    path("course/add", hod_views.add_course, name='add_course'),
    path("send_student_notification/", hod_views.send_student_notification,
         name='send_student_notification'),
    path("send_staff_notification/", hod_views.send_staff_notification,
         name='send_staff_notification'),
    path("add_session/", hod_views.add_session, name='add_session'),
    path("admin_notify_student", hod_views.admin_notify_student,
         name='admin_notify_student'),
    path("admin_notify_staff", hod_views.admin_notify_staff,
         name='admin_notify_staff'),
    path("admin_view_profile", hod_views.admin_view_profile,
         name='admin_view_profile'),
    path("check_email_availability", hod_views.check_email_availability,
         name="check_email_availability"),
    path("session/manage/", hod_views.manage_session, name='manage_session'),
    path("session/edit/<int:session_id>",
         hod_views.edit_session, name='edit_session'),
    path("student/view/feedback/", hod_views.student_feedback_message,
         name="student_feedback_message",),
    path("staff/view/feedback/", hod_views.staff_feedback_message,
         name="staff_feedback_message",),
    path("student/view/leave/", hod_views.view_student_leave,
         name="view_student_leave",),
    path("staff/view/leave/", hod_views.view_staff_leave, name="view_staff_leave",),
    path("attendance/view/", hod_views.admin_view_attendance,
         name="admin_view_attendance",),
    path("attendance/fetch/", hod_views.get_admin_attendance,
         name='get_admin_attendance'),
    path("student/add/", hod_views.add_student, name='add_student'),
    path("subject/add/", hod_views.add_subject, name='add_subject'),
    path("staff/manage/", hod_views.manage_staff, name='manage_staff'),
    path("student/manage/", hod_views.manage_student, name='manage_student'),
    path("course/manage/", hod_views.manage_course, name='manage_course'),
    path("subject/manage/", hod_views.manage_subject, name='manage_subject'),
    path("staff/edit/<int:staff_id>", hod_views.edit_staff, name='edit_staff'),
    path("staff/delete/<int:staff_id>",
         hod_views.delete_staff, name='delete_staff'),

    path("course/delete/<int:course_id>",
         hod_views.delete_course, name='delete_course'),

    path("subject/delete/<int:subject_id>",
         hod_views.delete_subject, name='delete_subject'),

    path("session/delete/<int:session_id>",
         hod_views.delete_session, name='delete_session'),

    path("student/delete/<int:student_id>",
         hod_views.delete_student, name='delete_student'),
    path("student/edit/<int:student_id>",
         hod_views.edit_student, name='edit_student'),
    path("course/edit/<int:course_id>",
         hod_views.edit_course, name='edit_course'),
    path("subject/edit/<int:subject_id>",
         hod_views.edit_subject, name='edit_subject'),
    path('hod/all_table/', hod_views.staff_student_data, name='admin_table'),
    path('staff-student-data/', hod_views.StaffStudentData.as_view({'get': 'list'}), name='staff-student-data'),
    path('apiall/', hod_views.APIALL.as_view(), name='apiall'),
    path("hod/All-Entrprises/", hod_views.GIGTABLE, name='gigtable'),










    # Staff
    path("staff/home/", staff_views.staff_home, name='staff_home'),
    path("staff/apply/leave/", staff_views.staff_apply_leave,
         name='staff_apply_leave'),
    path("staff/feedback/", staff_views.staff_feedback, name='staff_feedback'),
    path("staff/view/profile/", staff_views.staff_view_profile,
         name='staff_view_profile'),
    path("staff/attendance/take/", staff_views.staff_take_attendance,
         name='staff_take_attendance'),
    path("staff/attendance/update/", staff_views.staff_update_attendance,
         name='staff_update_attendance'),
    path("staff/get_students/", staff_views.get_students, name='get_students'),
    path("staff/attendance/fetch/", staff_views.get_student_attendance,
         name='get_student_attendance'),
    path("staff/attendance/save/",
         staff_views.save_attendance, name='save_attendance'),
    path("staff/attendance/update/",
         staff_views.update_attendance, name='update_attendance'),
    path("staff/fcmtoken/", staff_views.staff_fcmtoken, name='staff_fcmtoken'),
    path("staff/view/notification/", staff_views.staff_view_notification,
         name="staff_view_notification"),
    path("staff/result/add/", staff_views.staff_add_result, name='staff_add_result'),
    path("staff/result/edit/", EditResultView.as_view(),
         name='edit_student_result'),
    path('staff/result/fetch/', staff_views.fetch_student_result,
         name='fetch_student_result'),
    path('staff/RJU_BIG_TBALE/', staff_views.Rju_big_table, name='rju_big_table'),
    path('staff/create_new_table/', staff_views.create_rju_table, name='create_new_table'),
    path('Rrju_table/', staff_views.Rju_table, name='rju_table'),
    path('staff/Rju_manage_student/', staff_views.Rju_manage_student, name='rju_manage_student'),
    path('staff/BIG_T/', staff_views.BIG_T, name='big_t'),
    path('create_staff_table', staff_views.create_staff_table, name='create_staff_table'),
    path('staff/for-test/', staff_views.ForTest, name='fortest'),








    # Student
    path("student/home/", student_views.student_home, name='student_home'),
    path("student/view/attendance/", student_views.student_view_attendance,
         name='student_view_attendance'),
    path("student/apply/leave/", student_views.student_apply_leave,
         name='student_apply_leave'),
    path("student/feedback/", student_views.student_feedback,
         name='student_feedback'),
    path("student/view/profile/", student_views.student_view_profile,
         name='student_view_profile'),
    path("student/fcmtoken/", student_views.student_fcmtoken,
         name='student_fcmtoken'),
    path("student/view/notification/", student_views.student_view_notification,
         name="student_view_notification"),
    path('student/view/result/', student_views.student_view_result,
         name='student_view_result'),

    path('barchasi/', student_views.BarchasiListView.as_view(), name='barchasi_list'),
    path('barchasi/<int:pk>/', student_views.BarchasiDetailView.as_view(), name='barchasi_detail'),
    path('barchasi/create/', student_views.create, name='barchasi_create'),
    path('barchasi/<int:pk>/update/', student_views.barchasi_update, name='barchasi_update'),
    path('barchasi/<int:pk>/delete/', student_views.BarchasiDeleteView.as_view(), name='barchasi_delete'),



    path('tiptable/', student_views.tiptable_list, name='tiptable_list'),
    path('tiptable/<int:pk>/', student_views.tiptable_detail, name='tiptable_detail'),
    path('tiptable/create/', student_views.tiptable_create, name='tiptable_create'),
    path('tiptable/<int:pk>/update/', student_views.tiptable_update, name='tiptable_update'),
    path('tiptable/<int:pk>/delete/', student_views.tiptable_delete, name='tiptable_delete'),
    
    # URLs for Rasxod
    path('rasxod/', student_views.rasxod_list, name='rasxod_list'),
    path('rasxod/<int:pk>/', student_views.rasxod_detail, name='rasxod_detail'),
    path('rasxod/create/', student_views.rasxod_create, name='rasxod_create'),
    path('rasxod/<int:pk>/update/', student_views.rasxod_update, name='rasxod_update'),
    path('rasxod/<int:pk>/delete/', student_views.rasxod_delete, name='rasxod_delete'),
    path('testing/', student_views.IndexView.as_view(), name='testing'),





    path('iz_prognoz/', student_views.iz_prognoz_list, name='iz_prognoz_list'),
    path('iz_prognoz/<int:pk>/', student_views.iz_prognoz_detail, name='iz_prognoz_detail'),
    path('iz_prognoz/new/', student_views.iz_prognoz_new, name='iz_prognoz_new'),
    path('iz_prognoz/<int:pk>/edit/', student_views.iz_prognoz_edit, name='iz_prognoz_edit'),
    path('iz_prognoz/<int:pk>/delete/', student_views.iz_prognoz_delete, name='iz_prognoz_delete'),
    path('space/', student_views.Space, name='space'),
    path('student/Mini_Table/', student_views.MiniTable, name='mini_Table'),
    path('big/', student_views.your_view, name='big'),
    path('vsego/', student_views.barchasi_data, name='data'),
    path('student/calculate_total/', student_views.calculate, name='calculate_total'),
    path('table/', student_views.TableView.as_view(), name='table'),
    path('tr/', student_views.TR.as_view(), name='tr'),
    path('api/minitable/', MiniTableView.as_view(), name='minitable'),

    path('te/', student_views.get_fakt_pr_zatr, name='te'),
    path('tel/', student_views.calculate_and_render_table, name='tel'),


    
   
]



