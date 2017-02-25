#Alexa IoT Sprinker

Integrates OpenSprinkler Pi to the AWS Alexa
so that you can command your sprinkler.


## Flow of messages

This is how your commands are sent to the OSPI server:

Echo -> Alexa -> Lambda -> AWS IoT -> IoT client -> OSPI server


## Project

The project is organised into 2 parts, __thing__ and __controller__.

###Thing
A Thing is the Raspberry Pi running the IoT client and OSPI server.

###Controller
The Alexa service is a controller that sends commands to the Thing.
Other examples could be a Mobile App.

## Deployment

###Thing
Deploying a Thing requires AWS IoT Thing provisioning then setting up our Thing to connect to AWS IoT.

####Provisioning
Install the depdencies to setup AWS IoT, in this case it's boto3.

```
sudo pip install requirements.txt
```
Configure AWS credentials by following the instructions for [AWS CLI configuration](http://docs.aws.amazon.com/cli/latest/userguide/installing.html).

Provision our Thing:

```
cd thing/ospi
python setup-aws-iot.py
```

If all went well you'll see the following printed to the console:

- Certificate ARN
- Policy ARN
- Thing ARN 

The certificate and keys for use on your Thing will also be saved to:

- opensprinklerpi-private.pem.key
- opensprinklerpi-public.pem.key (unused)
- opensprinklerpi-certificate.pem.crt

_TIP: Use these values if you want to delete the provisioned resources._

####Install
Deploying to a Raspberry Pi Thing is simple, copy the thing/ospi directory onto your Raspberry Pi, then execute the following:

```
sudo python setup.py install
```

If successful you'll have:
-  ```iot``` command available
- sample configuration at **/etc/iot/iot.json**
- systemd unit installed as **iot.service**

####Configure
After successful installation you'll need to configure the IoT client.

Set the endpoint value to your AWS IoT endpoint located within the AWS IoT Dashboard.

You'll need to [download the Verisign ca-certificate](https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem) and save as ca-certificate.pem.crt.

```
curl -o ca-certificate.pem.crt https://www.symantec.com/content/en/us/enterprise/verisign/roots/VeriSign-Class%203-Public-Primary-Certification-Authority-G5.pem
```

Move ca-certificate.pem.crt, opensprinklerpi-private.pem.key and opensprinklerpi-certificate.pem.crt into /etc/iot/. 

If you prefer to keep your certificates and key in an alternative location, you may their path within iot.json.

MD5 your OSPI password and set as ospi-password-hash in /etc/iot/iot.json:

```
echo "yourpassword" | md5
```

Specify your OSPI instance base URL, this would be the URL that you'd load to view it's web page eg. http://raspberry-pi.local:8080 or http://localhost:8080 if you're running the iot client on the same device as OSPI.

Ensure each of the following values in iot.json is modified to suit your setup:

- client-id
- endpoint
- ospi-password-hash
- ospi-base-url


####Running at startup

A systemd unit configuration is deployed to the /lib/systemd/system directory it can be enabled:

```
sudo systemctrl enable iot.service
```

The service can be started immediately with:

```
sudo systemctrl start iot.service
```

###Alexa
Alexa Skill setup is a manual operation however the creation of the Lambda is automated.

####Skill configuration
Create an Alexa skill within [developer.amazon.com](http://developer.amazon.com).
Use INTENT.txt, UTTERANCES.txt for field values within the skill configuration.


####Lambda
Setup the Alexa skill handler:

```
cd controller/alexa
pip install -r requirements.txt -t .
python setup-aws-alexa-lambda.py
```
TIP: The Role ARN and Lambda ARN are printed if you need to delete these resources.

##Testing
1. Open the AWS IoT platform and select "Test"
2. Subscribe to Topic "home/sprinkler"
3. Open Alexa Skill > Test
4. Enter Utterance "turn on my sprinkler for 5 seconds"
5. Confirm a message is received in AWS IoT Platform Test console

##Troubleshooting

If connection fails with a timeout or a certificate error it's likely your AWS IoT certificate isn't setup correctly, please ensure a policy is attached and specifies the appropriate permissions and a Thing is attached.
