# Counting the number of people in the room
To count the number of people in the room, a camera will be used. The camera image captured from the video stream will be run through a [MobileNetV2-SSD](https://pjreddie.com/darknet/yolo/) Deep Neural Network to find if there are people present in the room, and then find the count of people. <br> 

## REST Server
The application access is through REST API, called via `GET http://<IP:5000>/countPeople` <br>
The response is simply an integer representing the number of people found. <br>

## Setup
Python 3.6+ is required. Install all necessary dependencies through: <br>
`python -m pip install -r requirements.txt` <br>

This will take care of installing any necessary modules <br>
For detection to work, the pre-trained model weights are needed for the network to classify the image. They can be downloaded from the Tensorflow webiste [here](http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_oid_v4_2018_12_12.tar.gz) (152MB). <br>
<br>
Extract the contents of the tarball, and retain the `saved_model` folder. Ensure that the `saved_model` folder is under a directory named `ssd`. The folder structure looks like: <br>
```
+ root
  + classification
    - README.md
    + ssd
        + saved_model
        - label_mapping.csv
  ...
```

### Camera
Currently, the phone camera is used in place of an actual camera <br>
On your smartphone, install the `IP WebCam` app, or any similar WiFi camera streaming application <br>
Run the WiFi camera streamer, and make a note of the IP address. <br>
Change the IP address in the `rest_server_classifier.py` file as shown: <br>
`
CAMERA_IP = '<camera IP address:Port>' (e.g. '192.168.1.2:8080')
` <br>

## Running the application
Start the REST server using `FLASK_APP=rest_server_classifier flask run` <br>
Make a HTTP GET call to `<server IP>:5000/countPeople` (using a browser will also work) to run get the number of people in the room. <br>

The file can also be run directly as a python script through `python rest_server_classifier.py`, which simply grabs a single frame from the camera, and returns the number of people found. <br>

