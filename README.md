# censorFaces
A WebApp where the user can upload a video and images of multiple people who they want to censor from that particular video

# Steps to run the application
**Prerequisites**
1. Download mongo
2. Download GO and Go libraries using go get *link of library*
3. setting up Django environment
  a. Download and run yolo9000
  b. Download face_recognition

**To run**
1. clone the git
2. Download both weights from :
  1. https://drive.google.com/drive/folders/1pW4mKNOzOIf0Edyr4BppwnLpddCQ6Qch?usp=sharing

  2. https://drive.google.com/open?id=1JupZYcQO7Jh5aiRQLwNzYZaX0uYGULdK

3. Place the weights in the Django/mlbackend folder with the other .py files

**To run Everything**
1. source startApp.sh
2. Press enter once everything runs to get control back of the terminal
3. Jobs will be running in the background
4. To verify, run command jobs in the terminal to see the processes running

**WebApp (Reactjs) : port-3000**
1. cd Client
2. npm install
3. npm start

**API (Golang): port-8080**
1. cd API_Go
2. go run main.go

**MLSystem (Django): port-8000**
1. cd pythonbackend
2. cd djangobackend
3. python3 manage.py runserver

**Server (NodeJS): port-4000**
1. cd NodeServer
To setup npm_modules:
1. source install.sh
**(OR)**
2. npm install
3. npm install express-zip
4. npm install multer
5. npm install zip-folder
6. npm install cors
7. npm install express
8. npm install serve-index
**To start server**
9. node server.js

**if npm build is failing, install by : npm install <absent library>**

**For building yolo9000 :**
1. pip install Cython
2. git clone https://github.com/thtrieu/darkflow.git
3. cd darkflow
4. python3 setup.py build_ext --inplace
5. pip install .

**To setup mongo collections :**
1. use GoDB
2. db.createCollection("ImageNames")
3. db.createCollection("UserData")

# About

**Feature list**
1. Upload Video
2. Upload photos
3. Censor People

**To migrate the application to cloud, please check DeploymentReadme**
