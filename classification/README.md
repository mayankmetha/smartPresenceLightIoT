# Counting the number of people in the room
To count the number of people in the room, a camera will be used. The camera image captured from the video stream will be run through a [YOLO](https://pjreddie.com/darknet/yolo/) Deep Neural Network to find if there are people present in the room, and then find the count of people. <br>

## REST Server
The application access is through REST API, called via `GET http://<IP:5000>/classify` <br>
The response is in the format:
```json
{
    'numPersons': int
}
```

## Setup
Python 3.6+ is required. Install all necessary dependencies through: <br>
`python -m pip install -r requirements.txt` <br>

This will take care of installing any necessary modules <br>
For YOLO, the pre-trained model weights are needed for the network to classify the image. They can be downloaded from the YOLO webiste [here](https://pjreddie.com/media/files/yolov3.weights) (237MB). <br>
<br>
Save the weights file directly under the `classification` sub-folder under the root folder. <br>

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
Make a HTTP GET call to `<server IP>:5000/peopleCount` (using a browser will also work) to run get the number of people in the room. <br>

The file can also be run directly as a python script through `python rest_server_classifier.py`, which simply grabs a single frame from the camera, and returns the number of people found. <br>

