import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.core.files.storage import default_storage
from rest_framework import viewsets, status
from rest_framework.decorators import action

from .utils import read_pdf, GPT_return_text
from .models import LabReport, Question, Section
from .serializers import UploadLabHandoutSerializer, UploadAnswertoSectionSerializer, UploadAnswertoSectionSerializer, SectionSerializer


class ExtractLabHandoutTextViewSet(viewsets.ModelViewSet):
    queryset = LabReport.objects.all()
    serializer_class = UploadLabHandoutSerializer

    @action(detail=False, methods=['post'])
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
            lab_report.number_of_pages = request.data.get('number_of_pages')
            lab_report.extracted_text = extracted_text

            # Handle sections if provided
            sections_data = request.data.get('sections')
            if sections_data:
                sections_data = json.loads(sections_data)
                for section_text in sections_data:
                    Section.objects.create(lab_report=lab_report, section=section_text)
            #Generate question with LLM
            #Save each question to the question text of the Question object
            #return
            questions = GPT_return_text(f'The lab handout text is {extracted_text}. What are the questions the lab wants us to answer? Return in the format ["Question1", "Question2","Question3", etc.]')
            start = questions.index("[")
            questions = questions[start:]
            if questions:
                questions = json.loads(questions)
                print("Success")
                for question in questions:
                    Question.objects.create(lab_report=lab_report, question_text=question)

            lab_report.save()
        except Exception as e:
            return JsonResponse({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(lab_report)
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    
#URL: /<id>/generate_section_text/
class GenerateSectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = UploadAnswertoSectionSerializer

    @action(detail=True, methods=['put', 'patch'])
    def generate_section_text(self, request, pk=None):
        text = request.data.get('text')

        try:
            # Retrieve the Section instance by its primary key (pk)
            section = self.get_object()
            # Extract additional details for processing
            title = section.section
            lab_report = section.lab_report
            extracted_text = lab_report.extracted_text

            # Generate refined text using GPT (assuming GPT_return_text is defined)
            answer = GPT_return_text(
                f"The lab handout text is {extracted_text}. Now I want to write the {title} of the lab report. "
                f"This is some of my ideas but very incomplete: {text}. Can you help me generate a refined version of {title}?"
            )
            section.text = answer
            section.save()

            # Serialize and return the updated section data
            response_data = SectionSerializer(section).data

        except Section.DoesNotExist:
            return JsonResponse({"error": "Section not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": f"Failed to generate text: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse(response_data, status=status.HTTP_200_OK)
