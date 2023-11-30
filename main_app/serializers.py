from rest_framework import serializers
from .models import Barchasi

class BarchasiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barchasi
        fields = '__all__'  # Or specify a list of field names to include e.g. ['id', 'name', 'created_by_student', ...]




from rest_framework import serializers
from .models import Staff, Student, Barchasi

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

class BarchasiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barchasi
        fields = '__all__'
