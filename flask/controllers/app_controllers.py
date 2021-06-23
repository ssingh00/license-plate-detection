from google.cloud import automl, vision
import cv2
import matplotlib.pyplot as plt
import base64
import controllers.app_constants as app_constants
from PIL import Image
from datetime import datetime
import io
import os


def plate_detection(file_path, project_id, model_id):

    prediction_client = automl.PredictionServiceClient()

    # Get the full path of the model.
    model_full_id = automl.AutoMlClient.model_path(
        project_id, "us-central1", model_id)

    # Read the file.
    with open(file_path, "rb") as content_file:
        content = content_file.read()

    image = automl.Image(image_bytes=content)
    payload = automl.ExamplePayload(image=image)
    # params is additional domain-specific parameters.
    # score_threshold is used to filter the result
    # https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#predictrequest
    params = {"score_threshold": "0.8"}
    request = automl.PredictRequest(
        name=model_full_id, payload=payload, params=params)
    response = prediction_client.predict(request=request)

    print("Prediction results:")
    for result in response.payload:
        print(result)

    # read image
    img = cv2.imread(file_path)
    # height, width, number of channels in image
    height = img.shape[0]
    width = img.shape[1]

    vertices = list(
        result.image_object_detection.bounding_box.normalized_vertices)

    x_min = int(vertices[0].x * width)
    y_min = int(vertices[0].y * height)
    x_max = int(vertices[1].x * width)
    y_max = int(vertices[1].y * height)
    cropped = img[y_min:y_max, x_min:x_max]

    folder_time = str(datetime.now().timestamp()).replace(".", "")

    im = Image.fromarray(cropped)
    cropped_path = os.path.join(
        app_constants.CROPPED_FOLDER, folder_time+"_"+"cropped.jpg")

    im.save(cropped_path)
    return cropped_path


def plate_recognition(cropped_path):
    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # The name of the image file to annotate
    file_name = os.path.abspath(cropped_path)

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # Performs label detection on the image file
    # response = client.label_detection(image=image)
    # labels = response.label_annotations
    # print('Labels:')
    # for label in labels:
    #     print(label.description)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    return (str(texts[0].description).split("\n")[0])
