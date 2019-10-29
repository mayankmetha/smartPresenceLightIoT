from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient 
import json
from time import sleep
import sys
import threading
import functools

host = "PUT YOUR AWS IOT HOSTNAME HERE"
certPath = "certs"
clientId = "raspberry-pi"
device = 'Device Name'

def getShadowClient(rootCa='{}/AmazonRootCA1.pem'.format(certPath),
                    private_key='{}/thing_private_key.pem.key'.format(certPath),
                    certificate='{}/thing_cert.pem.crt'.format(certPath)):
    # Init AWSIoTMQTTClient
    myAWSIoTMQTTClient = None
    myAWSIoTMQTTClient = AWSIoTMQTTShadowClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTClient.configureCredentials(rootCa, private_key, certificate)

    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    if not myAWSIoTMQTTClient.connect():
        return None
    return myAWSIoTMQTTClient

# Callback function
def printState(event, payload, status, token):
    res = json.dumps(json.loads(payload), indent=4, sort_keys=True)
    print('Request completed with status: {}\nResponse: {}'.format(status, res))
    request = json.loads(payload)
    state = request['state']
    if 'numLightsOn' in state:
        print('Requested value for numLightsOn: {}'.format(state['numLightsOn']))
    if 'opMode' in state:
        print('Requested value for opMode: {}'.format(state['opMode']))
    if 'currentLdrReading' in state:
        print('Requested value for currentLdrReading: {}'.format(state['currentLdrReading']))

    event.set()

if __name__ == '__main__':
    timeout = 10 # secs
    event = threading.Event()
    shadowClient = getShadowClient()
    if not shadowClient:
        print('Failed to connect AWS IOT device')
        exit(1)

    shadow = shadowClient.createShadowHandlerWithName(device, False)
    callback = functools.partial(printState, event)
    shadow.shadowRegisterDeltaCallback(callback)

    print('Registered for callbacks, waiting...')
    event.wait()
