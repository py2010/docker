

# https://docs.docker.com/develop/sdk/examples/


import docker
client = docker.DockerClient(base_url='http://192.168.80.238:2375', tls=1)

ser = client.services.create('nginx', name='xyf', constraints=['node.ip==10.2.21.9'],)

container = client.containers.run("bfirsh/reticulate-splines", detach=True)
print container.id


client = docker.from_env()
for container in client.containers.list():
    print container.id


client = docker.from_env()
container = client.containers.get('1eeafff5e6d5')
print container.logs()


client = docker.from_env()
image = client.images.pull("alpine")
print image.id

import docker
client = docker.from_env(timeout=3, environment={'DOCKER_HOST': 'tcp://10.5.0.32:2375'})
i = client.images.list()
ii = i[0]
c = client.containers.list()
cc = c[0]
client.containers.run(image='nginx', name='tt66', network='sdj', detach=1)


# ~/.docker/ca.pem cert.pem key.pem
client = docker.from_env(environment={'DOCKER_HOST': 'tcp://1.docker.sdj:2375', 'DOCKER_TLS_VERIFY': 1})
client.images.list()


client = docker.from_env(environment={'DOCKER_HOST': 'tcp://192.168.80.238:2375', 'DOCKER_TLS_VERIFY': 1})
client.images.list()


import requests
requests.get('https://192.168.80.238:2375', headers={"Host": "1.docker.sdj:2375"}, cert=('/root/.docker/cert.pem', '/root/.docker/key.pem'), verify='/root/.docker/ca.pem')


endpoint = client.api.create_endpoint_config(ipv4_address='192.168.0.111',)

client.api.create_networking_config({'sdj': endpoint})

{'EndpointsConfig': {'sdj': {'IPAMConfig': {'IPv4Address': '192.168.0.111'}}}}

{
    'name': 'tt66',
    'image': 'nginx',
    'command': None,
    'detach': 1,
    'host_config': {'Binds': ['/home/user1/:/mnt/vol2', '/var/www:/mnt/vol1:ro'], 'NetworkMode': 'sdj'},
    'networking_config': {'EndpointsConfig': {'sdj': {'IPAMConfig': {'IPv4Address': '192.168.0.88'}}}}
}


kwargs = {
    'network': ['bridge'],
    'ip': ['1.1.1.1'],
    'mont': ['/var/:/var:ro'],
    'command': ['top'],
    'csrfmiddlewaretoken': ['EWTKg6UElIYeJ6MdKmuPObHoaZLY5X71kCOEBt999cccSoXxiJ8b9DFhaszyMOFy'],
    'image': ['sha256:f6e427c148a766d2d6c117d67359a0aa7d133b5bc05830a7ff6e8b64ff6b1d1d'],
    'name': ['eeeeeee']
}
