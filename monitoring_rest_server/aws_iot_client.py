from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient 
import json
from time import sleep
import sys
import threading
import functools

host = 'PUT YOUR AWS IOT HOSTNAME HERE'
certPath = "certs"
clientId = "raspberry-pi_1"
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
    event.set()

if __name__ == '__main__':
    timeout = 10 # secs
    args = sys.argv
    if len(args) < 2:
        print('Syntax: {} get-state|update-mode [auto|manual|on|off]'.format(args[0]))
        exit(1)    

    shadowClient = getShadowClient()
    if not shadowClient:
        print('Failed to connect to AWS IOS device')
        exit(1)

    shadow = shadowClient.createShadowHandlerWithName(device, False)
    event = threading.Event()
    if args[1] == 'get-state':
        callback = functools.partial(printState, event)
        shadow.shadowGet(callback, timeout)
    elif args[1] == 'update-state':
        if not len(args) == 3:
            print('Invalid arguments. New mode required. Only One of manual|auto|on|off must be specified')
            exit(1)

        updatePayload = { 'state': {
                            'desired' : {
                                'opMode' : args[2]
                                }
                            }
                        }
        print('Attempting to set operation mode to {}'.format(args[2]))
        callback = functools.partial(printState, event)
        shadow.shadowUpdate(json.dumps(updatePayload), callback, timeout)
    else:
        print('Invalid arguments. One of <get-state|update-state> need to be specified')
        exit(1)

    event.wait()
