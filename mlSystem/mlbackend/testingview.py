import os
import cv2
import numpy as np
import requests
import urllib.request
import json

# Functions for Comparing faces:

def makedir(videoName):
        # Directory
        try:
            directory = videoName
            path = os.path.join("assets", directory)
            os.mkdir(path)
            print("Directory created: "+str(directory))

        except:
            print("File exists, Continue")

def cropFace(request):
    dictdata = {'userName':'usertest','imageUrls':'http://localhost:4000/img/sampleVideo.mp4','imageNames':'testadams.jpg,testcillian.jpg,testhardy.jpg','videoName':'sampleVideo','serverUrl':'http://localhost:4000'}

    #decodeddata = request.body.decode('utf-8')
    #dictdata = ast.literal_eval(decodeddata)
    userName = dictdata["userName"]
    imageUrls = dictdata["imageUrls"]
    imageNames = dictdata["imageNames"]
    videoName = dictdata["videoName"]
    nodeServerUrl = dictdata["serverUrl"]
    listofimages = imageNames.split(",")

    print("list: ")
    print(listofimages)
    makedir(videoName)

    for images in listofimages:
        if images != ".DS_Store":
            print("image name :"+images)
            # Load the cascade
            face_cascade = cv2.CascadeClassifier('Weights/haarcascade_frontalface_default.xml')
            # Read the input image
            url = nodeServerUrl+"/img/"+userName+"/images/"+images
            print("url: "+str(url))
            req = urllib.request.urlopen(url)
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv2.imdecode(arr, -1) # 'Load it as it is'
            print("imgae shape: "+str(img.shape))
            # Convert into grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            # Draw rectangle around the faces
            #  crop_img = img[res["topleft"]["y"]:res["bottomright"]["y"],res["topleft"]["x"]:res["bottomright"]["x"]]
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                break

            crop_img = img[y:y+h,x:x+w]
            crop_img = crop_img.copy()
            crop_img = cv2.resize(crop_img, dsize=(512, 512), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite('assets/'+videoName+"/"+images,crop_img) # can remain the same
            print("writing: "+str('assets/'+videoName+"/"+images))

    context = {"data":"data"}
    return render(request, 'index.html', context)

cropFace(1)
