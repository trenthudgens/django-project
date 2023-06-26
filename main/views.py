from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.conf import settings

import base64
import os
import json
from PIL import Image, ImageOps
import torch
from torch import nn
from torchvision import transforms
import io
from io import BytesIO

PREDICTED_DIGIT = None

# Create your views here.
def home(request):
    return render(request, 'main/homepage.html')

# Model setup
# Define the same model structure
model = nn.Sequential(nn.Linear(784, 128),
                      nn.ReLU(),
                      nn.Linear(128, 64),
                      nn.ReLU(),
                      nn.Linear(64, 10),
                      nn.LogSoftmax(dim=1))

# Load the model parameters
model.load_state_dict(torch.load('model.pth', map_location='cpu'))

# Ensure the model is in evaluation mode
model.eval()

def store_transformed_image(image):
    image = transforms.ToPILImage()(image)

    # Resize the image
    image = image.resize((image.width * 10, image.height * 10), resample=Image.NEAREST)
    
    # Save the resized image
    image_path = os.path.join(settings.MEDIA_ROOT, 'transformed_image.png')
    image.save(image_path)

    return image_path

@csrf_exempt
def save_image(request):
    def get_prediction(digit, image_url):
        # Create a dictionary with the predicted digit and image URL
        response_data = {
            'digit': digit,
            'image': image_url,
        }

        # Return the response as JSON
        return JsonResponse(response_data)

    if request.method == "POST":
        # Decode and process image data
        data = request.body.decode('utf-8')
        received_json_data = json.loads(data)

        image_data = received_json_data['image'].split(',')[1]
        image_data = base64.b64decode(image_data)

        # Open the image file with PIL and convert to grayscale
        image = Image.open(BytesIO(image_data)).convert('L')
        image = ImageOps.invert(image)

        # Downscale image
        image = image.resize((28, 28), resample=Image.BILINEAR)

        # Perform transformations on the image
        transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
        image = transform(image)

        # Store the transformed image
        image_path = store_transformed_image(image)

        image = image.view(1, -1)

        # Make the prediction
        with torch.no_grad():
            output = model(image)

        # Get the predicted class
        _, predicted = torch.max(output.data, 1)
        predicted_digit = predicted.item()

        # Pass the predicted digit and image URL to the template
        return get_prediction(predicted_digit, image_path)

    else:
        # If not POST method, render the form
        return render(request, 'main/homepage.html')