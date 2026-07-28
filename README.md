# Trabajo Práctico n˚1 Redes

## Integrantes:

### Fabricio Batastini
### Facundo Madotta
### Manuel Peñalva
### Mateo Nowenstein
### Joaquín Schapira

# File Transfer sobre UDP

Este proyecto implementa una arquitectura Cliente-Servidor para la transferencia de archivos de forma confiable sobre el protocolo UDP, el cual nativamente no ofrece garantías de entrega. Se desarrollaron a nivel de aplicación dos mecanismos de control de flujo y recuperación de errores: **Stop-and-Wait** y **Go-Back-N**.

## Arquitectura

El servidor soporta la conexión de múltiples clientes de forma concurrente. Utiliza un `Client Acceptor` para recibir conexiones (SYN) en un puerto principal y delega la transferencia de datos a `Client Handlers` independientes (vía Threads) utilizando puertos efímeros para cada clientes, garantizando así el aislamiento del tráfico y previniendo bloqueos.

## Requisitos previos

El sistema requiere Python.

## Modo de Uso

El sistema consta de tres comandos principales: inicio del servidor, subida de archivos (upload) y descarga de archivos (download). Todo sobre la carpeta `/src`

### 1. Iniciar el Servidor (`server`)
Levanta el servidor a la escucha de peticiones entrantes.
```bash
python start_server.py -H <IP> -p <PUERTO> -s <DIRECTORIO_ALMACENAMIENTO> [-v | -q]
```

### 2.1 Iniciar el Cliente (`upload`)
```bash
python upload.py -H <IP_SERVIDOR> -p <PUERTO_SERVIDOR> -s <RUTA_LOCAL> -n <NOMBRE_DESTINO> -r <snw|gbn> [-v | -q]
```

### 2.2 Iniciar el Cliente (`download`)
```bash
python download.py -H <IP_SERVIDOR> -p <PUERTO_SERVIDOR> -d <RUTA_DESTINO> -n <NOMBRE_ORIGEN> -r <snw|gbn> [-v | -q]
```

## Pruebas y Simulación de Red (Mininet)

Para evaluar la robustez de los protocolos frente a escenarios adversos (como la pérdida de paquetes), el sistema está diseñado para ser testeado utilizando **Mininet**.

### 1. Levantar la topología
Para ejecutar la topología sobre el directorio principal
```bash
sudo python3 topology_mininet.py
```

### 2. Una vez en Mininet:
```bash
mininet> xterm h1 h2
```

### 3. Acceder a la carpeta del proyecto /src y ejecutar en cada terminal:

En h1:

```bash
python start_server.py -H 10.0.0.1 -p 8080 -s <DIRECTORIO_ALMACENAMIENTO> [-v | -q]
```

En h2:

```bash
python upload.py -H 10.0.0.1 -p 8080 -s <RUTA_LOCAL> -n <NOMBRE_DESTINO> -r <snw|gbn> [-v | -q]
```

o 

```bash
python download.py -H 10.0.0.1 -p 8080 -d <RUTA_DESTINO> -n <NOMBRE_ORIGEN> -r <snw|gbn> [-v | -q]
```


## Requisitos previos

El sistema requiere Mininet para las simulaciones de pérdida.