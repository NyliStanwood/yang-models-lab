# Memoria – Laboratorio de programación de redes basada en modelos YANG

> **RDSV/SDNV** · Curso 2026-27
>
> **Integrantes:** _[PENDIENTE: nombres]_
>
> **Grupo / Puesto:** _[PENDIENTE]_
>
> **Fecha de entrega:** _[PENDIENTE]_

<!-- Convención: todo lo marcado como [PENDIENTE] queda por completar. Las capturas de pantalla se guardan en docs/images/memoria/ (o la carpeta que elijamos). -->

## Índice
- [Memoria – Laboratorio de programación de redes basada en modelos YANG](#memoria--laboratorio-de-programación-de-redes-basada-en-modelos-yang)
  - [Índice](#índice)
  - [Introducción](#introducción)
  - [1. YANG, descubrimiento de capacidades y consultas de datos de configuración y estado](#1-yang-descubrimiento-de-capacidades-y-consultas-de-datos-de-configuración-y-estado)
    - [1.1. Capacidades de gestión con NETCONF y fuentes de la verdad para YANG](#11-capacidades-de-gestión-con-netconf-y-fuentes-de-la-verdad-para-yang)
      - [1.1.1. NETCONF y el intercambio de capacidades](#111-netconf-y-el-intercambio-de-capacidades)
      - [1.1.2. Fuentes de la verdad para YANG y uso de NETCONF como YANG *explorer*](#112-fuentes-de-la-verdad-para-yang-y-uso-de-netconf-como-yang-explorer)
      - [1.1.3. NETCONF para consultar la configuración y el estado operativo](#113-netconf-para-consultar-la-configuración-y-el-estado-operativo)
    - [1.2. Capacidades de gestión con gNMI y captura de tráfico de gestión](#12-capacidades-de-gestión-con-gnmi-y-captura-de-tráfico-de-gestión)
      - [1.2.1. gNMI para intercambio de capacidades y consultas](#121-gnmi-para-intercambio-de-capacidades-y-consultas)
      - [1.2.2. Análisis del tráfico de gestión en gNMI](#122-análisis-del-tráfico-de-gestión-en-gnmi)
  - [2. Topología de red y configuración basada en modelos con gNMI](#2-topología-de-red-y-configuración-basada-en-modelos-con-gnmi)
  - [3. Model-Driven Telemetry con gNMI](#3-model-driven-telemetry-con-gnmi)
  - [4. Conclusiones](#4-conclusiones)
  - [5. Archivos entregados](#5-archivos-entregados)

---

## Introducción

En esta práctica trabajamos con la gestión de red basada en modelos YANG, usando los protocolos NETCONF y gNMI sobre routers Nokia SR Linux. Desplegamos los escenarios de red con Containerlab dentro de la máquina virtual. A lo largo de tres actividades, consultamos las capacidades de los equipos, exploramos sus modelos YANG, configuramos la red de forma remota y, por último, montamos un sistema de telemetría basado en suscripciones gNMI con Kafka y Prometheus como consumidores de datos.

---

## 1. YANG, descubrimiento de capacidades y consultas de datos de configuración y estado

Para esta primera actividad desplegamos, con el script `deploy-srlinux-testbed.sh`, un escenario compuesto por dos routers Nokia SR Linux (`r1` y `r2`) unidos por un enlace punto a punto y dos hosts Linux (`pc1` y `pc2`), cada uno conectado a la LAN de su router. La gestión de los routers la hicimos siempre a través de sus interfaces de gestión (`mgmt0`).

_[PENDIENTE: captura opcional del escenario desplegado / prueba de conectividad entre pc1 y pc2]_

╭──────────────────────────┬────────────────────────────────┬─────────┬───────────────────╮
│           Name           │           Kind/Image           │  State  │   IPv4/6 Address  │
├──────────────────────────┼────────────────────────────────┼─────────┼───────────────────┤
│ clab-srlinux-testbed-pc1 │ linux                          │ running │ 172.20.20.4       │
│                          │ wbitt/network-multitool:latest │         │ 3fff:172:20:20::4 │
├──────────────────────────┼────────────────────────────────┼─────────┼───────────────────┤
│ clab-srlinux-testbed-pc2 │ linux                          │ running │ 172.20.20.3       │
│                          │ wbitt/network-multitool:latest │         │ 3fff:172:20:20::3 │
├──────────────────────────┼────────────────────────────────┼─────────┼───────────────────┤
│ clab-srlinux-testbed-r1  │ nokia_srlinux                  │ running │ 172.20.20.2       │
│                          │ ghcr.io/nokia/srlinux:latest   │         │ 3fff:172:20:20::2 │
├──────────────────────────┼────────────────────────────────┼─────────┼───────────────────┤
│ clab-srlinux-testbed-r2  │ nokia_srlinux                  │ running │ 172.20.20.5       │
│                          │ ghcr.io/nokia/srlinux:latest   │         │ 3fff:172:20:20::5 │
╰──────────────────────────┴────────────────────────────────┴─────────┴───────────────────╯
Done!

docker ps -a
CONTAINER ID   IMAGE                            COMMAND                  CREATED       STATUS       PORTS                                  NAMES
56a233b65084   ghcr.io/nokia/srlinux:latest     "/tini -- /usr/local…"   3 hours ago   Up 3 hours                                          clab-srlinux-testbed-r2
836ec084dfbf   wbitt/network-multitool:latest   "/bin/sh /docker/ent…"   3 hours ago   Up 3 hours   80/tcp, 443/tcp, 1180/tcp, 11443/tcp   clab-srlinux-testbed-pc2
c5bbe719aebf   ghcr.io/nokia/srlinux:latest     "/tini -- /usr/local…"   3 hours ago   Up 3 hours                                          clab-srlinux-testbed-r1
de89d80ab3bb   wbitt/network-multitool:latest   "/bin/sh /docker/ent…"   3 hours ago   Up 3 hours   80/tcp, 443/tcp, 1180/tcp, 11443/tcp   clab-srlinux-testbed-pc1

ssh -p 830 admin@clab-srlinux-testbed-r1 -s netconf

ssh -p 830 admin@clab-srlinux-testbed-r2 -s netconf

La contraseña es NokiaSrl1!

### 1.1. Capacidades de gestión con NETCONF y fuentes de la verdad para YANG

#### 1.1.1. NETCONF y el intercambio de capacidades

Ejecutamos el script `get-capabilities-srlinux.py`, que con la librería `ncclient` abre una sesión NETCONF contra el router y muestra los módulos YANG que anuncia, las capacidades adicionales del servidor NETCONF y las capacidades del cliente.

python get-capabilities-srlinux.py <container_name>
python get-capabilities-srlinux.py clab-srlinux-testbed-r1

created activities/module-1/r1-capabilities.txt


**Pregunta 1.** Información que se obtiene de las capacidades; soporte de XPath, YANG Push y *writable-running*; soporte de esas capacidades en `ncclient`; proporción de modelos estándar frente a propietarios.

> El script lee las capacidades que el servidor anuncia en su `<hello>` NETCONF (`session.server_capabilities`) y las separa en tres bloques: los **módulos YANG** que implementa el equipo (nombre, revisión, namespace y, en algunos casos, `features` y `deviations`), las **capacidades NETCONF adicionales** del servidor y las **capacidades del cliente** `ncclient`.
>
> - **XPath:** el servidor no anuncia `:xpath:1.0`, así que solo admite filtros *subtree*.
> - **YANG Push:** no lo soporta. No anuncia `:notification:1.0` ni los módulos `ietf-subscribed-notifications`/`ietf-yang-push`. En SR Linux las suscripciones se hacen con gNMI.
> - **writable-running:** no lo anuncia, así que no se puede hacer `<edit-config>` directamente sobre *running*. Sí se puede configurar por NETCONF: el servidor anuncia `:candidate:1.0` y `:confirmed-commit:1.1`, de modo que se edita *candidate* y luego se hace `<commit>`.
>
> `ncclient` sí anuncia `writable-running`, `xpath`, `notification` e `interleave`, pero una capacidad solo se puede usar si la anuncian los dos extremos, así que con este equipo no sirven.
>
> De los 392 módulos anunciados, la mayoría son **propietarios de Nokia**: 268 (unos 68 %), con prefijo `srl_nokia-` o namespace `urn:nokia.com`. Hay 111 de OpenConfig (unos 28 %) y solo 13 del IETF/IANA (unos 3 %), casi todos relacionados con NETCONF/YANG. Además, el equipo declara desviaciones (`openconfig-srl-deviations`, `ietf-srl-deviations`) sobre muchos de los modelos estándar.
>Los modelos de organismos de estandarización (IETF/IANA) son pocos, y se limitan casi siempre a lo relativo al propio NETCONF/YANG: ietf-netconf, ietf-yang-library, ietf-netconf-monitoring, ietf-yang-types, ietf-interfaces y otros. OpenConfig no es un organismo de estandarización formal, sino un grupo de operadores (Google y otros) que publica modelos vendor-neutral. 
[PENDIENTE: captura / extracto de la salida del script]_



#### 1.1.2. Fuentes de la verdad para YANG y uso de NETCONF como YANG *explorer*

Con el script `download-yang-modules-schemas-srlinux.py` descargamos los esquemas de todos los módulos YANG que implementa el router y armamos un catálogo local en la carpeta `yang-models-srlinux`. Después usamos `pyang` (formatos `tree` y `xpath`) para revisar el módulo `ietf-yang-library@2019-01-04.yang` y lanzamos una consulta GET con filtro *subtree* mediante `get-rpc-yang-library-srlinux.py`.


python download-yang-modules-schemas-srlinux.py clab-srlinux-testbed-r1
saved output in activities/module-1/pyang-tree-ietflib.txt 


pyang -f xpath ietf-yang-library@2019-01-04.yang
saved output in activities/module-1/pyang-xpath-ietflib.txt

python get-rpc-yang-library-srlinux.py <container_name> > get-rpc-yang-library-srlinux-output.xml 
python get-rpc-yang-library-srlinux.py clab-srlinux-testbed-r1 > get-rpc-yang-library-srlinux-output.xml
saved output in activities/module-1/get-rpc-yang-library-srlinux-output.xml

**Pregunta 2.** Propósito del módulo `ietf-yang-library` y su relación con las capacidades; *datastores* que implementa SR Linux; soporte de NMDA (RFC 8342) y módulo asociado; número de módulos de Nokia, del IETF y de OpenConfig.

> **Propósito.** `ietf-yang-library` (RFC 8525) describe el propio servidor. Todos sus nodos son de solo lectura (`+--ro`) e indican qué módulos YANG implementa el equipo (nombre, revisión, *namespace*, ubicación, *features* y *deviations*), cuáles se importan solo por sus tipos (`import-only-module`) y en qué *datastores* se aplica cada conjunto de módulos (`module-set` → `schema` → `datastore`). El nodo `content-id` cambia cuando cambia ese conjunto.
>
> **Relación con las capacidades.** Sí la tiene. El servidor anuncia en su `<hello>` la capacidad `urn:ietf:params:netconf:capability:yang-library:1.1`, que indica que la lista completa de modelos se puede consultar con un `<get>` sobre `/yang-library`. Las capacidades dan una lista plana de módulos, y la YANG library da la misma información estructurada y asociada a cada *datastore*.
>
> **Datastores.** La consulta GET devuelve cinco, todos asociados al esquema `nokia`: `ds:running`, `ds:candidate`, `ds:startup`, `ds:intended` y `ds:operational`.
> <datastore>
                <name xmlns:ds="urn:ietf:params:xml:ns:yang:ietf-datastores">ds:candidate</name>
                <schema>nokia</schema>
            </datastore>
            <datastore>
                <name xmlns:ds="urn:ietf:params:xml:ns:yang:ietf-datastores">ds:intended</name>
                <schema>nokia</schema>
            </datastore>
            <datastore>
                <name xmlns:ds="urn:ietf:params:xml:ns:yang:ietf-datastores">ds:operational</name>
                <schema>nokia</schema>
            </datastore>
            <datastore>
                <name xmlns:ds="urn:ietf:params:xml:ns:yang:ietf-datastores">ds:running</name>
                <schema>nokia</schema>
            </datastore>
            <datastore>
                <name xmlns:ds="urn:ietf:params:xml:ns:yang:ietf-datastores">ds:startup</name>
                <schema>nokia</schema>
            </datastore>
>
> **NMDA.** Sí lo implementa. Expone `intended` y `operational`, separados de los *datastores* de configuración, y usa la versión NMDA de la YANG library (`datastore`/`schema`, con la rama `modules-state` marcada como obsoleta). Entre los módulos soportados está `ietf-netconf-nmda@2019-01-07` (RFC 8526), que añade las operaciones `get-data` y `edit-data`. Estas operaciones reciben un parámetro `datastore` (`ds:datastore-ref`) con el que se elige el *datastore* NMDA sobre el que actuar, y admiten `with-origin` para saber de dónde procede cada valor operativo. El equipo importa también `ietf-datastores` (identidades `ds:*`) e `ietf-origin`.
>
> ```
> +--ro datastore* [name]
> |  +--ro name      ds:datastore-ref
> |  +--ro schema    -> ../../schema/name
> ```
> ```xml
> <datastore>
>     <name xmlns:ds="urn:ietf:params:xml:ns:yang:ietf-datastores">ds:operational</name>
>     <schema>nokia</schema>
> </datastore>
> ```
>
> **Origen de los módulos.** Los 392 módulos descargados se clasifican por su *namespace*. Por eso `ietf-srl-deviations`, `openconfig-srl-deviations` y `openconfig-srl-augments` cuentan como Nokia, ya que su *namespace* es `urn:nokia.com:...`.
>
> | Origen de los módulos | Cantidad |
> |---|---|
> | Nokia SR Linux (propietarios) | 268 |
> | IETF | 11 |
> | OpenConfig | 111 |
> | Otros (`iana-if-type` de IANA y `yang`, de extensiones de YANG) | 2 |

#### 1.1.3. NETCONF para consultar la configuración y el estado operativo

Analizamos el modelo propietario `srl_nokia-interfaces@2026-07-31.yang` con `pyang -f tree` y, a partir del script de ejemplo, creamos dos scripts nuevos para consultar la interfaz `ethernet-1/1`: uno con GET (estado operativo) y otro con GET-CONFIG (configuración).

copied activities/module-1/P3_a_get-rpc-nokia-ietf-netconf-srlinux.py 
to 
with new netconf filter. 
schema_tree_filter = """
<yang-library xmlns="urn:ietf:params:xml:ns:yang:ietf-yang-library">
    <module-set>
        <name>nokia</name>
        <module>
            <name>ietf-netconf</name>
        </module>
    </module-set>
</yang-library>
"""
run
python P3_a_get-rpc-nokia-ietf-netconf-srlinux.py clab-srlinux-testbed-r1 > get-rpc-yang-ietf-netconf-srlinux-output.xml
vea cómo ahora se proporciona información relativa sólo al módulo `ietf-netconf`.

---
then run 
$ pyang -f tree srl_nokia-interfaces@2026-07-31.yang 
output saved to pyang-tree-nokia-interfaces.txt
to analize how to consult info to the router

also construct the call to get the xml file
- Take element names and nesting from the pyang tree, which shows <interface> as the top level grouping(at the root) directly.
- Take the xmlns from the namespace line of the .yang file.
$ python P3_b_get-rpc-nokia-interfaces-srlinux.py clab-srlinux-testbed-r1 > a_P3_b_nokia-interfaces-srlinux-output.xml

CREATE


 (1) get-rpc-interface-srlinux.py para realizar una consulta RPC de tipo GET que obtenga los datos operativos de la interfaz de red ethernet-1/1 (intefaz de conexión con el host) de uno de los router Nokia SR Linux
$ python P3_get-rpc-interface-srlinux.py clab-srlinux-testbed-r1 > P3_1_nokia-interface-r1-e1.xml

 (2) get-config-rpc-interface-srlinux.py para realizar una consulta RPC de tipo GET-CONFIG que obtenga los datos de configuración de la interfaz de red ethernet-1/1 de uno de los router Nokia SR Linux
$ python P3_get-config-rpc-interface-srlinux.py clab-srlinux-testbed-r1 > P3_2_nokia-getConfig-interface-r1-e1.xml


**Pregunta 3.** Scripts `get-rpc-interface-srlinux.py` y `get-config-rpc-interface-srlinux.py`; *datastore* al que accede cada consulta.

> _[PENDIENTE: descripción de los filtros utilizados en cada script]_
>
> _[PENDIENTE: extracto de la salida de cada script]_
>
> _[: respuesta sobre los datastores]_
> (1) <get>: datastore running más los datos de estado

<get> no lleva parámetro source, así que no se elige datastore. Según RFC 6241 (§7.7), devuelve la configuración del datastore running junto con los datos de estado (nodos ro del árbol pyang: oper-state, statistics, ifindex…). En el modelo NMDA (RFC 8342), que el router anuncia con ietf-datastores e ietf-netconf-nmda, esto equivale aproximadamente a la vista del datastore operational.

(2) <get-config>: el datastore indicado en source, aquí running

<get-config> exige indicar el datastore de origen. En el script es source="running", la configuración activa del router. Solo devuelve datos de configuración (nodos rw: admin-state, mtu, description, subinterface…), nunca datos de estado.

### 1.2. Capacidades de gestión con gNMI y captura de tráfico de gestión

#### 1.2.1. gNMI para intercambio de capacidades y consultas

Repetimos el descubrimiento de capacidades, ahora con el cliente `gNMIc`, y realizamos consultas `get` sobre `/yang-library/datastore` y con filtros de tipo *path*. Después definimos nuestras propias consultas para obtener la configuración y el estado operativo de `ethernet-1/1`.

**Pregunta 4.** Información de las capacidades en gNMI; comparación con NETCONF (capacidades operativas, diferencias en los modelos anunciados, negociación de versión y codificación).

> _[PENDIENTE: análisis y respuesta]_
>
> _[PENDIENTE: extracto de la salida de `gnmic capabilities`]_

**Pregunta 5.** Consultas `get` de configuración y de estado de `ethernet-1/1`; coherencia con el modelo YANG y con las respuestas de NETCONF.

> _[PENDIENTE: comandos `gnmic` utilizados]_
>
> ```bash
> # [PENDIENTE] consulta de configuración
> # [PENDIENTE] consulta de estado
> ```
>
> _[PENDIENTE: capturas de la ejecución exitosa y respuesta]_

#### 1.2.2. Análisis del tráfico de gestión en gNMI

Capturamos el tráfico en la interfaz `mgmt0` de `r1` con `clab-capture-traffic.sh` mientras ejecutábamos las consultas gNMI con la opción `--log-tls-secret`. Guardamos la captura como `gnmi-traffic.pcap` y los secretos TLS de cada operación por separado. En Wireshark configuramos esos secretos para descifrar TLS y cargamos los archivos `.proto` de `gnmi4wireshark` para decodificar los mensajes Protobuf.

**Pregunta 6.** Operación de capacidades: cabeceras HTTP/2 con los parámetros de conexión; mensaje gRPC/Protobuf de respuesta (versión de gNMI, modelos y codificaciones).

> _[PENDIENTE: captura del paquete HTTP/2 + descripción]_
>
> _[PENDIENTE: captura de la cabecera Protocol Buffers de la respuesta + descripción]_

**Pregunta 7.** Operación GET: campos del mensaje de petición y de la respuesta en Protobuf.

> _[PENDIENTE: captura de la petición + descripción]_
>
> _[PENDIENTE: captura de la respuesta + descripción]_

Al terminar, destruimos el escenario con `destroy-srlinux-testbed.sh`.

---

## 2. Topología de red y configuración basada en modelos con gNMI

En la segunda actividad desplegamos con `deploy-routing-testbed.sh` un escenario más grande: tres routers SR Linux (`r1`, `r2`, `r3`) conectados en triángulo, tres switches OVS (`s1`, `s2`, `s3`) y seis hosts (dos por LAN). Los hosts ya tenían direccionamiento y rutas, pero los enlaces entre routers y el encaminamiento quedaban sin configurar. Para entender la topología usamos `containerlab graph` y/o la extensión de VS Code, y ejecutamos la aplicación Java `topology-driver-1.0.jar`, que normaliza los datos de la topología según el modelo YANG del IETF de la RFC 8345.

**Pregunta 8.** Descripción del escenario; función de la aplicación Java; utilidad para un controlador SDN.

> _[PENDIENTE: descripción del escenario y diagrama / captura]_
>
> | Enlace / LAN | Interfaces | Prefijo IP |
> |---|---|---|
> | _[PENDIENTE]_ | | |
>
> _[PENDIENTE: análisis de `topology.json` / `topology.xml` y respuesta]_

A partir de los modelos `srl_nokia-interfaces`, `srl_nokia-if-ip`, `srl_nokia-network-instance`, `srl_nokia-static-routes` y `srl_nokia-next-hop-groups`, identificamos las variables de las plantillas `configure_ip_address.yaml` y `configure_ip_routing.yaml`, y escribimos un script que automatiza todas las peticiones `set` de `gNMIc` para configurar el direccionamiento y las rutas estáticas de los tres routers. Verificamos la configuración con consultas `get` (incluido `gnmic-get-routing-config.sh`) y con pruebas de conectividad entre hosts.

**Pregunta 9.** Script de automatización de la configuración y pruebas de conectividad.

> _[PENDIENTE: nombre del script y explicación breve de su lógica]_
>
> _[PENDIENTE: plan de direccionamiento y rutas estáticas por router]_
>
> _[PENDIENTE: captura de pruebas de conectividad (ping) entre hosts]_

**Pregunta 10 (opcional).** Captura y análisis del tráfico de una operación `set` de gNMI.

> _[PENDIENTE / OMITIDA: capturas de la petición y la respuesta en Protobuf + descripción]_

---

## 3. Model-Driven Telemetry con gNMI

En la última actividad, sobre el mismo escenario de la actividad 2, completamos la plantilla `gnmic-subscription.yaml` con dos suscripciones a la interfaz `ethernet-1/1` de `r1`: una periódica (`sample`, cada 5 s) para las estadísticas de tráfico y otra basada en cambios (`on-change`) para los estados operativo y administrativo. Lanzamos `gnmic subscribe` y provocamos cambios de estado con un `set` sobre el estado administrativo de la interfaz, comprobando también la pérdida y recuperación de conectividad.

**Pregunta 11.** Notificaciones periódicas y basadas en cambios; comando `set` utilizado.

> _[PENDIENTE: paths elegidos para cada suscripción]_
>
> ```bash
> # [PENDIENTE] comando gnmic set para cambiar el estado administrativo
> ```
>
> _[PENDIENTE: capturas de notificaciones periódicas y on-change + descripción]_

**Pregunta 12 (opcional).** Captura y análisis del tráfico de la suscripción y de sus notificaciones.

> _[PENDIENTE / OMITIDA: capturas + respuesta sobre el número de cabeceras GRPC Message y Protocol Buffers]_

Después creamos `gnmic-subscription-kafka-prometheus.yaml` para cubrir todas las interfaces de `r1`. Las estadísticas se envían a Prometheus (cada 10 s) y al *topic* `traffic-stats` de Kafka (cada 5 s), y los cambios de estado al *topic* `interface-status`. Levantamos el sistema de telemetría con `docker compose` (gNMIc, Kafka, Zookeeper, Consul y Prometheus), consultamos las métricas desde la interfaz web de Prometheus y consumimos los *topics* de Kafka con `kafka-console-consumer.sh`.

**Pregunta 13.** Notificaciones en Prometheus y en Kafka; gráfica de bytes de entrada y salida.

> _[PENDIENTE: descripción de la configuración de suscripciones y salidas]_
>
> _[PENDIENTE: captura de Kafka – topic `traffic-stats`]_
>
> _[PENDIENTE: captura de Kafka – topic `interface-status`]_
>
> _[PENDIENTE: captura de métricas en Prometheus]_
>
> _[PENDIENTE: gráfica de bytes de entrada/salida de todas las interfaces de r1]_

---

## 4. Conclusiones

> _[PENDIENTE: valoración personal de la práctica, problemas que encontramos y sugerencias]_

---

## 5. Archivos entregados

| Archivo | Pregunta |
|---|---|
| `get-rpc-interface-srlinux.py` | 3 |
| `get-config-rpc-interface-srlinux.py` | 3 |
| `gnmi-traffic.pcap` | 6, 7 |
| `<container_name>-capabilities.tlssecret.log` | 6 |
| `<container_name>-get-rpc.tlssecret.log` | 7 |
| _[PENDIENTE: script de configuración]_ | 9 |
| `<container_name>-edit-config-rpc.pcap` + `.tlssecret.log` (opcional) | 10 |
| `gnmic-subscription.yaml` (modificado) | 11 |
| `<container_name>-subscribe-rpc.pcap` + `.tlssecret.log` (opcional) | 12 |
| `gnmic-subscription-kafka-prometheus.yaml` | 13 |
