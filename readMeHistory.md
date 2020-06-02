**TODO**
3. Add an option to record videos uploaded to the backend
4. Get the cropFacesFromImages and getMlOutPut working
**DONE**
1. Set up video upload
2. Set up image upload
3. Set up blur image pipeline
  a. Video upload
  b. Images upload for that particular video
  c. Save images in a separate folder
    i. read all uploaded images
    ii. detect face
    iii. crop face and save in a folder
  d. Read video
  e. Read the images from the folder
  f. save the processed frames into a video and make it available for download

General guide : To Kill Ports : lsof -P | grep ':8080' | awk '{print $2}' | xargs kill -9
