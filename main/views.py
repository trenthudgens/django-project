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

@csrf_exempt
def save_image(request):
    def get_prediction(digit):
        # Create a dictionary with the predicted digit
        response_data = {
            'digit': digit,
        }

        # Return the predicted digit as a JSON response
        return JsonResponse(response_data)

    if request.method == "POST":
        data = request.body.decode('utf-8')
        received_json_data = json.loads(data)

        image_data = received_json_data['image'].split(',')[1]
        image_data = base64.b64decode(image_data)

        # Open the image file with PIL and convert to grayscale
        image = Image.open(BytesIO(image_data)).convert('L')
        image = ImageOps.invert(image)

        image.save("image.png")
        save = image.resize((28, 28), Image.ANTIALIAS) # DOWNSCALE
        save.save("dummy.png")
        # image.save("dummy.png")

        # Resize and normalize the image
        transform = transforms.Compose([transforms.Resize((28, 28)),
                                        transforms.ToTensor(),
                                        transforms.Normalize((0.5,), (0.5,))])
        image = transform(image)

        # Add an extra dimension because the model expects batches
        image = image.view(1, -1)

        # Make the prediction
        with torch.no_grad():
            output = model(image)

        # Get the predicted class
        _, predicted = torch.max(output.data, 1)
        predicted_digit = predicted.item()

        print(predicted_digit)

        # Pass the predicted digit to the template
        return get_prediction(predicted_digit)

    else:
        # If not POST method, render the form
        return render(request, 'main/homepage.html')