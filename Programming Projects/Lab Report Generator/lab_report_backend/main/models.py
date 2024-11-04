from django.db import models

# Create your models here.
from django.db import models

class LabReport(models.Model):
    file = models.FileField(upload_to='lab_reports/')
    number_of_pages = models.IntegerField(null=True, blank=True)
    extracted_text = models.TextField()


class Question(models.Model):
    lab_report = models.ForeignKey(LabReport, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    experimental_value = models.ImageField(null=True, blank=True)
    answer = models.TextField()


class Section(models.Model):
    lab_report = models.ForeignKey(LabReport, related_name='sections', on_delete=models.CASCADE)
    section = models.CharField(max_length=100)
    text = models.TextField()

