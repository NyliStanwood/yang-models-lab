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

```bash
gnmic -a clab-srlinux-testbed-r1:57400 -u admin -p NokiaSrl1! --skip-verify capabilities > p4-output.txt
```

Extracto de la salida (`p4-output.txt`):

```text
gNMI version: 0.10.0
supported models:
  - urn:nokia.com:srlinux:aaa:aaa:srl_nokia-aaa, Nokia, 2026-07-31
  - http://openconfig.net/yang/aaa:openconfig-aaa, OpenConfig working group, 2022-07-29
  ...
supported encodings:
  - JSON_IETF
  - PROTO
  - ASCII
  - 52
  - 42
  ...
```

**Información proporcionada.** La respuesta contiene la versión de gNMI (0.10.0), la lista de modelos soportados (nombre, organización y versión/revisión) y las codificaciones soportadas: `JSON_IETF`, `PROTO` y `ASCII`, además de los valores 42–53, que son codificaciones propietarias de Nokia y quedan fuera del enumerado estándar de gNMI.

**¿Capacidades operativas más allá de los modelos YANG?** No, salvo la versión y las codificaciones. En NETCONF el `<hello>` anuncia capacidades del protocolo y del equipo: `base:1.0/1.1`, `candidate`, `confirmed-commit`, `rollback-on-error`, `validate`, `startup`, `url`, `with-defaults`… Los módulos se anuncian además con sus *features* y *deviations*. gNMI no informa de nada de esto, porque la semántica de sus operaciones (`Get`, `Set`, `Subscribe`) está fijada por la especificación: no hay datastores que elegir y el `Set` es siempre transaccional.

**¿Diferencias en los modelos?** Sí. gNMI anuncia 384 modelos y NETCONF 392, aunque los modelos de configuración y estado implementados (`srl_nokia-*`, `openconfig-*`) coinciden en nombre y revisión.

- **Solo en NETCONF (80):** los módulos propios de NETCONF/NMDA (`ietf-netconf`, `ietf-netconf-nmda`, `ietf-netconf-with-defaults`, `ietf-datastores`, `ietf-origin`, `ietf-srl-deviations`…) y los módulos *import-only* de la yang-library (`*-types`, `ietf-interfaces`, `openconfig-bgp`, `srl_nokia-gnmi`…). gNMI solo lista los modelos implementados.
- **Solo en gNMI (76):** los módulos `srl_nokia-tools-*`, que modelan el árbol `/tools` de acciones operativas (borrar estadísticas, reiniciar protocolos…). SR Linux los expone por gNMI pero no por NETCONF.

**¿Negociación implícita en NETCONF?** De versión, sí: en el intercambio de `<hello>` ambos extremos anuncian `base:1.0` y `base:1.1`, y se usa la mayor común (1.1, con *chunked framing*). De codificación, no, porque NETCONF usa siempre XML. En gNMI no hay *handshake*: el cliente elige la codificación en cada petición (campo `encoding`) y el servidor responde con error si no la soporta.

**Pregunta 5.** Consultas `get` de configuración y de estado de `ethernet-1/1`; coherencia con el modelo YANG y con las respuestas de NETCONF.

Según el árbol de `pyang` (`pyang-tree-nokia-interfaces.txt`), `interface` es una lista en la raíz con clave `name`. Por eso el *path* es `/interface[name=ethernet-1/1]`, equivalente al nodo de contenido `<name>ethernet-1/1</name>` del filtro *subtree* de NETCONF. El tipo de datos se elige con la opción `--type` de `gnmic get` (`ALL` por defecto, `CONFIG`, `STATE` u `OPERATIONAL`).

```bash
# Consulta de configuración
gnmic -a clab-srlinux-testbed-r1:57400 -u admin -p NokiaSrl1! --skip-verify get \
  --path "/interface[name=ethernet-1/1]" --type CONFIG --encoding JSON_IETF

# Consulta de estado operativo
gnmic -a clab-srlinux-testbed-r1:57400 -u admin -p NokiaSrl1! --skip-verify get \
  --path "/interface[name=ethernet-1/1]" --type STATE --encoding JSON_IETF
```

