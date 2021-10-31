# Notes

Determine DigitalOcean public VM Network configuration:

```bash
HOSTNAME=$(curl -s http://169.254.169.254/metadata/v1/hostname); \
PUBLIC_IPV4=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address); \
NETMASK=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/netmask); \
GATEWAY=$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/gateway); \
echo $HOSTNAME; echo $PUBLIC_IPV4; echo $NETMASK; echo $GATEWAY
```
