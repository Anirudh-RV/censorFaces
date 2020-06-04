from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

import requests
from darkflow.net.build import TFNet
# to read images from urls
import os
import time
import ast
import urllib.request

# to read images from urls
import PIL
from PIL import Image
import cv2
from darkflow.net.build import TFNet
import numpy as np
import face_recognition.api as face_recognition
from models.compareFacesUtils import scan_known_people,test_image,compareFaces,makedir

'''
Loading the cfg file to make a placeholder of the network/graph
Filling that network/graph with the weights trained in the yolo9000.weights
threshold of 0.01 provided
'''

yolo9000 = {"model" : "cfg/yolo9000.cfg", "load" : "Weights/yolo9000.weights", "threshold": 0.01}
tfnet = TFNet(yolo9000)

'''
Function: def censorPeople(request)
Needs videoName,videoUrl,userName,facesFolder
The functions reads the videoUrl and each frame is processed
The frames are compared with the images present in the facesFolder
facesFolder is obtained by processing the uploaded images for a particular video and cropping the face from them (Function : cropFaces)
All the outputs will be separate for each user and each video
'''
@csrf_exempt
def censorPeople(request):
    # Decoding received data
    decodeddata = request.body.decode('utf-8')
    dictdata = ast.literal_eval(decodeddata)

    username = dictdata["userName"]
    videoName = dictdata["videoName"]
    nodeServerUrl = dictdata["serverUrl"]

    videoUrl = nodeServerUrl+'/img/'+username+'/videos/'+videoName
    facesFolder = 'assets/'+username+"_"+videoName+"/"
    cap = cv2.VideoCapture(videoUrl)
    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open file...")

    frameWidth = int(cap.get(3))
    frameHeight = int(cap.get(4))
    outputVideo = 'assets/output_'+videoName+'.m4v'
    out = cv2.VideoWriter(outputVideo,cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frameWidth,frameHeight))
    framecount = 0

    # Make this while True to process whole video
    while framecount < 15:
        # Pre-processing variables
        start_time = time.time()
        ret, frame = cap.read()
        if frame is not None:
            framecount = framecount + 1
            img = frame
            img_h = img.shape[0]
            img_w = img.shape[1]
            img_d = img.shape[2]
            imgcv = img
            result = tfnet.return_predict(imgcv)
            count = 0

            for res in result:
                if res["label"] == "person":
                    top = (res["topleft"]["x"], res["topleft"]["y"])
                    bottom = (res["bottomright"]["x"], res["bottomright"]["y"])
                    cropImage = imgcv[res["topleft"]["y"]:res["bottomright"]["y"],res["topleft"]["x"]:res["bottomright"]["x"]]

                    listofmatches = []
                    # Load the cascade
                    face_cascade = cv2.CascadeClassifier('Weights/haarcascade_frontalface_default.xml')
                    # Convert into grayscale
                    gray = cv2.cvtColor(cropImage, cv2.COLOR_BGR2GRAY)
                    # Detect faces
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

                    # Coordinates of the face detected, stopping at one iteration as one crop should contain one face
                    for (x, y, w, h) in faces:
                        x = x+ res["topleft"]["x"]
                        y = y + res["topleft"]["y"]
                        facex = x
                        facey = y
                        facew = w
                        faceh = h
                        break

                    cropImage = img[y:y+h,x:x+w]
                    cropImage = cropImage.copy()
                    croppedface = cv2.resize(cropImage, dsize=(512, 512), interpolation=cv2.INTER_CUBIC)

                    imagesList = os.listdir(facesFolder)
                    for images in imagesList:
                        if images != ".DS_Store":
                            # Load the cascade
                            img2 = facesFolder+images
                            result = compareFaces(croppedface,img2)
                            if result == True:
                                blur = cv2.GaussianBlur(imgcv[facey-15:facey+faceh+15,facex-15:facex+facew+15], (51,51), 0)
                                imgcv[facey-15:facey+faceh+15,facex-15:facex+facew+15] = blur
                                listofmatches.append(images[6:])

            elapsed_time = time.time() - start_time
            out.write(imgcv)

    # shutting video the input and output streams
    cap.release()
    out.release()

    # Sending the video to the NodeServer
    files = {'file': open(outputVideo, 'rb')}
    headers = {
        'username': username,
        'type':'videoUpload',
    }
    response = requests.request("POST", 'http://localhost:4000/upload', files=files, headers=headers)
    print("Backend Process Complete")

    context = {"data":"data"}
    return render(request, 'index.html', context)
