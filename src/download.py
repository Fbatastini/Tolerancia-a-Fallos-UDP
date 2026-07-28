import socket
import argparse
import lib.common.protocol as Protocol
import lib.client.client as Client
import lib.common.logs as Logs
import lib.common.parser as Parser

def main():
    args = Parser.parse_args("download")
    Logs.configure_logging(args)
    Client.init_connection(args.protocol, (args.host, args.port), 'DOWNLOAD', args.name, local_filepath=args.dst)

if __name__ == "__main__":
    main()