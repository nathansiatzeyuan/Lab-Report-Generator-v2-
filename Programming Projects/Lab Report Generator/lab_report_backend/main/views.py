import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.core.files.storage import default_storage
from rest_framework import viewsets, status
from rest_framework.decorators import action

from .utils import read_pdf, GPT_return_text
from .models import LabReport, Question, Section
from .serializers import UploadLabHandoutSerializer


class ExtractLabHandoutTextViewSet(viewsets.ModelViewSet):
    queryset = LabReport.objects.all()
    serializer_class = UploadLabHandoutSerializer

    @action(detail=False, methods=['post'], url_path='upload', url_name='upload')
    def upload_lab_handout(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        
        if not file:
            return JsonResponse({"error": "File not provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Save LabReport instance
        lab_report = LabReport(file=file)
        lab_report.save()

        # Extract text from the PDF file
        extracted_text = ""
        try:
            extracted_text = read_pdf(file)
            lab_report.number_of_pages = request.get('number_of_pages')
            lab_report.extracted_text = extracted_text

            # Handle sections if provided
            sections_data = request.data.get('sections')
            if sections_data:
                for section_text in sections_data:
                    Section.objects.create(lab_report=lab_report, text=section_text)

            lab_report.save()
        except Exception as e:
            return JsonResponse({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(lab_report)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)