Respuesta de la consulta de configuración:

```json
"Path": "srl_nokia-interfaces:interface[name=ethernet-1/1]",
"values": {
  "srl_nokia-interfaces:interface": {
    "admin-state": "enable",
    "subinterface": [
      { "index": 0,
        "ipv4": { "address": [ { "ip-prefix": "10.0.1.1/24" } ], "admin-state": "enable" } }
    ]
  }
}
```

Extracto de la respuesta de la consulta de estado:

```json
"srl_nokia-interfaces:interface": {
  "ifindex": 32768,
  "oper-state": "up",
  "last-change": "2026-10-13T14:41:05.957Z",
  "ethernet": { "hw-mac-address": "1A:55:02:FF:00:01", ... },
  "statistics": { "in-octets": "666", ... },
  ...
}
```

**¿Coincide con lo esperado?** Sí.

- **Con el modelo YANG:** `CONFIG` devuelve solo nodos `rw` del árbol (`admin-state`, `subinterface/ipv4/address`), y `STATE` devuelve los nodos `ro` (`oper-state`, `ifindex`, `last-change`, `hw-mac-address`, `statistics`…). Las claves de las listas (`name`, `index`, `ip-prefix`) aparecen en ambas para identificar las entradas.
- **Con NETCONF:** la respuesta `CONFIG` es idéntica a la de `<get-config>` (`P3_2_nokia-getConfig-interface-r1-e1.xml`): `admin-state` `enable` y la dirección `10.0.1.1/24` en la subinterfaz 0. La respuesta `STATE` contiene los mismos datos de estado que `<get>` (`P3_1_nokia-interface-r1-e1.xml`). La diferencia es que `<get>` mezcla configuración y estado, por lo que su equivalente exacto en gNMI es `--type ALL` (la opción por defecto). Los valores que cambian con el tiempo (contadores, `last-change`, MAC) no coinciden porque la consulta NETCONF se hizo antes de redesplegar el escenario.
- **Formato:** el contenido es el mismo, pero NETCONF lo codifica en XML con el *namespace* del módulo, y gNMI en JSON_IETF con el nombre del módulo como prefijo (`srl_nokia-interfaces:interface`).

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

**Descripción del escenario.** La plantilla `routing-testbed.yaml` define tres routers SR Linux conectados en triángulo por sus interfaces `ethernet-1/2` y `ethernet-1/3`. Cada router conecta por `ethernet-1/1` con un switch OVS (`s1`, `s2`, `s3`), al que se conectan dos hosts `network-multitool`. Los switches son *bridges* que el script de despliegue crea en la máquina anfitriona con `ovs-vsctl add-br`, no contenedores. Todos los contenedores están además en la red de gestión `clab`, por la que se accede a los routers con gNMI (puerto 57400).

| Enlace / LAN | Interfaces | Prefijo IP |
|---|---|---|
| LAN 1 | `r1:ethernet-1/1` — `s1` — `pc11`, `pc12` | 192.168.1.0/24 (r1 `.1`, hosts `.100` y `.101`) |
| LAN 2 | `r2:ethernet-1/1` — `s2` — `pc21`, `pc22` | 192.168.2.0/24 (r2 `.1`, hosts `.100` y `.101`) |
| LAN 3 | `r3:ethernet-1/1` — `s3` — `pc31`, `pc32` | 192.168.3.0/24 (r3 `.1`, hosts `.100` y `.101`) |
| r1 ↔ r2 | `r1:ethernet-1/2` — `r2:ethernet-1/2` | 10.0.10.0/30 (sin configurar) |
| r1 ↔ r3 | `r1:ethernet-1/3` — `r3:ethernet-1/2` | 10.0.11.0/30 (sin configurar) |
| r2 ↔ r3 | `r2:ethernet-1/3` — `r3:ethernet-1/3` | 10.0.12.0/30 (sin configurar) |

Configuración inicial:

