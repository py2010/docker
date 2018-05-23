

#docker 2375端口默认不进行客户端安全验证，远程客户端连入2375后都可管理docker



cd ~/.docker

#1.CA
openssl genrsa -out ca-key.pem 4096
openssl req -x509 -sha256 -batch -subj '/CN=sdj' -new -days 9999 -key ca-key.pem -out ca.pem



#2.用CA生成证书
openssl genrsa -out key.pem 4096
openssl req -subj '/CN=Docker' -sha256 -new -key key.pem -out csr.pem

echo subjectAltName = DNS:*.docker.sdj,IP:127.0.0.1 > allow.list
openssl x509 -req -days 365 -sha256 -in csr.pem -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out cert.pem -extfile allow.list

#3.
rm -rf allow.list ca.srl ca-key.pem csr.pem
chmod 400 *.pem
systemctl restart docker



#服务端

docker daemon -H=0.0.0.0:2375    --tlsverify --tlscacert=/root/.docker/ca.pem --tlscert=/root/.docker/cert.pem --tlskey=/root/.docker/key.pem



#客户端

docker -H=tcp://127.0.0.1:2375 --tlsverify --tlscacert=/root/.docker/ca.pem --tlscert=/root/.docker/cert.pem --tlskey=/root/.docker/key.pem info




export DOCKER_HOST=tcp://1.docker.sdj:2375 DOCKER_TLS_VERIFY=1

docker info
