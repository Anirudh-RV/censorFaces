import React, { Component } from 'react';
import axios from 'axios';
import '../../cssComponents/App.css';
import {Progress} from 'reactstrap';
import { BrowserRouter, Route, Switch, Redirect } from 'react-router-dom';
import Cookies from 'universal-cookie';
import Button from 'react-bootstrap/Button';

/*
Get the two functions:
1. cropFacesFromImages
2. getMlOutPut

working, pipeline :
1. Upload Images
2. cropFacesFromImages
3. getMlOutPut
*/
class UploadMultipleFiles extends Component {
  constructor(props) {
    super(props);
      this.state = {
        selectedFile: null,
        loaded:0
      }
      var data = require('../../jsonData/urlData.json'); //(with path)
      this.nodeServerUrl = data.nodeServerUrl
      this.goApiUrl = data.goApiUrl
      this.pythonBackEndUrl = data.mlBackEndUrl
}

componentDidMount(){
this.heading.innerHTML = this.props.userName+"</br>CensorPeople on Video :"+this.props.videoName;
}

logOut = () =>{
    const cookies = new Cookies()
    cookies.remove('userName');
    window.location.reload(false);
}

checkMimeType=(event)=>{
    //getting file object
    let files = event.target.files
    //define message container
    let err = []
    // list allow mime type
    const types = ['image/png', 'image/jpeg', 'image/gif']
    // loop access array
    for(var x = 0; x<files.length; x++) {
     // compare file type find doesn't matach
         if (types.every(type => files[x].type !== type)) {
         // create error message and assign to container
         err[x] = files[x].type+' is not a supported format\n';
       }
     };
     for(var z = 0; z<err.length; z++) {// if message not same old that mean has error
         // discard selected file
        event.target.value = null
    }
   return true;
}

maxSelectFile=(event)=>{
    let files = event.target.files
        if (files.length > 101) {
           const msg = 'Only 10 images can be uploaded at a time'
           event.target.value = null
           return false;
      }
    return true;
 }

checkFileSize=(event)=>{
  let files = event.target.files
  let size = 2000000
  let err = [];
  for(var x = 0; x<files.length; x++) {
  if (files[x].size > size) {
   err[x] = files[x].type+'is too large, please pick a smaller file\n';
 }
};
for(var z = 0; z<err.length; z++) {// if message not same old that mean has error
  // discard selected file
 event.target.value = null
}
return true;
}

cropFacesFromImages = () =>{
  var userName = this.props.name
  var imageName = this.state.imageNames[this.state.index]
  var url = this.nodeServerUrl+"/img/"+this.props.name+"/images/"+this.state.imageNames[this.state.index]
  var mlOutPutUrl = this.nodeServerUrl+"/img/"+this.props.name+"/images/yoloOutput_"+this.props.name+"_"+imageName

  axios.post(this.pythonBackEndUrl+"/yolo/",{
    'userName':userName,
    'imageName':imageName,
    'imageUrl':url,
    'Coordinates':this.getCoordinates(),
    'annotationLabels':this.annotationHashMap,
    'server':this.nodeServerUrl,
    'api':this.goApiUrl
  })
  .then(res => {
      window.open(mlOutPutUrl, '_blank');
    })
    .catch(err => { // then print response status
    console.log(err)
    })
}

getMlOutPut = () =>{
  var userName = this.props.name
  var imageName = this.state.imageNames[this.state.index]
  var url = this.nodeServerUrl+"/img/"+this.props.name+"/images/"+this.state.imageNames[this.state.index]
  var mlOutPutUrl = this.nodeServerUrl+"/img/"+this.props.name+"/images/yoloOutput_"+this.props.name+"_"+imageName

  axios.post(this.pythonBackEndUrl+"/yolo/",{
    'userName':userName,
    'imageName':imageName,
    'imageUrl':url,
    'Coordinates':this.getCoordinates(),
    'annotationLabels':this.annotationHashMap,
    'server':this.nodeServerUrl,
    'api':this.goApiUrl
  })
  .then(res => {
      window.open(mlOutPutUrl, '_blank');
    })
    .catch(err => { // then print response status
    console.log(err)
    })
}

// using Api, add names of the images being uploaded to a database
sendToMlBackend = (files) =>{
  axios.post(this.goApiUrl+"/getimages",{
 'username':this.props.userName,
 'videoName':this.props.videoName
 })
 .then(res => {
      var imageNames = res.data.ImageNames
      var uniqueNames = imageNames.filter((item, i, ar) => ar.indexOf(item) === i);
      for(var x =0; x<uniqueNames.length;x++)
      {
        console.log("imageNames: "+uniqueNames[x])
      }
   })
   .catch(err => { // then print response status
   console.log(err)
 })
}

// using Api, add names of the images being uploaded to a database
addToBackendUsingApi = (files) =>{
      files = this.state.selectedFile
      var userName = this.props.userName;
      var fileNames = "";
      for(var x =0; x<files.length-1;x++)
      {
        fileNames = fileNames +files[x].name+ ",";
      }
      fileNames = fileNames + files[files.length-1].name;
      // api call
      axios.post(this.goApiUrl+"/insertimagedata",{
        'username': userName,
        'filenames' : fileNames,
        'videoname' : this.props.videoName
      })
        .then(res => {
      })
      .catch(err => { // then print response status
        console.log(err)
    })
}

// && this.checkFileSize(event) taken out for unlimited uploads
onChangeHandler=event=>{
  var files = event.target.files
  if(this.maxSelectFile(event) && this.checkMimeType(event)){
  // if return true allow to setState
     this.setState({
     selectedFile: files,
     loaded:0
   })
  }
}

onClickHandler = () => {
    const data = new FormData()
    // getting userName from input
    var userName = this.props.userName;
    // filling FormData with selectedFiles(Array of objects)
    for(var x = 0; x<this.state.selectedFile.length; x++) {
      data.append('file', this.state.selectedFile[x])
    }
    // header carries information of userName to backend with data
    axios.post(this.nodeServerUrl+"/upload",data,
    {
    headers: {
      userName: this.props.userName,
      userCredentials: userName,
      type : 'imageUpload'
    },
      onUploadProgress: ProgressEvent => {
        this.setState({
          loaded: (ProgressEvent.loaded / ProgressEvent.total*100),
        })
      },
    })
    .then(res => { // then print response status
        this.addToBackendUsingApi(this.state.selectedFile)
        // redirect to WorkingArea.js for viewing images
    })
    .catch(err => { // then print response status
      console.log(err)
    })
}

render() {
    return (
    <div>
      <h2 className = "appName" ref = {c => this.heading = c}></h2>
      <div className="uploadImages">
              <div class="form-group files">
                <label>Upload Your File </label>
                <input id="inputUploadID" type="file" class="form-control" multiple onChange={this.onChangeHandler}/>
              </div>
              <div class="form-group">
                <Progress id="progressBar" max="100" color="success" value={this.state.loaded} >{Math.round(this.state.loaded,2) }%</Progress>
              </div>

              <Button className="StartButton" block bsSize="large" onClick={this.onClickHandler} type="button">
                Upload
              </Button>

              <Button className="StartButton" block bsSize="large" onClick={this.downloadVideo} type="button">
                Download
              </Button>

              <Button className="StartButton" block bsSize="large" onClick={this.sendToMlBackend} type="button">
                GETIMAGES
              </Button>

              <Button className="StartButton" block bsSize="large" onClick={this.logOut} type="button">
                Log out
              </Button>
	      </div>
      </div>
    );
  }
}

export default UploadMultipleFiles;
