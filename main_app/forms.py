from django import forms
from django.forms.widgets import DateInput, TextInput

from .models import *
from .models import Organizations, MTU_Company, Korxon



class DateRangeForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()



class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Erkak'), ('F', 'Ayol')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender', 'password', 'profile_pic', 'address']


class StudentForm(CustomUserForm):

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + ['st_id']  # Add 'MTU' here


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
                 ['course']


class CourseForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = Course


class SubjectForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Subject
        fields = ['name', 'staff', 'course']


class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


class LeaveReportStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStudentForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStudent
        fields = ['feedback']


class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields


class EditResultForm(FormSettings):
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(
        label="Session Year", queryset=session_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        fields = ['session_year', 'subject', 'student', 'test', 'exam']


from django import forms
from .models import Rasxod, TipTable, Barchasi


class RasxodForm(forms.ModelForm):
    class Meta:
        model = Rasxod
        fields = '__all__'


class TipTableForm(forms.ModelForm):
    class Meta:
        model = TipTable
        fields = '__all__'


class BarchasiForm(forms.ModelForm):
    class Meta:
        model = Barchasi
        fields = ['id_tip_table', 'id_rasxod', 'data_date', 'pr_zatr', 'rasx_per', 'prognoz_zatr', 'prognoz_rasx_per',
                  'fakt_pr_zatr', 'fakt_rasx_per']


class OrganizationsForm(forms.ModelForm):
    class Meta:
        model = Organizations
        fields = '__all__'  # Boshqa atributlarni qo'shing

    # Agar qo'shimcha validatsiya kerak bo'lsa, quyidagi metodni qo'shing
    # def clean_<field_name>(self):
    #     field_value = self.cleaned_data.get('<field_name>')
    #     # Validatsiya kodlari
    #     return field_value


class MTU_CompanyForm(forms.ModelForm):
    class Meta:
        model = MTU_Company
        fields = '__all__'  # Boshqa atributlarni qo'shing


class KorxonForm(forms.ModelForm):
    class Meta:
        model = Korxon
        fields = '__all__'  # Boshqa atributlarni qo'shing


from django import forms
from .models import IZ_prognoz


class IZPrognozForm(forms.ModelForm):
    class Meta:
        model = IZ_prognoz
        fields = ('name_prognoz',)


from django import forms
from .models import Barchasi


class BarchasiForm(forms.ModelForm):
    class Meta:
        model = Barchasi
        fields = ['id_tip_table', 'id_rasxod', 'data_date', 'prognoz_zatr', 'prognoz_rasx_per', 'fakt_pr_zatr',
                  'fakt_rasx_per']


class RjuForm(forms.ModelForm):
    class Meta:
        model = Barchasi
        fields = ['id_tip_table', 'id_rasxod', 'data_date', 'pr_zatr', 'rasx_per', 'prognoz_zatr', 'prognoz_rasx_per',
                  'fakt_pr_zatr', 'fakt_rasx_per']


from django import forms
from .models import Barchasi, Rasxod, TipTable


class AjaxForm(forms.Form):
    id_tip_table = forms.ModelChoiceField(queryset=TipTable.objects.all())
    id_rasxod = forms.ModelChoiceField(queryset=Rasxod.objects.all())


from django import forms


class MonthYearForm(forms.Form):
    MONTH_CHOICES = [(i, i) for i in range(1, 13)]
    YEAR_CHOICES = [(i, i) for i in range(2023, 2031)]

    month = forms.ChoiceField(choices=MONTH_CHOICES)
    year = forms.ChoiceField(choices=YEAR_CHOICES)
