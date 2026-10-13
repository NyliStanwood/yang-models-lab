
#### 1.2.2. Análisis del tráfico de gestión en gNMI

A continuación, veremos cómo capturar el tráfico de señalización intercambiado entre cliente y servidor al realizar operaciones mediante el protocolo de gestión gNMI. Como ya hemos visto en la teoría, gNMI utiliza llamadas gRPC sobre una conexión HTTP/2 para la comunicación entre cliente y servidore. Además, esta comunicación puede estar cifrada mediante el protocolo TLS y los mensajes gNMI están codificados utilizando el formato binario Protocol Buffers (Protobuf). Veremos a continuación cómo capturar y analizar el tráfico asociado a consultas realizadas con el protocolo gNMI. Veremos a continuación cómo identificar en la captura el tráfico de gestión gNMI, así como descifrar y decodificar los mensajes para facilitar su análisis.

Para ello, dispone de un *script* [`clab-capture-traffic.sh`](../activities/module-1/clab-capture-traffic.sh) para poder capturar tráfico con Wireshark en las interfaces de red de los contenedores desplegados con el escenario de red de Containerlab. Se incluye a continuación el menú de ayuda para poder hacer uso del script:
```bash
Usage:
  ./clab-capture-traffic.sh <container_name> <interface>
    to open capture on specific container interface
    Valid values:
      <container_name>: clab-srlinux-testbed-pc1 clab-srlinux-testbed-pc2 clab-srlinux-testbed-r1 clab-srlinux-testbed-r2
      <container_interface>: e1-1 e1-2 mgmt0 for router containers, eth0 eth1 for host containers
```

En concreto, para capturar el tráfico de gestión gNMI deberá utilizar la interfaz de gestión de los routers (es decir, `mgmt0`). Por ejemplo, para capturar tráfico en la interfaz de gestión del router `r1`, el comando a ejecutar sería el siguiente:
```bash
./clab-capture-traffic.sh clab-srlinux-testbed-r1  mgmt0
```
TODO =====> redo capture of traffic 1 by 1


Mientras está activa la captura de tráfico, realizaremos las consultas con gNMI ejecutadas anteriormente para obtener las capacidades del router y para consultar el estado operativo de una de sus interfaces de red. Incluiremos la opción `--log-tls-secret` en el comando de `gNMIc`, de modo que se registren en un fichero los secretos de la sesión TLS establecida en la conexión HTTP/2, que posteriormente permitirá descifrar la comunicación  entre cliente y servidor gNMI. Por cada operación consultada con gNMI se generará un fichero de secretos TLS con el nombre  `<container_name>:57400.tlssecret.log`. El fichero generado con la primera consulta renómbrelo como `<container_name>-capabilities.tlssecret.log` mientras que el fichero generado con la segunda consulta renómbrelo como `<container_name>-get-rpc.tlssecret.log`.

>**Nota:** Por defecto, el fichero con los secretos TLS se genera siempre con el mismo nombre `<container_name>:57400.tlssecret`, por lo que debe renombrarlo justo después de cada operación que realice con gNMIc, de lo contrario se sobreescribirá su contenido.

Una vez completadas las consultas y guardados los ficheros de secretos TLS de cada una de ellas, pare la captura de tráfico y guárdela con el nombre `gnmi-traffic.pcap` en la máquina virtual.

Al analizar el tráfico capturado, encontraremos tráfico TLS producto de las operaciones realizadas con gNMI. Para descifrarlo, tendremos que incluir el fichero de secretos TLS correspondiente. En primer lugar, seleccionaremos el fichero asociado a la operación de extracción de capacidades. Para ello, iremos al panel de preferencias de Wireshark yendo a la barra de herramientas y seleccionando *"Edit > Preferences..."*. Una vez en el panel de preferencias, en la barra lateral desplegaremos la lista de protocolos y seleccione TLS. Vaya a la opción *"(Pre)-Master-Secreto log filename"* y pulsando en *"Browse..."* seleccione el fichero con los secretos TLS asociados. Mantendremos el resto de opciones marcadas por defecto y pulse el botón de *OK*.

Una vez configurado el fichero de secretos TLS, podremos comprobar que el tráfico TLS se ha descifrado y que podemos visualizar los paquetes HTTP/2 y gRPC correspondientes a las operaciones de gestión gNMI. Como ya se ha introducido anteriormente, las llamadas gRPC utilizan Protocol Buffers (Protobuf) para la codificación binaria de los mensajes, pese a que los datos puedan ser solicitados y ser expresados en formato JSON. A continuación, decodificaremos los mensajes gRPC codificados en Protobuf para facilitar la interpretación de los datos intercambiados entre cliente y servidor. Para ello, vaya de nuevo al panel de preferencias de Wireshark y seleccione Protobuf en la lista de protocolos. Vaya entonces a la opción *"Protobuf search paths"* y pulse la opción *"Edit..."*. Pulsando el botón `+` y en la nueva fila generada en la tabla superior haga doble *click* en la celda debajo de *"Protobuf source directory"* y pulse en los `...` seleccionando el directorio `/home/upm/gnmi4wireshark`. Luego, marque la casilla de la celda de la derecha bajo la columna *"Load all files"*. Dale al botón de OK. En las preferencias de Protocol Buffers mantenga los valores marcados por defecto y seleccione de nuevo el botón OK.

