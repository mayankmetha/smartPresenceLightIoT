# Connecting Raspberry Pi to AWS IOT

## Software installation
On your Raspberry Pi, install the AWS IOT SDK for python: <br>
`python3 -m pip install AWSIoTPythonSDK==1.0.0`
Verify that Pi has internet connectivity. MQTT is going to be used to exchange messages <br>

## AWS IOT setup
An AWS account is required to set this up. Procure the credentials and login to the AWS Console. Go to the IOT Core section to start setting up an AWS Thing. <br>
Follow [these instructions](https://docs.aws.amazon.com/iot/latest/developerguide/register-device.html) carefully to create and register an AWS thing <br> 
Make sure to download the certificates for your device, and copy them over to Raspberry PI as shown below: <br>
* Put the private key file into a folder called `certs`, name it as `thing_private_key.pem.key`
* Store the IOT client certificate into `certs` as `thing_cert.pem.crt`
* Download the `AmazonRootCA1.pem` from [here](https://www.amazontrust.com/repository/AmazonRootCA1.pem) and put it inside `certs` with the same name
<br>

From the IOT console, find the hostname for the newly created device, and set it inside `aws_iot_utils.py` (through property `host = '<>'`) <br>
Change the device name to the correct name that you have provided while registering your thing on AWS IOT. Set the `device = '<>'` property as well <br>
In the AWS IOT console, go to the `Manage` section, select your thing, and select the `Shadow` section. Edit the device shadow and set it to (First time only): <br> 

```json
{
  "reported": {
    "numLightsOn": 0,
    "currentLdrReading": 0,
    "opMode": "auto"
  }
}
```
<br>

## Running the code
The code is in two parts: <br>
* MQTT Publisher - `aws_iot_client.py` - This makes request to AWS IOT broker for getting current device state, as well as to update the state
* MQTT Subscriber - `aws_iot_listener.py` - This subscribes to the AWS IOT broker for update events, and performs necessary actions

For a quick example run, first start the MQTT subscriber through `python3 aws_iot_listener.py`. Then from a different device (laptop), run the MQTT client with the arguments `python3 aws_iot_client.py update-state off`, which sets the `opMode` to `off` <br>

## Controlling Raspberry PI
If an `update` command is detected, the new state requested by the user is written to the file `raw/opMode` as an integer. The values possible are: <br>
```
0 (auto)
1 (manual)
2 (off)
3 (on)
```
Each update causes the device shadow to be refreshed with the latest values for `numLightsOn`and `currentLdrReading`, both inferred from the files `raw/smd0` and `raw/ldr0`. <br>
```
