---------------------Wireguard

Testing the API
------------------- Create a Tenant



curl -X POST http://127.0.0.1:5000/tenants -H "Content-Type: application/json" -d '{
  "name": "tenant1",
  "address": "172.16.0.1/16"
}'


------------------Create a Client


curl -X POST http://127.0.0.1:5000/clients -H "Content-Type: application/json" -d '{
  "name": "client1",
  "address": "172.16.0.2/16"
}'


------------------Add a Peer to Tenant

curl -X POST http://127.0.0.1:5000/tenants/tenant1/peers -H "Content-Type: application/json" -d '{
  "client_name": "client1",
  "endpoint": "192.168.4.128"
}'




--------------------OpenVPN

------------Create a Server



curl -X POST http://127.0.0.1:4000/create_server -H "Content-Type: application/json" -d '{
  "server_name": "myserver",
  "server_ip": "10.8.0.0",
  "server_subnet": "255.255.255.0"
}'


--------------Create a Client


curl -X POST http://127.0.0.1:4000/create_client -H "Content-Type: application/json" -d '{
  "client_name": "client1",
  "endpoint": "myserver",
  "server_name": "myserver"
}'

------------- ---useful commands : 

sudo ss -tulnp | grep :<port>


sudo lsof -i -P -n



sudo netstat -tuln
sudo ss -tuln


tcpdump -i INTERFACE -vvv


-------------------------------------------------------------

sudo openvpn --config /etc/openvpn/client1.conf


--------------

sudo docker run -p 5000:5000 my-flask-app

sudo docker image rm my-wg-app

docker build -t my-wg-app .


sudo docker container exec 0b4d ip a

docker run -it --privileged --net=host YOUR_DOCKER_IMAGE


echo '' | base64 --decode | sudo tee /etc/openvpn/client1.conf > /dev/null
---------------------------------------------- vars in yours pipeline: 

$DOCKER_REGISTRY_USER
$DOCKER_REGISTRY_PASSWORD
$DOCKER_REGISTRY



