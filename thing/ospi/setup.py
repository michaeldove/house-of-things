from distutils.core import setup
setup(name='iot',
      version='1.0',
      scripts=['iot'],
      requires=['AWSIoTPythonSDK', 'requests'],
      data_files=[('/etc/iot', ['iot.json']),
                  ('/lib/systemd/system', ['iot.service'])]
      )
