import os
import django
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
import glob
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agrinova.settings")
django.setup()

def run_test():
    print("Testing Disease Prediction API...")
    
    client = Client()
    
    # Get a sample image
    img_files = glob.glob("../ml/PlantDiseaseImages/*/*.jpg")
    if not img_files:
        print("No test images found.")
        return
        
    test_img_path = img_files[0]
    print(f"Testing with image: {test_img_path}")
    
    with open(test_img_path, 'rb') as f:
        img_data = f.read()
        
    img_file = SimpleUploadedFile(
        name='test_image.jpg',
        content=img_data,
        content_type='image/jpeg'
    )
    
    # Make POST request
    response = client.post('/api/disease/predict/', {'image': img_file})
    
    print(f"\nStatus Code: {response.status_code}")
    if response.status_code == 200:
        print("\nResponse JSON:")
        print(json.dumps(response.json(), indent=2))
        print("\nSUCCESS: API integration is working perfectly!")
    else:
        print("\nFAILED:")
        print(response.content.decode('utf-8'))

if __name__ == '__main__':
    run_test()