>**Nota:** En `/home/upm/gnmi4wireshark` se encuentran los ficheros en formato .proto que permiten decodificar los mensajes en Protobuf intercambiados por gNMI. Estos ficheros .proto han sido obtenidos de la siguiente fuente de información: https://github.com/hellt/gnmi4wireshark.

:point_right: **Pregunta 6:** Busque primero los paquetes HTTP/2 y gRPC asociados a la operación gNMI de consulta de capacidades. Incluya una captura de pantalla del paquete HTTP/2 en la memoria y determine aquellos campos o cabeceras asociados a los parámetros de conexión para la consulta establecida mediante gNMI. Para la respuesta, encuentre el paquete gRPC del mensaje de capacidades resultante y determine la cabecera *Protocol Buffers* con los campos asociados a la versión de gNMI usada, la lista de modelos YANG implementados por el servidor y los formatos de codificación consultados, incluyendo una captura de pantalla representativa en la memoria. Describa brevemente la información mostrada en las capturas de pantalla.

:point_right: **Pregunta 7:** Repita el proceso para la operación GET de consulta de estado de la interfaz del router. Ahora, sobre la misma captura de tráfico, sólo tendrá que cambiar el fichero del secretos TLS asociado a la operación, pudiendo mantener la configuración de decodificación de Protobuf. Encuentre el paquete gRPC original de la petición GET y, yendo a la cabecera *Protocol Buffers*, determine los campos del mensaje e incluya una captura de pantalla asociada en la memoria. Encuentre luego el paquete gRPC de la respuesta y busque en la cabecera *Protocol Buffers* el mensaje con la respuesta asociada a la petición GET, incluyendo captura de pantalla representativa en la memoria. Describa brevemente la información mostrada en las capturas de pantalla.

>**Nota:** Incluya tanto las capturas de tráfico como los ficheros de secretos TLS utilizados para dar respuesta a las **Preguntas 6 y 7** en la entrega asociada a esta práctica.

Una vez terminada la actividad, destruya el escenario de red virtualizado de Containerlab mediante la ejecución del siguiente *script*:
```bash 
./destroy-srlinux-testbed.sh
```

## 2. Utilidades para examinar topología de red y configuración de red basada en modelos con gNMI   

En esta segunda actividad, se desplegará un nuevo escenario de red virtualizado con Containerlab pero su configuración de red estará incompleta. El objetivo será utilizar las capacidades del protocolo gNMI para configurar remotamente los equipos de la red. La configuración a completar será relativa al direccionamiento y encaminamiento IP entre los routers del escenario desplegado.

Además, como apoyo a esta actividad, previamente se analizarán utilidades para examinar mejor la topología de red desplegada y facilitar así la configuración de la red.

Para empezar esta actividad, acceda al directorio [`module-2`](../activities/module-2/) del repositorio de trabajo y ejecute el siguiente *script* para arrancar y configurar el escenario de red virtualizado de Containerlab que utilizaremos:
```bash 
./deploy-routing-testbed.sh 
```