- **Routers:** los `r*.cfg` solo configuran la interfaz de la LAN y la asocian a la *network-instance* `default`.
- **Hosts:** el script de despliegue les asigna la dirección y añade rutas hacia las otras dos LANs a través del router de su LAN.

Los enlaces entre routers no tienen direccionamiento ni hay rutas estáticas, por lo que no hay conectividad entre LANs. Los prefijos de 10.0.x.x son los del plan de direccionamiento del enunciado. Las LANs son en realidad /24 y no /30 como indica el enunciado, porque una /30 no podría contener las direcciones `.100` y `.101` de los hosts.

**Función de la aplicación Java.** `topology-driver-1.0.jar` lee el fichero `topology-data.json` que genera Containerlab al desplegar. Ese fichero está en un formato propio de la herramienta, con nodos, imágenes, MACs, direcciones de gestión, etc. La aplicación lo transforma en una instancia de datos conforme a los modelos `ietf-network` e `ietf-network-topology` de la RFC 8345, y la serializa en JSON (`topology.json`) y en XML (`topology.xml`) con las librerías YANG Tools de OpenDaylight. El resultado es una única red, `routing-testbed`, que contiene:

- 12 nodos (`node-id`), cada uno con sus puertos como *termination points* (`tp-id`).
- 12 enlaces (`link-id`), cada uno con origen y destino `source-node`/`source-tp` → `dest-node`/`dest-tp`.

En el proceso solo se conserva la información topológica: se descartan la imagen, el tipo de nodo, las MACs y la red de gestión. Además, los nombres de interfaz se normalizan a los del equipo, por ejemplo `e1-1` pasa a ser `ethernet-1/1`. Como los datos se validan contra el esquema YANG, el mismo contenido se puede serializar en JSON o en XML.

**Utilidad para un controlador SDN.** Un controlador necesita una vista global de la red independiente del entorno o fabricante del que procede. Con un modelo estándar como el de la RFC 8345, la topología se convierte en un dato YANG más, igual que la configuración de los equipos:

- **Almacenamiento y consulta homogéneos:** la topología se puede guardar en el *datastore* del controlador, consultar y exponer hacia aplicaciones superiores (NETCONF/RESTCONF) en la misma forma, venga de Containerlab, de LLDP o de otro inventario.
- **Configuración guiada por la topología:** los `node-id`/`tp-id` coinciden con los nombres de interfaz de los modelos de SR Linux, así que el controlador puede recorrer los enlaces y generar directamente los *paths* gNMI necesarios. En este escenario, por ejemplo, puede obtener qué interfaces de cada router asignar a cada /30 y qué siguiente salto usar en cada ruta estática.
- **Ampliación con otras capas:** la topología se puede ampliar con modelos que extienden `ietf-network`, como `ietf-l3-unicast-topology`, incluido en el propio jar, para añadir prefijos y atributos L3. También se puede contrastar con el estado real que se obtiene por telemetría.

A partir de los modelos `srl_nokia-interfaces`, `srl_nokia-if-ip`, `srl_nokia-network-instance`, `srl_nokia-static-routes` y `srl_nokia-next-hop-groups`, identificamos las variables de las plantillas `configure_ip_address.yaml` y `configure_ip_routing.yaml`, y escribimos un script que automatiza todas las peticiones `set` de `gNMIc` para configurar el direccionamiento y las rutas estáticas de los tres routers. Verificamos la configuración con consultas `get` (incluido `gnmic-get-routing-config.sh`) y con pruebas de conectividad entre hosts.

**Pregunta 9.** Script de automatización de la configuración y pruebas de conectividad.

**Plan de direccionamiento.** Seguimos el plan del enunciado para los enlaces entre routers. Las interfaces de cada enlace salen de `routing-testbed.yaml`:

