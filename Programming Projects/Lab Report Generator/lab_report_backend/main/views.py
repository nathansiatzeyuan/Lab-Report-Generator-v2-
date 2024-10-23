from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import json

@csrf_exempt
def lab_report_view(request):
    if request.method == 'POST':
        try:
            # Retrieve the uploaded PDF file
            if 'pdf' in request.FILES:
                pdf_file = request.FILES['pdf']
                pdf_path = default_storage.save(f'uploads/{pdf_file.name}', pdf_file)

            # Retrieve the uploaded image file (if provided)
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                image_path = default_storage.save(f'uploads/{image_file.name}', image_file)
            else:
                image_path = None

            # Extract other form data (page_limit and selected sections)
            page_limit = request.POST.get('page_limit')
            sections_needed = request.POST.get('sections_needed')

            # Convert sections_needed from JSON string to a Python object
            selected_sections = json.loads(sections_needed) if sections_needed else []

            print(f"Page limit: {page_limit}")
            print(f"Selected sections: {selected_sections}")
            print(f"PDF saved to: {pdf_path}")
            if image_path:
                print(f"Image saved to: {image_path}")

            # Respond with a success message
            return JsonResponse({'status': 'success', 'message': 'Lab report submitted successfully.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
