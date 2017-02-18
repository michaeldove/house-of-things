import boto3

THING_NAME = 'opensprinkler-pi'
POLICY_NAME = 'opensprinkler-pi'
PRIVATE_KEY_NAME = 'opensprinklerpi-private.pem.key'
PUBLIC_KEY_NAME = 'opensprinklerpi-public.pem.key'
CERTIFICATE_NAME = 'opensprinklerpi-certificate.pem.crt'
POLICY_FILE_NAME = 'iot-policy.json'

def policy_document():
    with open(POLICY_FILE_NAME, 'r') as fp:
        document = fp.read()
        return document

def write_file(data, file_name):
    with open(file_name, 'w') as fp:
        fp.write(data)

print "Setting up AWS IoT Thing named {}".format(THING_NAME)

client = boto3.client('iot')
thing_result = client.create_thing(thingName=THING_NAME)
cert_result = client.create_keys_and_certificate(setAsActive=False)
policy_result = client.create_policy(policyName=POLICY_NAME,
                                     policyDocument=policy_document())
cert_arn = cert_result['certificateArn']
client.attach_principal_policy(policyName=POLICY_NAME,
                               principal=cert_arn)
client.attach_thing_principal(thingName=THING_NAME,
                              principal=cert_arn)

private_key = cert_result['keyPair']['PrivateKey']
public_key = cert_result['keyPair']['PublicKey']
certificate_pem = cert_result['certificatePem']

write_file(private_key, PRIVATE_KEY_NAME)
write_file(public_key, PUBLIC_KEY_NAME)
write_file(certificate_pem, CERTIFICATE_NAME)

print "Completed setup of Thing with details: "
print "Thing name: {}".format(THING_NAME)
print "Thing ARN: {}".format(thing_result['thingArn'])
print "Certificate ARN: {}".format(cert_arn)
print "Policy name: {}".format(POLICY_NAME)
print "Policy ARN: {}".format(policy_result['policyArn'])
print "Public key file: {}".format(PUBLIC_KEY_NAME)
print "Private key file: {}".format(PRIVATE_KEY_NAME)
print "Certificate file: {}".format(CERTIFICATE_NAME)

client.update_certificate(certificateId=cert_result['certificateId'],
                          newStatus='ACTIVE')