| Enlace | Subred | Router A | Router B |
|---|---|---|---|
| r1 ↔ r2 | 10.0.10.0/30 | r1 `ethernet-1/2` 10.0.10.1 | r2 `ethernet-1/2` 10.0.10.2 |
| r1 ↔ r3 | 10.0.11.0/30 | r1 `ethernet-1/3` 10.0.11.1 | r3 `ethernet-1/2` 10.0.11.2 |
| r2 ↔ r3 | 10.0.12.0/30 | r2 `ethernet-1/3` 10.0.12.1 | r3 `ethernet-1/3` 10.0.12.2 |

**Rutas estáticas.** Cada router necesita una ruta hacia cada una de las dos LANs remotas. El siguiente salto es el extremo del enlace directo con el router de esa LAN:

| Router | Destino | Siguiente salto | *Next-hop group* |
|---|---|---|---|
| r1 | 192.168.2.0/24 | 10.0.10.2 (r2) | `nh-r1-r2` |
| r1 | 192.168.3.0/24 | 10.0.11.2 (r3) | `nh-r1-r3` |
| r2 | 192.168.1.0/24 | 10.0.10.1 (r1) | `nh-r2-r1` |
| r2 | 192.168.3.0/24 | 10.0.12.2 (r3) | `nh-r2-r3` |
| r3 | 192.168.1.0/24 | 10.0.11.1 (r1) | `nh-r3-r1` |
| r3 | 192.168.2.0/24 | 10.0.12.1 (r2) | `nh-r3-r2` |

Al dar valores a las variables de las plantillas tuvimos en cuenta lo siguiente:

- **`IF_IP_PREFIX` y `Target_IP_Prefix`** son prefijos, por lo que llevan máscara. Las LANs usan /24, que es lo configurado en los routers y hosts, y no /30 como indica el enunciado.
- **`IP_NextHop`** es una dirección sin máscara (`10.0.10.2`, no `10.0.10.2/30`), porque el nodo `ip-address` del modelo `srl_nokia-next-hop-groups` es de tipo dirección IP.
- **`Name_NextHop`** debe ser distinto para cada ruta de un mismo router, porque es la clave del *next-hop group*. Si se repite, el segundo `set` sobrescribe el grupo y las dos rutas acaban apuntando al mismo siguiente salto.
- **Router destino de cada petición:** la petición se envía con `-a` al router que debe tener la ruta (`nh-rX-rY` → `clab-routing-testbed-rX`), no al router de la LAN destino.

**Script.** El script ejecuta en secuencia las peticiones `set` de `gNMIc` con cada plantilla y le pasa los pares variable-valor en JSON por la entrada estándar (`--request-vars -`). Hay una petición por interfaz, con `configure_ip_address.yaml`, y una por ruta, con `configure_ip_routing.yaml`. Debe ejecutarse desde `module-2`, porque las plantillas se referencian con ruta relativa:

