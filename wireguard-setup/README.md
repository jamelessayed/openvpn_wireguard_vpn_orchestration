# wireguard


Testing the API
------------------- Create a Tenant



curl -X POST http://192.168.4.128:8080/tenants -H "Content-Type: application/json" -d '{
  "name": "tenant1",
  "address": "172.16.0.1/16"
}'


------------------Create a Client


curl -X POST http://192.168.4.128:8080/clients -H "Content-Type: application/json" -d '{
  "name": "client1",
  "address": "172.16.0.2/16"
}'


------------------Add a Peer to Tenant

curl -X POST http://192.168.4.128:8080/tenants/tenant1/peers -H "Content-Type: application/json" -d '{
  "client_name": "client1",
  "endpoint": "192.168.4.128"
}'

