#Alexa IoT Sprinker

Integrates OpenSprinkler Pi to the AWS Alexa
so that you can command your sprinkler.


## Flow of messages

This is how your commands are sent the the OSPI server:

Echo -> Alexa -> Lambda -> AWS IoT -> IoT client -> OSPI server


## Project

The project is organised into 2 logical parts, __thing__ and __controller__.
An Alexa is a controller that sends commands, while the RaspberryPi running the IoT client and OSPI server is the thing.

## Deployment

Deploying to a Raspberry Pi Thing is simple, copy the thing/ospi directory onto your Raspberry Pi, then execute the following:

```
sudo python setup.py install
```

If successful you'll have:
-  ```iot``` command available
- sample configuration at **/etc/iot/iot.json**
- systemd unit installed as **iot.service**

After successful installation you'll need to configure the IoT client.

Set the endpoint value to your AWS IoT endpoint located within the AWS IoT Dashboard.

Configure a new AWS IoT Certificate and attach a Policy and Thing, then download the keys and certificates, save as:

- ca-certificate.pem.crt
- certificate.pem.crt
- private.pem.key

move these files into /etc/iot/ the exact location is specified within the iot.json.

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


##Running at startup

A systemd unit configuration is deployed to the /lib/systemd/system directory it can be enabled:

```
sudo systemctrl enable iot.service
```

The service can be started immediately with:

```
sudo systemctrl start iot.service
```

##Troubleshooting

If connection fails with a timeout or a certificate error it's likely your AWS IoT certificate isn't setup correctly, please ensure a policy is attached and specifies the appropriate permissions and a Thing is attached.
