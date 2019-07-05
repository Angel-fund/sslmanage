# coding: utf-8
import time

import qiniu
import requests
from sslmanage.base import BaseSsl, log_info


class QnCertManager(BaseSsl):
    """
    上传SLL证书到七牛
    """
    HOST = "api.qiniu.com"

    def __init__(self, root_domain, domain, cert_file, key_file, access_key, secret_key, mail_svr=None):
        super().__init__(cert_file, key_file)

        if isinstance(domain, str):
            domain = [domain]
        self.domain = domain
        self.root_domain = root_domain
        self.cert_file = cert_file
        self.key_file = key_file
        self.access_key = access_key
        self.secret_key = secret_key
        self.mail_svr = mail_svr

    def handle(self, *args, **options):
        certid, ok = self.upload_ssl()
        domains = self.domain  # ['mt-avatar.hlsgl.top', 'mt-share.hlsgl.top', 'mt-card.hlsgl.top']
        if not ok:
            self.send_mail("upload ssl error: %s" % certid)
            log_info("upload ssl error: %s" % certid)
            return

        log_info("upload ssl success, certID: %s" % certid)
        for domain in domains:
            resp = self.replace_ssl(domain=domain, certid=certid)
            log_info("replace ssl result: %s" % resp.content)

        self.send_mail("证书更新完成: %s" % certid)

    def send_mail(self, msg):
        if self.mail_svr:
            self.mail_svr.send_mail(f'七牛:{msg}')

    def upload_ssl(self):
        session = requests.Session()

        auth = qiniu.Auth(access_key=self.access_key,
                          secret_key=self.secret_key)

        url = "https://{}{}".format(self.HOST, "/sslcert")

        token = auth.token_of_request(url)

        headers = {
            "Authorization": 'QBox {0}'.format(token),
            "Content-Type": "application/json",
            "Host": self.HOST,
        }

        self._get_ssl()

        resp = session.post(url, json={
            "name": "ssl{}new".format(time.strftime('%Y%m%d', time.localtime())),
            "common_name": self.root_domain,
            "ca": self.cert,
            "pri": self.cert_key,
        }, headers=headers)

        if resp.status_code != 200:
            return "", False

        cert_id = resp.json().get("certID", "")
        code = resp.json().get("code", 0)
        if cert_id and code == 200:
            return cert_id, True

        return resp.content, False

    def replace_ssl(self, domain, certid):
        # 替换ssl证书
        session = requests.Session()
        auth = qiniu.Auth(access_key=self.access_key,
                          secret_key=self.secret_key)

        url = "https://{}/domain/{}/httpsconf".format(self.HOST, domain)

        token = auth.token_of_request(url)

        headers = {
            "Authorization": 'QBox {0}'.format(token),
            "Content-Type": "application/json",
            "Host": self.HOST,
        }

        resp = session.put(url, json={
            'certid': certid,
            'forceHttps': False,
        }, headers=headers)

        return resp

