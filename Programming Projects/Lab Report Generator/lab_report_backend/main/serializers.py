from rest_framework import serializers
from .models import LabReport, Question, Section

class UploadLabHandoutSerializer(serializers.ModelSerializer):
    sections = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    #file, number of pages,
    class Meta:
        model = LabReport
        fields = ['id', 'file', 'number_of_pages',  'sections']