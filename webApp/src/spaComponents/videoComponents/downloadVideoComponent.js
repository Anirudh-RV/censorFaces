import React, { Component } from 'react'
import axios from 'axios'
import {Progress} from 'reactstrap'
import { BrowserRouter, Route, Switch, Redirect } from 'react-router-dom'
import Cookies from 'universal-cookie'
import '../../cssComponents/App.css'
import Form from 'react-bootstrap/Form'
import Button from 'react-bootstrap/Button'
import Bootstrap from "react-bootstrap"
import {FormGroup, FormControl} from "react-bootstrap"
import { Link } from 'react-router-dom'

class DownloadVideoComponent extends Component {
  constructor(props) {
    super(props)
      this.state = {
        selectedFile: null,
        loaded:0
      }
      var data = require('../../jsonData/urlData.json'); //(with path)
      this.nodeServerUrl = data.nodeServerUrl
      this.goApiUrl = data.goApiUrl
      this.pythonBackEndUrl = data.mlBackEndUrl
      this.videoName = ""
}

componentDidMount(){
this.heading.innerHTML = this.props.location.state.userName+"</br>Censor People Directly From Videos"
}

checkMimeType=(event)=>{
    //getting file object
    let files = event.target.files
    //define message container
    let err = []
    // list allow mime type
    const types = ['image/png', 'image/jpeg', 'image/gif','video/mp4']
    // loop access array
    for(var x = 0; x<files.length; x++) {
     // compare file type find doesn't matach
         if (types.every(type => files[x].type !== type)) {
         // create error message and assign to container
         err[x] = files[x].type+' is not a supported format\n'
       }
     }
     for(var z = 0; z<err.length; z++) {// if message not same old that mean has error
         // discard selected file
        event.target.value = null
    }
   return true
}

maxSelectFile=(event)=>{
    let files = event.target.files
        if (files.length !=1) {
           const msg = 'Only 1 images can be uploaded at a time'
           event.target.value = null
           return false
      }
    return true
}

checkFileSize=(event)=>{
  let files = event.target.files
  let size = 2000000
  let err = []
  for(var x = 0; x<files.length; x++) {
  if (files[x].size > size) {
   err[x] = files[x].type+'is too large, please pick a smaller file\n'
    }
  }
  for(var z = 0; z<err.length; z++) {// if message not same old that mean has error
    // discard selected file
   event.target.value = null
  }
  return true
}

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
    var userName = this.props.location.state.userName
    var videoNames = []
    // filling FormData with selectedFiles(Array of objects)
    for(var x = 0; x<this.state.selectedFile.length; x++) {
      data.append('file', this.state.selectedFile[x])
    }
    // header carries information of userName to backend with data
    axios.post(this.nodeServerUrl+"/upload",data,
    {
    headers: {
      userName: userName,
      type: 'videoUpload'
    },
      onUploadProgress: ProgressEvent => {
        this.setState({
          loaded: (ProgressEvent.loaded / ProgressEvent.total*100),
        })
      },
    })
    .then(res => { // then print response status
      this.goToUploadPage(this.state.selectedFile[0].name)
    })
    .catch(err => { // then print response status
    console.log(err)
  })
}

goToUploadPage = (videoName) =>{
  this.props.history.push({
    pathname: '/editPage',
    state: {userName: this.props.location.state.userName},
    videoName : videoName
  })
}

handleSubmit = () =>{
  this.Message.innerHTML = "The process may take a few minutes..."
  axios.post(this.nodeServerUrl+"/download/",{
    userName : this.props.location.state.userName,
    videoName : this.videoName.value,
    videoUrl : this.videoUrl.value,
  })
  .then(res => { // then print response status
    //toast.success('upload success')
    this.Message.innerHTML = "Download complete..."
  })
  .catch(err => {
  console.log(err)
  })
}

render() {
    return (
      <div>
      <h2 className = "appName" ref = {c => this.heading = c}></h2>

      <div className="videoUpload">
        <label>Upload Videos from your System</label>
        <input id="videoUploadID" type="file" class="form-control" multiple onChange={this.onChangeHandler}/>
        <div class="form-group">
          <Progress id="progressBar" max="100" color="success" value={this.state.loaded} >{Math.round(this.state.loaded,2) }%</Progress>
        </div>
        <Button className="StartButton" block bsSize="large" onClick={this.onClickHandler} type="button">
          Upload
        </Button>
      </div>

      <div className="signIn">
        <form onSubmit={this.handleSubmit}>
        <p class = "signInHead">Annotation Tool</p>
        <p class = "signUpHead">Upload A Video From YouTube</p>
        &nbsp
          <FormGroup controlId="url" bsSize="large">
            <FormControl
              autoFocus
              placeholder="Enter the url of the youtube video"
              ref = {c => this.videoUrl = c}
            />
          </FormGroup>

          <FormGroup controlId="url" bsSize="large">
            <FormControl
              autoFocus
              placeholder="Enter the name of the video"
              ref = {c => this.videoName = c}
            />
          </FormGroup>

          <Button className="StartButton" block bsSize="large" onClick={this.handleSubmit} type="button">
            Download
          </Button>

          <Button className="StartButton" block bsSize="large" onClick={this.goToUploadPage} type="button">
            Upload Images of People
          </Button>
          <br/>
          <p className = "errorMessage" ref = {c => this.Message = c}></p>
        </form>
      </div>

      <div className="signIn" ref = {c => this.Info = c}>
        <p className = "linkToAccount"> Download complete and not redirecting?Click here&nbsp
          <Link className="linkToSignUp" onClick={this.goToUploadPage}>Redirect</Link>
        </p>
      </div>
      </div>
    )
  }
}

export default DownloadVideoComponent