Una vez desplegado el escenario, evalúe la topología de red y la configuración de red realizada en el escenario. Para ello, analice primero el *script* de despliegue, determinando la plantilla en formato YAML que especifica la interconexión de los equipos que conforman el escenario de red, así como los archivos de configuración utilizados para arrancar los equipos Nokia SR Linux utilizados con una configuración base. Además, analice la configuración extra realizada en el *script* de despliegue para la configuración de direccionamiento y encaminamiento IP en los *hosts* del escenario. Para hallar el diagrama de la topología de red puede ayudarse de dos utilidades de Containerlab:
- Utilizar la [extensión de VS Code para Containerlab](https://marketplace.visualstudio.com/items?itemName=srl-labs.vscode-containerlab) que, entre otras cosas, permite representar gráficamente la topología de red de un escenario de Containerlab desplegado.
- Utilizar la opción `graph` de Containerlab para proporcionar una representación gráfica de la topología de un escenario de especificación YAML definido a través de un servidor web integrado. Para ello, ejecute el siguiente comando:
  ```bash 
  containerlab graph --topo routing-testbed.yaml
  ```

Además, utilizaremos una aplicación Java que integra la librería [`YANG Tools`](https://github.com/opendaylight/yangtools) para normalizar datos del escenario de red desplegado según modelos YANG de referencia del IETF definidos en la [RFC 8345](https://www.rfc-editor.org/info/rfc8345). Para ejecutar la aplicación, introduzca el siguiente comando:
```bash 
java -jar topology-driver-1.0.jar /tmp/.clab/clab-routing-testbed/topology-data.json topology.json topology.xml 
```

Examine la salida estándar que devuelve la ejecución de la aplicación, así como los ficheros `topology.json` y `topology.xml` generados, analizando su contenido.

:point_right: **Pregunta 8:** Una vez analizado el nuevo escenario de red desplegado, añada en la memoria una breve descripción del mismo apoyándose en el uso de capturas de pantalla si lo desea. ¿Qué función realiza la aplicación Java evaluada? ¿Qué utilidad podría tener para un controlador de red SDN que controle y gestión equipos con soporte para YANG? Justifique sus respuestas.

Como se ha introducido y se habrá verificado en el análisis previo realizado del escenario de red desplegado, falta por configurar el direccionamiento IP del las interfaces que interconectan los routers, así como el encaminamiento IP para permitir la conectividad entre los clientes o hosts extremos de la red. Para completar esta configuración realizaremos consultas de tipo *`set`* con el cliente `gNMIc`. 

Entre las opciones del cliente `gNMIc` para realizar solicitudes de tipo *`set`*, destaca la posibilidad de utilizar plantillas en formato YAML parametrizables y reutilizables que permitan simplificar y automatizar el proceso de configuración (para más detalles revise el apartado [*Templated Set Request file*](https://gnmic.openconfig.net/cmd/set/#templated-set-request-file) de la documentación de `gNMIc` para solicitudes de tipo *`set`*). Justo utilizaremos este tipo de plantillas para definir la estructura de configuración del direccionamiento IP y del encaminamiento IP de los routers del escenario. Tenemos, por tanto, dos plantillas diferentes: (1) [`configure_ip_address.yaml`](../activities/module-2/configure_ip_address.yaml) y (2) [`configure_ip_routing.yaml`](../activities/module-2/configure_ip_routing.yaml). Analizando estas plantillas, encontrará variables de entrada cuyos valores podrán ser parametrizados. Veamos cómo hacer esto. 

La solución recomendada es ejecutar el comando de `gNMIc` de tipo *`set`* indicando previamente los pares variable-valor necesarios para la plantilla de solicitud en formato JSON. Se muestra a continuación un ejemplo genérico de ejecución del comando `gNMIc` para la configuración de direccionamiento IP de un router:
```bash 
echo '{"IF_NAME": "...", "IF_IP_PREFIX": "..."}' | gnmic -a <container_name>:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_address.yaml --request-vars -
```
>**Nota:** Deberá sustituir los `...` por el valor adecuado.

Alternativamente, puede definir archivos de tipo JSON o YAML que incluyan la especificación de los pares variable-valor a utilizar por la plantilla en cada solicitud `gNMIc` de tipo *`set`*. Se incluye un ejemplo de los ficheros de especificación de variable-valor, primero en formato JSON y luego en formato YAML, para las variables necesarias en la plantilla `configure_ip_address.yaml`.
```bash 
# Ejemplo de fichero con extensión .json de definición de variables
{ 
  "IF_NAME": "...", 
  "IF_IP_PREFIX": "..."
}
```

```bash 
# Ejemplo de fichero con extensión .yaml de definición de variables
IF_NAME: ...
IF_IP_PREFIX: ...
```

Teniendo en cuenta esta forma alternativa de definir los valores de las variables a utilizar por la plantilla de configuración, se muestra a continuación un ejemplo genérico de ejecución del comando de `gNMIc` de tipo *`set`* para la configuración de direccionamiento IP de un router:
```bash 
gnmic -a <container_name>:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_address.yaml --request-vars <fichero JSON/YAML de definición de variables>
```
>**Nota:** El problema de esta alternativa es que deberá definir archivos JSON/YAML específicos por cada ejecución de comandos de configuración de tipo *`set`* con `gNMIc`.

Para facilitar la tarea de cómo definir las variables necesarias para parametrizar los valores de las plantillas de configuración a usar en las consultas  de tipo *`set`* realizadas con `gNMIc`, puede analizar los modelos YANG propietarios de Nokia SR Linux requeridos a los que apuntan los *paths* incluidos en las plantillas. 

Para la configuración del direccionamiento IP asociada a las interfaces de red se utilizan los modelos YANG `srl_nokia-interfaces@2026-07-31.yang` (visto anteriormente en `module-1`) y `srl_nokia-if-ip@2026-07-31.yang` que extiende el modelo YANG anterior para proporcionar información adicional relativa a direccionamiento IPv4 e IPv6. Para ver la estructura en forma árbol de ambos modelos YANG combinados puede utilizar la herramienta *pyang* ejecutando el siguiente comando:
```bash
pyang -f tree srl_nokia-interfaces@2026-07-31.yang srl_nokia-if-ip@2026-07-31.yang
```

Para la configuración del encaminamiento IP asociada se utiliza el modelo YANG `srl_nokia-network-instance@2026-07-31.yang`. Este modelo proporciona información relativa a `network-instance` que es la utilidad que tiene el sistema operativo de red de Nokia SR Linux para disponer de múltiples instancias de tablas de encaminamiento coexistiendo en un router al mismo tiempo, concepto conocido como *Virtual Router and Forwarding* (VRF). En este laboratorio, utilizaremos la *network-instance* *default* para trabajar con la tabla de encaminamiento por defecto de los routers. Este modelo YANG importa otros dos modelos de interés: `srl_nokia-static-routes@2026-07-31.yang` que incluye la información para definir el prefijo destino de las rutas por defecto a configurar y `srl_nokia-next-hop-groups@2026-07-31.yang` que incluye información sobre la dirección IP de siguiente salto de las rutas. Vuelva a utilizar la herramienta *pyang* para ver la estructura en forma árbol de ambos modelos YANG combinados, ejecutando el siguiente comando:
```bash
pyang -f tree srl_nokia-static-routes@2026-07-31.yang srl_nokia-next-hop-groups@2026-07-31.yang
```

Para la configuración de direccionamiento IP en los enlaces de interconexión entre routers, se propone el siguiente plan de direccionamiento:

 | **Enlace** | **Dirección IP de subred**  |
|-----------------|----------------|
| **r1<->r2**        | 10.0.10.0/30       | 
| **r1<->r3**        | 10.0.11.0/30       |
| **r2<->r3**        | 10.0.12.0/30       |

>**Nota:** Los enlaces de interconexión entre routers se establecen entre las interfaces de red `ethernet-1/2` y `ethernet-1/3`.

Aparte, los routers tienen interfaces de red `ethernet-1/1` asociadas a la red LAN que los conecta con los hosts pertenecientes a dicha red. Observe cómo los equipos de red (tanto routers como hosts) sí tienen configurado el direccionamiento IP de sus interfaces de red conectados a dichas LANs. Además, observe cómo los hosts tienen configurado al router de su LAN como *gateway* por defecto. A continuación, se muestran las direcciones de subred asociadas a las 3 LANs del escenario de red:

 | **LAN** | **Dirección IP de subred**  |
|-----------------|----------------|
| **LAN 1 (r1)**        | 192.168.1.0/30       | 
| **LAN 2 (r2)**        | 192.168.2.0/30       |
| **LAN 3 (r3)**        | 192.168.3.0/30       |

Establecidos los planes de direccionamiento anteriores, tendrá que configurar rutas de encaminamiento estáticas en cada uno de los routers para poder tener conectividad IP punto a punto entre las 3 LANs del escenario de red.

:point_right: **Pregunta 9:** Teniendo en cuenta estas directrices, deberá de definir un *shell script* general que permita automatizar las ejecuciones de los comandos de `gNMIc` de tipo *`set`* para la configuración de direccionamiento y encaminamiento IP de todos los routers del escenario. Incluya el *script* en la entrega asociada a la práctica. Realice además pruebas de conectividad punto a punto entre los contenedores de los hosts extremos para verificar que la configuración de red es exitosa. Incluya captura de alguna de estas pruebas de conectividad en la memoria.

>**Nota:** Para comprobar las configuraciones establecidas con gNMI, puede realizar consultas de tipo *`get`* con *paths* de consultas hacia la información de configuración de direccionamiento y encaminamiento IP. Para consultas sobre la configuración de direccionamiento IP, puede reaprovechar el comando del cliente `gNMIc` realizada en el `module-1` anterior. Para las consultas sobre la configuración de encaminamiento IP, puede utilizar el *script* [`gnmic-get-routing-config.sh`](../activities/module-2/gnmic-get-routing-config.sh) proporcionado en `module-2`. Este *script* consulta toda la información de encaminamiento del equipo de red en la *network-instance* por defecto. A la hora de ejecutarlo, tiene que especificar el nombre del router a consultar.

>**Nota:** Adicionalmente, puede comprobar la configuración de direccionamiento y encaminamiento IP establecida accediendo directamente a la consola CLI nativa de los routers (opción `sr_cli`). Una vez dentro de la CLI propia de Nokia SR Linux, dispone de dos comandos de verificación: (1) `show interface` para ver el estado y configuración de la interfaces de red habilitadas; y (2) `show network-instance default ipv4 route` para ver el estado y configuración de rutas de reenvío IPv4 establecidas en la tabla de encaminamiento por defecto del router.

:bulb: **Pregunta 10 (Opcional):** Como parte opcional, se plantea capturar y analizar el tráfico para una de las operaciones de configuración de red realizadas con gNMI. Siguiendo la metodología utilizada para las capturas de tráfico realizadas en el `module-1`, capture tráfico en la interfaz de gestión de uno de los routers Nokia SR Linux mientras realiza uno de los comandos de tipo *`set`* con `gNMIC`. No se olvide de incluir ahora la opción`--log-tls-secret` al comando de `gNMIc` para que registre en un fichero los secretos de la sesión TLS. Renombre el fichero generado con la consulta como `<container_name>-edit-config-rpc.tlssecret.log`. Para analizar la captura de tráfico obtenida, sólo tendrá que cambiar el fichero de secretos TLS asociado a la operación, pudiendo mantener la configuración de decodificación de Protobuf. Encuentre el paquete gRPC original de la petición de configuración y, yendo a la cabecera *Protocol Buffers*, determine los campos del mensaje e incluya una captura de pantalla asociada en la memoria. Encuentre luego el paquete gRPC de la respuesta y busque en la cabecera *Protocol Buffers* el mensaje que determine la respuesta exitosa asociada a la configuración del equipo, incluyendo captura de pantalla representativa en la memoria. Describa brevemente la información mostrada en las capturas de pantalla. Incluya en la entrega de la práctica tanto la captura de tráfico (renómbrela como `<container_name>-edit-config-rpc.pcap`) como el fichero de secretos TLS asociado.

>**Nota:** Para capturar el tráfico de gestión gNMI dispone de una versión del *script* [`clab-capture-traffic.sh`](../activities/module-2/clab-capture-traffic.sh) que permite capturar tráfico con Wireshark en las interfaces de red de los contenedores desplegados con Containerlab para el escenario de red del `module-2`.

Una vez terminada la actividad **no destruya** el escenario de red desplegado con Containerlab pues servirá de base para la última actividad de la práctica.

## 3. *Model-Driven Telemetry* con gNMI

En esta última actividad, tomando el escenario de red de la actividad anterior como base, analizaremos las posibilidades del protocolo gNMI para realizar operaciones de subscripción sobre datos de estado operativo y de estadísticas de telemetría de red que permitan desencadenar notificaciones periódicas o basadas en cambios de estado. En definitiva, esta actividad nos permitirá evaluar mecanismos de telemetría de red basada en modelos YANG o *Model-Driven Telemetry*.

En primer lugar, determinaremos cómo realizar operaciones de subscripción básicas con `gNMIc` que muestren las notificaciones generadas por salida estándar. Además, analizaremos el tráfico de gestión relativo a las notificaciones obtenidas mediante Wireshark.

En segundo lugar, configuraremos un sistema de telemetría que permita gestionar los datos monitorizados de todas las interfaces de uno de los routers producto de nuevas operaciones de subscripción desencadenadas. Para ello, propagaremos la salida de las notificaciones resultantes de las operaciones de subscripción tanto en un bus de mensajes basado en la solución de [`Apache Kafka`](https://kafka.apache.org/) como en una base de datos de series temporales como [`Prometheus`](https://prometheus.io/), dependiendo de ciertas condiciones de los tipos de subscripción definidas.

Para empezar esta actividad, acceda al directorio [`module-3`](../activities/module-3/).

Para la primera parte de la actividad, determinaremos cómo realizar operaciones de tipo *`subscribe`* con el cliente `gNMIC`. Aunque se pueden definir en una única línea de comando, utilizaremos de nuevo una plantilla YAML para la especificación de las subscripciones a realizar. La estructura de la plantilla se encuentra en el archivo [`gnmic-subscription.yaml`](../activities/module-3/gnmic-subscription.yaml) y tiene el siguiente contenido:
```bash
targets:
  router1:
    # gNMI target address; CLI flag `--address`
    address: "<container_name>:57400"
    # gNMI target user name; CLI flag `--username`
    username: admin
    # gNMI target user password; CLI flag `--password`
    password: NokiaSrl1!
    # do not verify the target certificate when using tls; CLI flag `--skip-verify`
    skip-verify: true
    log: true
    # log file location; CLI flag `--log-file`
    log-file: /tmp/gnmic.log
    subscriptions:
      - r1_traffic_stats_e1-1
      - r1_interface_status_e1-1

subscriptions:
  r1_traffic_stats_e1-1:
    paths:
       - "..."
    stream-mode: sample
    sample-interval: 5s
    encoding: JSON_IETF
    outputs: 
      - stdout-output
  r1_interface_status_e1-1:
    paths:
      - "..."
      - "..."
    stream-mode: on-change
    encoding: JSON_IETF
    outputs: 
      - stdout-output

outputs:
  stdout-output:
    type: file # output type
    file-type: stdout # or stderr
    # Exported msg format, json, protojson, prototext, proto, event
    format: event
```

Deberá cambiar los valores `<container_name>` y `<...>` convenientemente. En el apartado *paths* de la subscripción periódica `r1_traffic_stats` indicada, incluya el *path* que apunte las estadísticas de la interfaz de red `ethernet-1/1` del router `r1` del escenario (es decir, nodo de datos general de estadísticas perteneciente modelo YANG de Nokia SR Linux para datos de configuración y estado de interfaces de red visto y utilizado en actividades anteriores). En el apartado *paths* de la subscripción basada en cambios `r1_port_status`  indicada, incluye dos *paths*, uno que apunte al estado operativo de la interfaz de red `ethernet-1/1` y el otro que apunte al estado administrativo de la interfaz `ethernet-1/1` (determine para ello los nodos de datos relativos pertenecientes al modelo YANG de Nokia SR Linux para datos de configuración y estado de interfaces de red visto anteriormente).

>**Nota:** Al incluir el índice de los *paths* donde se apunta al nombre de la interfaz, no incluya el nombre entre `""` o `''`.

Una vez definido el fichero de configuración de subscripciones, el comando `gNMIc` necesario para ejecutar la operación de tipo *`subscribe`* sería el siguiente:
```bash 
gnmic subscribe --config gnmic-subscription.yaml
```

Verifique si la operación de subscripción funciona según lo esperado y si recibe notificaciones periódicas o basadas en cambios de estado mientras tenga activo el comando. Para provocar cambios de estado que desencadenen notificaciones relativas a la subscripción `r1_port_stats` definida, se propone realizar una consulta con el cliente `gNMIc` de tipo *`set`* que modifique el estado administrativo de la interfaz. Para este tipo de acción con gNMIc, vale con realizar un comando de tipo *`set`* que incluya el *path* que apunte al nodo de datos que se quiere actualizar de un modelo YANG y el valor apropiado. Se incluye un ejemplo general del comando a continuación:
```bash 
gnmic -a <container_name>:57400 -u admin -p NokiaSrl1! --skip-verify set --update-path "<path>" --update-value <value>
```
, donde deberá cambiar los valores de `<container_name>`, `<path>` y `<value>` acordemente. Verifique que actualizando el estado administrativo de la interfaz de red llegan nuevas notificaciones de cambios de estado operativo y administrativo. Verifique además que, dependiendo del estado administrativo configurado y de la interfaz asociada, pierde o recupera conexión en el escenario de red desplegado.

:point_right: **Pregunta 11:** Teniendo en cuenta estas directrices, incluya en la memoria capturas de pantalla representativas que muestren la generación de notificaciones periódicas y basadas en cambios relativas a las subscripciones realizadas con gNMI, describiendo brevemente los resultados obtenidos. Incluya en la entrega asociada a la práctica la plantilla YAML modificada de especificación de las subscripciones. Incluya en la memoria también el comando de `gNMIc` de tipo *`set`* utilizado para cambiar el estado operativo de la interfaz de red del router.

:bulb: **Pregunta 12 (Opcional):** Como parte opcional, se plantea capturar y analizar el tráfico para operaciones de subscripción realizadas con gNMI y notificaciones asociadas. Siguiendo la metodología utilizada para las capturas de tráfico realizadas en el `module-1`, capture tráfico en la interfaz de gestión del router `r1` mientras realiza la ejecución del comando de tipo *`subscribe`* con `gNMIc` y mantenga la captura hasta que reciba alguna notificación periódica de las estadísticas de la interfaz del router monitorizada. No se olvide de incluir ahora la opción `--log-tls-secret` al comando de `gNMIc` para que registre en un fichero los secretos de la sesión TLS. Renombre el fichero generado con la consulta como `<container_name>-subscribe-rpc.tlssecret.log`. Para analizar la captura de tráfico obtenida, sólo tendrá que cambiar el fichero del secretos TLS asociado a la operación, pudiendo mantener la configuración de decodificación de Protobuf. Encuentre el paquete gRPC original de la operación de subscripción y, yendo a la cabecera *Protocol Buffers* determine los campos del mensaje e incluya una captura de pantalla asociada en la memoria. ¿Cuantas cabeceras de tipo *GRPC Message* y *Protocol Buffers* hay y por qué? Justifique su respuesta. Encuentre luego el paquete gRPC de alguna notificación cursada y busque de nuevo en la cabecera *Protocol Buffers* el mensaje que determine la información asociada, incluyendo otra captura de pantalla representativa en la memoria. Describa brevemente la información mostrada en las capturas de pantalla. Incluya en la entrega de la práctica tanto la captura de tráfico (renómbrela como `<container_name>-subscribe-rpc.pcap`) como el fichero de secretos TLS asociado.

>**Nota:** Para capturar el tráfico de gestión gNMI utilice la versión del *script* [`clab-capture-traffic.sh`](../activities/module-2/clab-capture-traffic.sh) del `module-2` que permite poder capturar tráfico con Wireshark en las interfaces de red de los contenedores desplegados con el escenario de red de Containerlab.

En el ejemplo de creación de subscripciones anterior, se devuelve la salida de las notificaciones de telemetría generadas por salida estándar. Sin embargo, `gNMIc` permite transmitir el contenido de las notificaciones a servicios externos. Como se ha introducido al inicio de esta actividad, en esta práctica veremos cómo propagar el contenido de las notificaciones a servicios como Apache Kafka y Prometheus. El escenario resultante al que queremos llegar es el siguiente:

![SR Linux telemetry scenario](images/routing-testbed-telemetry-solution.png)

Apache Kafka funciona como un sistema de mensajería mediante mecanismo de publicación/subscripción, donde los datos de las notificaciones serán publicados en canales de datos (denominados *topics*) a los que también nos podremos subscribir para consultar esos mismos datos. Sin embargo, Prometheus funciona como un mecanismo de monitorización basada en *polling* que sondea periódicamente métricas de monitorización externas según un intervalo de tiempo preconfigurado. Para nuestro caso de aplicación, el cliente `gNMIc` va a ser configurado para exponer las notificaciones que se vayan generando como métricas compresibles para Prometheus en un *endpoint* HTTP que el propio servicio de Prometheus podrá consultar luego periódicamente.

Para el caso de Prometheus, se obtendrán notificaciones periódicas cada 10 segundos sobre las estadísticas de telemetría de todas las interfaces de red del router `r1`. Para Kafka, se enviarán notificaciones periódicas cada 5 segundos para las estadísticas de telemetría de todas las interfaces del router `r1` y notificaciones basadas en cambios para los datos de estado operativo y administrativo de las interfaces del router `r1`. De esta forma, la definición de las subscripciones y los *paths* de consulta serán muy similares a a los utilizados en el apartado anterior.

Para completar este proceso, genere una nueva versión de la plantilla de especificación de subscripciones denominada `gnmic-subscription-kafka-prometheus.yaml` partiendo de la plantilla `gnmic-subscription.yaml` que utilizó en el apartado anterior. En ella tendrá que configurar los tipos de subscripción indicados bajo la sección `subscriptions`, teniendo en cuenta que en el apartado `paths` se pueden incluir tantos *paths* como se deseen para cubrir la subscripción a todas las interfaces de red del router `r1`. Para que se propague la  salida de las notificaciones a Kafka o Prometheus, incluya la siguiente especificación de `outputs` en la plantilla YAML de creación de subscripciones:
```bash
outputs:
  kafka-output-traffic-stats:
    type: kafka
    address: kafka:9092
    topic: traffic-stats
    # Exported msg format, json, protojson, prototext, proto, event
    format: event
  kafka-output-interface-status:
    type: kafka
    address: kafka:9092
    topic: interface-status
    # Exported msg format, json, protojson, prototext, proto, event
    format: event
  prom-output:
    type: prometheus
    listen: "gnmic:9804"
    service-registration:
      address: consul-agent:8500
```
Deberá configurar las subscripciones definidas para que apunten a la salida apropiada. Tenga en cuenta también que en el apartado `outputs` para cada tipo de subscripción definida en la sección `subscriptions`, puede asociar tantas salidas como desee. En el caso de Kafka, se configuran dos salidas, una para publicar las estadísticas de telemetría de tráfico en un *topic* denominado `traffic-stats` y otra para publicar notificaciones del estado operativo y administrativo de las interfaces  de red en un *topic* denominado `interface-status`.

Una vez configurada la plantilla, veamos cómo arrancar el sistema de telemetría completo para probar su funcionalidad. En el directorio `module-3` encontrará un fichero [`docker-compose.yaml`](../activities/module-3/docker-compose.yaml) que define y configura los diferentes servicios dependientes para poder desplegar el sistema de telemetría como microservicios basados en contenedores Docker, incluido el cliente de `gNMIC`. Para poder comunicarse directamente con el escenario de red de Containerlab, los servicios contenerizados del sistema de telemetría utilizan la misma red de gestión de Docker que los equipos de la red. Para poder desplegar los servicios del sistema de telemetría ejecute el siguiente comando:
```bash
docker compose -f docker-compose.yaml up -d
```

En caso de errores en el despliegue o por necesidad, puede parar y eliminar los contenedores del sistema de telemetría mediante el siguiente comando:
```bash
docker compose -f docker-compose.yaml down
```

Una vez arrancado el sistema de telemetría, verificaremos que las notificaciones llegan convenientemente a los servicios destinatarios. 

Para Prometheus, abra en un navegador web de la máquina virtual su interfaz gráfica mediante la URL `http://localhost:9090`. En ella deberá poder consultar las métricas expuestas por gNMI a partir de las notificaciones que sean generadas, viendo el potencial de la herramienta `gNMIc` para procesar y transformar los datos de notificaciones según el servicio destinatario. Busque también la opción de representar gráficamente la evolución de las métricas consultadas a lo largo del tiempo.
>**Nota:** Si tiene curiosidad, para ver el formato en crudo de exposición de las notificaciones generadas por el protocolo gNMI como métricas resultantes accesibles desde Prometheus, entre a uno de los contenedores que hacen de *hosts* o clientes en el escenario de red y realice una consulta mediante la herramienta `curl` a la URL  `http://gnmic:9804/metrics`.

Para Kafka, abriremos una terminal en el contenedor Docker asociado y nos subscribiremos al *topic* `traffic-stats` o `interface-status`, según el tipo de notificaciones de telemetría que deseemos consumir. Para ello, ejecute el siguiente comando:
```bash
docker exec -it kafka kafka-console-consumer.sh --topic <topic_name> --bootstrap-server kafka:9092 --from-beginning
```
, siendo `<topic_name>` `traffic-stats` o `interface-status`.

:point_right: **Pregunta 13:** Teniendo en cuenta las directrices dadas, incluya en la memoria capturas de pantalla representativas que muestren la generación de notificaciones tanto en Prometheus como en Kafka relativas a las subscripciones configuradas con gNMI, describiendo brevemente los resultados obtenidos. En el caso de Kafka, incluya ejemplos de capturas donde se vean tanto notificaciones periódicas de las estadísticas de tráfico como notificaciones basadas en cambios del estado operativo y administrativo de las interfaces de red. Para el caso de Prometheus, incluya además una captura de pantalla de una gráfica que represente la evolución temporal de las métricas de bytes de entrada y bytes de salida por todas las interfaces de red monitorizadas del router `r1`. Incluya en la entrega asociada a la práctica la plantilla YAML modificada de especificación de las subscripciones (es decir, el fichero `gnmic-subscription-kafka-prometheus.yaml`). 

Una vez terminada esta actividad, puede destruir el escenario de red virtualizado de Containerlab mediante la ejecución del siguiente *script* localizado en el directorio `module-2`:
```bash
./destroy-srlinux-testbed.sh
```

## 4. Conclusiones
Incluya en la entrega un apartado de conclusiones con su valoración personal de la práctica, incluyendo los posibles problemas que haya encontrado y sus sugerencias. 

## 5. Entrega
Para evaluar la práctica, debe realizar una memoria en la que se dé respuesta a las preguntas planteadas en el enunciado. En la entrega asociada al espacio de Moodle de la asignatura deberá incluir tanto la memoria como los *scripts* y las capturas de tráfico solicitados a lo largo del enunciado.

# Referencias
1. B. Claise, J. Clarke, and J. Lindblad, Network Programmability with YANG: The Structure of Network Automation with YANG, NETCONF, RESTCONF, and gNMI. Addison-Wesley Professional, 2019. Available: https://www.oreilly.com/library/view/network-programmability-with/9780135180471/.
2. M. Björklund, The YANG 1.1 Data Modeling Language, RFC 7950, Aug. 2016. doi: [10.17487/RFC7950](https://www.rfc-editor.org/info/rfc7950).
3. R. Enns, M. Björklund, A. Bierman, and J. Schönwälder, Network Configuration Protocol (NETCONF), RFC 6241, Jun. 2011. doi: [10.17487/RFC6241](https://www.rfc-editor.org/info/rfc6241).
4. OpenConfig Community, gRPC Network Management Interface (gNMI). [Online]. Available: https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-specification.md
5. Bjorklund, M. and L. Berger, Ed., YANG Tree Diagrams, RFC 8340, Mar. 2018. doi. [10.17487/RFC8340](https://www.rfc-editor.org/info/rfc8340).
6. Clemm, A., Medved, J., Varga, R., Bahadur, N., Ananthakrishnan, H., and X. Liu, A YANG Data Model for Network Topologies, RFC 8345, Mar. 2018. doi: [10.17487/RFC8345](https://www.rfc-editor.org/info/rfc8345).
7. Containerlab. Available: https://containerlab.dev/.
8. Nokia SR Linux. Available: https://learn.srlinux.dev/.
9. ncclient: Python library for NETCONF clients. Available: https://github.com/ncclient/ncclient.
10. OpenConfig Community, gNMIc. Available: https://github.com/openconfig/gnmic.
