import argparse

def common_parse_arg(desc):
    parser = argparse.ArgumentParser(description=desc)
    mutex_group = parser.add_mutually_exclusive_group()
    mutex_group.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')
    mutex_group.add_argument('-q', '--quiet', action='store_true', help='Decrease output verbosity')
    parser.add_argument('-H', '--host', required=True, help='Service IP address')
    parser.add_argument('-p', '--port', type=int, required=True, help='Service port')
    return parser

def get_parser(role):
    parser = common_parse_arg(f"File transfer {role} arguments")
    if role == 'server':
        parser.add_argument('-s', '--storage', required=True, help='Storage directory path')     
    else:
        parser = client_args(parser, role)
    return parser

def client_args(parser, role):
    if role == 'upload':
        parser.add_argument('-s', '--src', required=True, help='Source file path')
    elif role == 'download':
        parser.add_argument('-d', '--dst', required=True, help='Destination file path')
    parser.add_argument('-n', '--name', required=True, help='File name on the server')
    parser.add_argument('-r', '--protocol', choices=['gbn', 'snw'], required=True, help='Error recovery protocol (gbn or snw)')
    return parser

def parse_args(role):
    parser = get_parser(role)
    return parser.parse_args()