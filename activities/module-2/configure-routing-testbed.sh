#!/bin/bash

# Configura con gNMIc (peticiones set) el direccionamiento IP de los enlaces entre
# routers y las rutas estáticas entre las LANs del escenario routing-testbed.
# Ejecutar desde activities/module-2 con el escenario ya desplegado.

cd "$(dirname "$0")"

USER='admin'
PASS='NokiaSrl1!'
PORT=57400

# set_ip <router> <interfaz> <prefijo IP>
set_ip() {
  echo "Configurando $2 = $3 en $1..."
  echo "{\"IF_NAME\": \"$2\", \"IF_IP_PREFIX\": \"$3\"}" | \
    gnmic -a clab-routing-testbed-$1:$PORT -u $USER -p $PASS --skip-verify \
      set --request-file configure_ip_address.yaml --request-vars - || exit 1
}

# set_route <router> <nombre next-hop-group> <IP siguiente salto> <prefijo destino>
set_route() {
  echo "Configurando ruta $4 via $3 en $1..."
  echo "{\"Name_NextHop\": \"$2\", \"IP_NextHop\": \"$3\", \"Target_IP_Prefix\": \"$4\"}" | \
    gnmic -a clab-routing-testbed-$1:$PORT -u $USER -p $PASS --skip-verify \
      set --request-file configure_ip_routing.yaml --request-vars - || exit 1
}

# Direccionamiento de los enlaces entre routers
# r1 <-> r2: 10.0.10.0/30, r1 <-> r3: 10.0.11.0/30, r2 <-> r3: 10.0.12.0/30
set_ip r1 ethernet-1/2 10.0.10.1/30
set_ip r1 ethernet-1/3 10.0.11.1/30
set_ip r2 ethernet-1/2 10.0.10.2/30
set_ip r2 ethernet-1/3 10.0.12.1/30
set_ip r3 ethernet-1/2 10.0.11.2/30
set_ip r3 ethernet-1/3 10.0.12.2/30

# Rutas estáticas hacia las LANs remotas
set_route r1 nh-r1-r2 10.0.10.2 192.168.2.0/24
set_route r1 nh-r1-r3 10.0.11.2 192.168.3.0/24
set_route r2 nh-r2-r1 10.0.10.1 192.168.1.0/24
set_route r2 nh-r2-r3 10.0.12.2 192.168.3.0/24
set_route r3 nh-r3-r1 10.0.11.1 192.168.1.0/24
set_route r3 nh-r3-r2 10.0.12.1 192.168.2.0/24

echo 'Done!'
