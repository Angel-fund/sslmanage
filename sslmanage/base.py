# coding: utf-8
import logging

logging.basicConfig(filename="/tmp/upssl.log",
                    level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt='%m/%d/%Y %I:%M:%S %p')

log_info = logging.info


class BaseSsl:
    def __init__(self, cert_file, key_file):
        self.cert_file = cert_file
        self.key_file = key_file

    def _get_ssl(self):
        with open(self.cert_file, 'r+') as f_ca:
            self.cert = f_ca.read()

        with open(self.key_file, 'r+') as f_pri:
            self.cert_key = f_pri.read()

