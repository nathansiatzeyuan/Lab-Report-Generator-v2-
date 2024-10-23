import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from .utils import read_pdf, GPT_return_text


@csrf_exempt
def lab_report_view(request):
    if request.method == 'POST':
        try:
            # Retrieve the uploaded PDF file
            if 'pdf' in request.FILES:
                pdf_file = request.FILES['pdf']
                handout_text = read_pdf(pdf_file)
                # pdf_path = default_storage.save(f'uploads/{pdf_file.name}', pdf_file)

            # Retrieve the uploaded image file (if provided)
            # if 'image' in request.FILES:
            #     image_file = request.FILES['image']
            #     image_path = default_storage.save(f'uploads/{image_file.name}', image_file)
            # else:
            #     image_path = None

            # Extract other form data (page_limit and selected sections)
            page_limit = request.POST.get('page_limit')
            sections_needed = request.POST.get('sections_needed')
            # Convert sections_needed from JSON string to a Python object
            selected_sections = json.loads(sections_needed) if sections_needed else []
            question = f"Generarte a Latex format lab report. The lab_handout text is here: {handout_text}. The sections needed in the lab_report are {selected_sections} with page limit {page_limit}"
            latex_lab_report = GPT_return_text(question)
            # if image_path:
            #     print(f"Image saved to: {image_path}")

            # Respond with a success message
            return JsonResponse({'lab_report': f'{latex_lab_report}'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
