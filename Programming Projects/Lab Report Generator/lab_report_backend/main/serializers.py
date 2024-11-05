from rest_framework import serializers
from .models import LabReport, Question, Section

class UploadLabHandoutSerializer(serializers.ModelSerializer):
    sections = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    questions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = LabReport
        fields = ['id', 'file', 'number_of_pages',  'sections', 'questions']