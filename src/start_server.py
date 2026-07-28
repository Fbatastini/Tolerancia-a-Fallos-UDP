import logging
import socket
import argparse
import lib.common.logs as Logs
import os
from lib.server.server import Server
import lib.common.parser as Parser

def main():
    try:
        args = Parser.parse_args("server")
        Logs.configure_logging(args)
        logging.debug("Starting server with configuration: Host=%s, Port=%d, Storage=%s", args.host, args.port, args.storage)
        storage_dir = args.storage
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

        server = Server(args.host, args.port, storage_dir)
        server.start()
    except Exception as e:
        print(f"Error iniciando servidor: {e}")
    except KeyboardInterrupt:
        print("Servidor detenido por el usuario")
        server.stop()
        return

if __name__ == "__main__":
    main()