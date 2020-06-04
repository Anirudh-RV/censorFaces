from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from models.compareFacesUtils import scan_known_people,test_image,compareFaces,makedir
import os
import time
import ast
import urllib.request
import requests
import face_recognition.api as face_recognition

import PIL
from PIL import Image
import cv2
import numpy as np

'''
Function: def cropFace(request)
Needs userName,imageUrls,imageNames,videoName,nodeServerUrl
Makes a new directory for the particular video
Reads the images uploaded by the user for the particular video
Process the images, crop the face and save the images in the new directory created
The images in this directory will be used by the censorPeople function
'''
@csrf_exempt
def cropFace(request):
    decodeddata = request.body.decode('utf-8')
    dictdata = ast.literal_eval(decodeddata)

    userName = dictdata["userName"]
    imagesList = dictdata["imageNames"]
    videoName = dictdata["videoName"]
    nodeServerUrl = dictdata["serverUrl"]

    # Make a separate directory for the video
    makedir(userName+"_"+videoName)

    for images in imagesList:
        if images != ".DS_Store":
            # Load the cascade
            face_cascade = cv2.CascadeClassifier('Weights/haarcascade_frontalface_default.xml')
            # Read the input image
            url = nodeServerUrl+"/img/"+userName+"/images/"+images
            req = urllib.request.urlopen(url)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, -1) # 'Load it as it is'
            # Convert into grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            # Draw rectangle around the faces
            #  cropImage = img[res["topleft"]["y"]:res["bottomright"]["y"],res["topleft"]["x"]:res["bottomright"]["x"]]
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                break

            cropImage = img[y:y+h,x:x+w]
            cropImage = cropImage.copy()
            cropImage = cv2.resize(cropImage, dsize=(512, 512), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite('assets/'+userName+"_"+videoName+"/"+images,cropImage)

    context = {"data":"data"}
    return render(request, 'index.html', context)