```bash
# Direccionamiento IP de los enlaces entre routers
echo '{"IF_NAME": "ethernet-1/2", "IF_IP_PREFIX": "10.0.10.1/30"}' | gnmic -a clab-routing-testbed-r1:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_address.yaml --request-vars -
echo '{"IF_NAME": "ethernet-1/3", "IF_IP_PREFIX": "10.0.11.1/30"}' | gnmic -a clab-routing-testbed-r1:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_address.yaml --request-vars -
echo '{"IF_NAME": "ethernet-1/2", "IF_IP_PREFIX": "10.0.10.2/30"}' | gnmic -a clab-routing-testbed-r2:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_address.yaml --request-vars -
echo '{"IF_NAME": "ethernet-1/3", "IF_IP_PREFIX": "10.0.12.1/30"}' | gnmic -a clab-routing-testbed-r2:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_address.yaml --request-vars -
echo '{"IF_NAME": "ethernet-1/2", "IF_IP_PREFIX": "10.0.11.2/30"}' | gnmic -a clab-routing-testbed-r3:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_address.yaml --request-vars -
echo '{"IF_NAME": "ethernet-1/3", "IF_IP_PREFIX": "10.0.12.2/30"}' | gnmic -a clab-routing-testbed-r3:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_address.yaml --request-vars -

# Rutas estáticas hacia las LANs remotas
echo '{"Name_NextHop": "nh-r1-r2", "IP_NextHop": "10.0.10.2", "Target_IP_Prefix": "192.168.2.0/24"}' | gnmic -a clab-routing-testbed-r1:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_routing.yaml --request-vars -
echo '{"Name_NextHop": "nh-r1-r3", "IP_NextHop": "10.0.11.2", "Target_IP_Prefix": "192.168.3.0/24"}' | gnmic -a clab-routing-testbed-r1:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_routing.yaml --request-vars -
echo '{"Name_NextHop": "nh-r2-r1", "IP_NextHop": "10.0.10.1", "Target_IP_Prefix": "192.168.1.0/24"}' | gnmic -a clab-routing-testbed-r2:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_routing.yaml --request-vars -
echo '{"Name_NextHop": "nh-r2-r3", "IP_NextHop": "10.0.12.2", "Target_IP_Prefix": "192.168.3.0/24"}' | gnmic -a clab-routing-testbed-r2:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_routing.yaml --request-vars -
echo '{"Name_NextHop": "nh-r3-r2", "IP_NextHop": "10.0.12.1", "Target_IP_Prefix": "192.168.2.0/24"}' | gnmic -a clab-routing-testbed-r3:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_routing.yaml --request-vars -
echo '{"Name_NextHop": "nh-r3-r1", "IP_NextHop": "10.0.11.1", "Target_IP_Prefix": "192.168.1.0/24"}' | gnmic -a clab-routing-testbed-r3:57400 -u admin -p NokiaSrl1! --skip-verify set --request-file configure_ip_routing.yaml --request-vars -
```

**Resultado de las peticiones `set`.** Cada petición devuelve una `SetResponse` con dos operaciones `UPDATE`, que se corresponden con los dos `updates` de la plantilla:

- `configure_ip_address.yaml`: `interface[name=ethernet-1/N]` y `network-instance[name=default]/interface[name=ethernet-1/N.0]`.
- `configure_ip_routing.yaml`: `network-instance[name=default]/next-hop-groups/group[name=nh-rX-rY]` y `network-instance[name=default]/static-routes/route[prefix=192.168.Z.0/24]`.

Extracto de la respuesta a la primera ruta de r1:

```json
{
  "source": "clab-routing-testbed-r1:57400",
  "time": "2026-10-15T23:23:10.692752764+02:00",
  "results": [
    { "operation": "UPDATE", "path": "network-instance[name=default]/next-hop-groups/group[name=nh-r1-r2]" },
    { "operation": "UPDATE", "path": "network-instance[name=default]/static-routes/route[prefix=192.168.2.0/24]" }
  ]
}
```

**Verificación con `get`.** Lanzamos `gnmic-get-routing-config.sh` sobre cada router. Los tres tienen en la *network-instance* `default` las interfaces `ethernet-1/1.0`, `ethernet-1/2.0` y `ethernet-1/3.0`, dos *next-hop groups* y dos rutas estáticas con `admin-state` `enable`, tal como aparece en la tabla de rutas anterior. Por ejemplo, en r1:

```json
"srl_nokia-next-hop-groups:next-hop-groups": {
  "group": [
    { "name": "nh-r1-r2", "nexthop": [ { "admin-state": "enable", "index": 1, "ip-address": "10.0.10.2" } ] },
    { "name": "nh-r1-r3", "nexthop": [ { "admin-state": "enable", "index": 1, "ip-address": "10.0.11.2" } ] }
  ]
},
"srl_nokia-static-routes:static-routes": {
  "route": [
    { "admin-state": "enable", "next-hop-group": "nh-r1-r2", "prefix": "192.168.2.0/24" },
    { "admin-state": "enable", "next-hop-group": "nh-r1-r3", "prefix": "192.168.3.0/24" }
  ]
}
```

**Pruebas de conectividad.** Hacemos `ping` entre hosts de LANs distintas, por ejemplo `docker exec clab-routing-testbed-pc11 ping -c 3 192.168.3.100`.

> _[PENDIENTE: captura de las pruebas de conectividad (ping) entre hosts]_

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
