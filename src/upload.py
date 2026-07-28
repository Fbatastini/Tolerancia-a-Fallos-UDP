import socket
import argparse
import lib.common.protocol as Protocol
import logging
import lib.client.client as Client
import lib.common.logs as Logs
import lib.common.parser as Parser

def main():
    args = Parser.parse_args("upload")
    Logs.configure_logging(args)
    logging.debug("Starting upload with configuration: Host=%s, Port=%d, Source=%s, Name=%s, Protocol=%s", args.host, args.port, args.src, args.name, args.protocol)
    Client.init_connection(args.protocol, (args.host, args.port), 'UPLOAD', args.name, local_filepath=args.src)

if __name__ == "__main__":
    main()