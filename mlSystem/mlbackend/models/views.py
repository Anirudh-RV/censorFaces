from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.template import Context, loader
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.template import Context, loader
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
import json

'''
Loading the cfg file to make a placeholder of the network/graph
Filling that network/graph with the weights trained in the yolo9000.weights
threshold of 0.01 provided
'''
yolo9000 = {"model" : "cfg/yolo9000.cfg", "load" : "Weights/yolo9000.weights", "threshold": 0.01}
tfnet = TFNet(yolo9000)

'''
Funtion description: def scan_known_people(known_people_folder)

'''
def scan_known_people(known_people_folder):
    known_names = []
    known_face_encodings = []

    basename = known_people_folder
    img = known_people_folder
    encodings = face_recognition.face_encodings(img)
    if len(encodings) == 1:
        known_names.append(basename)
        known_face_encodings.append(encodings[0])
    return known_names, known_face_encodings


'''
Funtion description: def test_image(image_to_check, known_names, known_face_encodings)

'''
def test_image(image_to_check, known_names, known_face_encodings):
    unknown_image = face_recognition.load_image_file(image_to_check)

    # Scale down image if it's giant so things run a little faster
    if unknown_image.shape[1] > 1600:
        scale_factor = 1600.0 / unknown_image.shape[1]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            unknown_image = scipy.misc.imresize(unknown_image, scale_factor)

    unknown_encodings = face_recognition.face_encodings(unknown_image)

    try:
        if len(unknown_encodings)==1:
            for unknown_encoding in unknown_encodings:
                result = face_recognition.compare_faces(known_face_encodings, unknown_encoding)
                distance = face_recognition.face_distance(known_face_encodings, unknown_encoding)
                print("True") if True in result else print("False ")

            return distance[0],result[0]
        else:
            return "0","Many Faces or No Faces"
    except:
        return "0","Many Faces or No Faces"

'''
Probably a redudant function : def image_files_in_folder(folder)
might be removed
'''
def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

'''
Funtion description: def compareFaces(known_people_folder, image_to_check)

'''
def compareFaces(known_people_folder, image_to_check):
    known_names, known_face_encodings = scan_known_people(known_people_folder)
    distance,result=test_image(image_to_check, known_names, known_face_encodings)
    return result

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
    facesFolder = dictdata["facesFolder"]
    videoUrl = dictdata["videoUrl"]
    videoName = dictdata["videoName"]
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
            print("Framecount: "+str(framecount))
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
    }
    response = requests.request("POST", 'http://localhost:4000/upload', files=files, headers=headers)
    print("Backend Process Complete")

    context = {"data":"data"}
    return render(request, 'index.html', context)

'''
The function: def makedir(videoName)
Needs videoName
creates a directory with the name videoName
'''
def makedir(videoName):
        # Directory
        try:
            directory = videoName
            path = os.path.join("assets", directory)
            os.mkdir(path)
            print("Directory created: "+str(directory))
        except:
            print("File exists, Continue")

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
    imageUrls = dictdata["imageUrls"]
    imageNames = dictdata["imageNames"]
    videoName = dictdata["videoName"]
    nodeServerUrl = dictdata["serverUrl"]
    imagesList = imageNames.split(",")

    print("imagesList: ")
    print(imagesList)
    makedir(videoName)

    for images in imagesList:
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
            #  cropImage = img[res["topleft"]["y"]:res["bottomright"]["y"],res["topleft"]["x"]:res["bottomright"]["x"]]
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                break

            cropImage = img[y:y+h,x:x+w]
            cropImage = cropImage.copy()
            cropImage = cv2.resize(cropImage, dsize=(512, 512), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite('assets/'+videoName+"/"+images,cropImage)
            print("writing: "+str('assets/'+videoName+"/"+images))

    context = {"data":"data"}
    return render(request, 'index.html', context)
