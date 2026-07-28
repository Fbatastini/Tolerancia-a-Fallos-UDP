import logging
from .client_acceptor import ClientAcceptor

class Server:
    def __init__(self, host, port, storage_dir):
        self.host = host
        self.port = port
        self.storage_dir = storage_dir
        self.acceptor = ClientAcceptor(self.host, self.port, self.storage_dir)

    def start(self):
        logging.info(f"Starting server on {self.host}:{self.port}, storing files in {self.storage_dir}")
        self.acceptor.start()
        while self.acceptor.is_alive():
            self.acceptor.join(0.5)
        logging.info("Server stopped")

    def stop(self):
        if self.acceptor:
            logging.info("Stopping server...")
            self.acceptor.stop()
            self.acceptor.join()
            self.acceptor = None

    def is_alive(self):
        return self.acceptor and self.acceptor.is_alive()

    def wait(self, timeout=None):
        if self.acceptor:
            self.acceptor.join(timeout=timeout)
