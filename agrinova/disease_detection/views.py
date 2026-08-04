import os
import tempfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.apps import apps
from django.core.files.storage import default_storage

class PredictDiseaseView(APIView):
    permission_classes = [AllowAny]  # Allowing any user to predict for now

    def post(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return Response({'error': 'No image provided. Please upload an image using the "image" field.'}, status=status.HTTP_400_BAD_REQUEST)
            
        image_file = request.FILES['image']
        
        # 1. Validate file format
        valid_extensions = ['.jpg', '.jpeg', '.png']
        ext = os.path.splitext(image_file.name)[1].lower()
        if ext not in valid_extensions:
            return Response({'error': f'Unsupported file extension {ext}. Please upload a JPG or PNG image.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 2. Save file temporarily
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, image_file.name)
        try:
            with open(temp_path, 'wb+') as dest:
                for chunk in image_file.chunks():
                    dest.write(chunk)
                    
            # 3. Get the pre-loaded predictor from apps
            app_config = apps.get_app_config('disease_detection')
            if not app_config.predictor:
                return Response({'error': 'Disease model is currently unavailable on the server.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
            # 4. Predict
            result = app_config.predictor.predict_disease(temp_path)
            
            # 5. Return success
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': f'Failed to process image or predict: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        finally:
            # 6. Cleanup temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
