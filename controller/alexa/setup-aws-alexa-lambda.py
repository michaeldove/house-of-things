import boto3

ZIP_FILE_NAME = 'lambda.zip'
POLICY_FILE_NAME = 'iam-policy.json'
ASSUME_ROLE_POLICY_FILE_NAME = 'iam-assume-role-policy.json'
ROLE_NAME = 'Basic-Execution-IoT'
FUNCTION_NAME = 'opensprinklerpi-alexa'

def create_zip():
    import os
    import zipfile

    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file))

    zipf = zipfile.ZipFile(ZIP_FILE_NAME, 'w', zipfile.ZIP_DEFLATED)
    zipf.write('sprinkler-alexa.py')
    zipdir('isodate', zipf)
    zipf.close()
    return ZIP_FILE_NAME

def read_file(filename):
    with open(filename, 'rb') as fp:
        return fp.read()

def create_role():
    iam = boto3.client('iam')
    policy_document = read_file(POLICY_FILE_NAME)
    assume_role_policy_document = read_file(ASSUME_ROLE_POLICY_FILE_NAME)
    role_result = iam.create_role(
        RoleName=ROLE_NAME,
        AssumeRolePolicyDocument=assume_role_policy_document
        )
    policy_result = iam.put_role_policy(
        RoleName=ROLE_NAME,
        PolicyName='IoTPubSub',
        PolicyDocument=policy_document
        )
    return role_result['Role']


print "Setting up AWS Alexa Lambda"

zip_file_name = create_zip()
zip_data = read_file(zip_file_name)

role_arn = create_role()['Arn']

print "Role ARN: {}".format(role_arn)


client = boto3.client('lambda')
func_result = client.create_function(
    FunctionName=FUNCTION_NAME,
    Runtime='python2.7',
    Role=role_arn,
    Handler='sprinkler-alexa.lambda_handler',
    Code={'ZipFile': zip_data},
    Description='OpenSprinkler Pi Alexa handler',
    Timeout=10,
    Publish=True)

perm_result = client.add_permission(
    FunctionName=FUNCTION_NAME,
    StatementId='1',
    Action='lambda:invokeFunction',
    Principal='alexa-appkit.amazon.com')

print "Lambda ARN: {}".format(func_result['FunctionArn'])
