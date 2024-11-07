from rest_framework import serializers
from .models import LabReport, Question, Section




class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'lab_report', 'section', 'text']  # Include all the fields you want to serialize


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'lab_report', 'question_text', 'experimental_value', 'answer'] 


class UploadLabHandoutSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, required=False)
    questions = QuestionSerializer(many=True, required=False)
    class Meta:
        model = LabReport
        fields = ['id', 'file', 'number_of_pages',  'sections', 'questions']


class UploadAnswertoSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'text']


class UploadAnswerImagetoQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'experimental_value', 'answer'] 