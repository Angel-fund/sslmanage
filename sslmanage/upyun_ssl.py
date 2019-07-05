# coding: utf-8
import json
import time

import requests
from collections import OrderedDict

from sslmanage.base import BaseSsl, log_info

HEADER = {
    "Content-Type": "application/json",
    "Origin": "https://console.upyun.com",
    "Referer": "https://console.upyun.com/login/?from=https:%2F%2Fwww.upyun.com%2F",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}

URLS = {
    'auth': '/accounts/signin/',
    'add_cert': '/api/https/certificate/',
    'cert': '/api/https/certificate/manager',
    'cert_service': '/api/https/services/manager',
    'bucket_domain': '/api/buckets/domains/',
    'bucket': '/api/buckets/info/',
    'migrate_cert': '/api/https/migrate/certificate',
}


class HTTPClient:
    def __init__(self):
        """
        :param method:
        :param headers: Must be a dict. Such as headers={'Content_Type':'text/html'}
        """
        self.init()

    @staticmethod
    def _set_header_default():
        header_dict = OrderedDict()
        header_dict["Accept"] = "application/json, text/plain, */*"
        header_dict["Content-Type"] = "application/json"
        header_dict["Origin"] = "https://console.upyun.com"
        header_dict[
            "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) 12306-electron/1.0.1 Chrome/59.0.3071.115 Electron/1.8.4 Safari/537.36"
        header_dict["Referer"] = "https://console.upyun.com/login/?from=https:%2F%2Fwww.upyun.com%2F"
        return header_dict

    def init(self):
        self._s = requests.Session()
        self._s.headers.update(self._set_header_default())

        return self

    def set_cookies(self, **kwargs):
        """
        设置cookies
        :param kwargs:
        :return:
        """
        for k, v in kwargs.items():
            self._s.cookies.set(k, v)

    def get_cookies(self):
        """
        获取cookies
        :return:
        """
        return self._s.cookies.values()

    def set_headers(self, headers):
        self._s.headers.update(headers)
        return self

    def reset_headers(self):
        self._s.headers.clear()
        self._s.headers.update(self._set_header_default())

    def get_headers_referer(self):
        return self._s.headers["Referer"]

    def set_headers_referer(self, referer):
        self._s.headers.update({"Referer": referer})
        return self

    def send(self, urls, method=None, **kwargs):
        requests.packages.urllib3.disable_warnings()
        req = getattr(self._s, method.lower())
        response = req(f'https://console.upyun.com{urls}', **kwargs)

        if response.status_code == 200:
            return response
        else:
            log_info('req err', response.content)
            return None


class UpLogin:
    def __init__(self, session, user, passwd):
        self.session = session
        self.baseLogin(user, passwd)

    def baseLogin(self, user, passwd):
        """
        登录过程
        :param user:
        :param passwd:
        """
        logurl = URLS['auth']
        params = {
            "username": user,
            "password": passwd,
            "from": "https://www.upyun.com/"
        }
        result = self.session.send(logurl, method='post', json=params)


class UpCertManager(BaseSsl):
    """
    upyun cert管理: 添加证书 ->获取域名证书列表 ->选择最新证书 ->设置证书
    domain为数组时可以多个域名共用一张证数
    """
    def __init__(self, session, domain, cert_file, key_file, mail_svr=None):
        super().__init__(cert_file, key_file)

        self.session = session
        self.cert_file = cert_file
        self.key_file = key_file
        self.mail_svr = mail_svr
        if isinstance(domain, str):
            domain = [domain]
        self.domain = domain

    def add_cert(self):
        self._get_ssl()
        params = {
            'certificate': self.cert,
            'private_key': self.cert_key
        }
        req_url = URLS['add_cert']
        resp = self.session.send(req_url, method='post', data=json.dumps(params).encode('utf-8'))
        cert_info = resp.content.decode()
        log_info(f'upssl =>{cert_info}')

    def get_cert_by_cid(self, cid):
        """
        获取证书详情
        :param cid:
        :return: {"data":{
            "authenticate_num":2,
            "authenticate_domain":[
                "hlsgl.top",
                "*.hlsgl.top"
            ],
            "domains":[
                {
                    "name":"cdn.hlsgl.top",
                    "type":"file",
                    "bucket_id":1083190,
                    "bucket_name":"annecard",
                    "https":true,   # 启用了此项则开启了https
                    "force_https":false,
                    "source_https":false
                },
                {
                    "name":"mt-cdn.hlsgl.top",
                    "type":"file",
                    "bucket_id":851187,
                    "bucket_name":"mt-card",
                    "https":true,
                    "force_https":false,
                    "source_https":false
                },
                {
                    "name":"wwj.hlsgl.top",
                    "type":"file",
                    "bucket_id":966782,
                    "bucket_name":"funclaw"
                }
            ]
        }}
        """
        req_url = URLS['cert']
        certificate_info = self.session.send(req_url, method='GET', params={'certificate_id': cid})
        return certificate_info

    def migrate_cert(self, old_crt_id, new_crt_id):
        # 查询旧证书上是否有迁移域名
        # old_crt_info = self.get_cert_by_cid(old_crt_id)
        # if old_crt_id.get('data').get('authenticate_num') > 0:
        #     pass

        req_url = URLS['migrate_cert']
        resp = self.session.send(req_url, method='post', json={
                                  "old_crt_id": old_crt_id,
                                  "new_crt_id": new_crt_id
                                })
        cert_info = resp.json()
        return len(cert_info.get('msg').get('errors')) == 0

    def send_mail(self, msg):
        if self.mail_svr:
            self.mail_svr.send_mail(f'又拍云:{msg}')
        print(msg)

    def set_cert(self):
        """ 设置cert是否开启
        :return {
            "data": {"status": true},
            "msg": {"errors": [], "messages": []}
        }
        """
        certificate_id, pre_cert_id = self.get_cert_by_domain()
        log_info(f'cert={certificate_id} pre={pre_cert_id}')
        # 无可用证书邮件通知
        if not certificate_id:
            self.send_mail("无可用证书")
            return

        # 存在新旧证书,迁移证书
        if pre_cert_id:
            ok = self.migrate_cert(pre_cert_id, certificate_id)
            mail_msg = "迁移证书完成"
            if not ok:
                mail_msg = "迁移证书失败"

            self.send_mail(mail_msg)
            return

        success_domain = []
        fail_domain = []
        for domain in self.domain:
            params = {
                # "name": "wwj.hlsgl.top",
                # "type": "file",
                # "bucket_id": 966782,
                # "bucket_name": "funclaw",
                # 必传参数
                "certificate_id": certificate_id,
                "domain": domain,
                "https": True,    # false
                "force_https": False    # 强制https
                # 取消cert
                # certificate_id: "c16c706e7306f219bb854e6630b6d39e"
                # domain: "wwj.invit.vip"
                # force_https: false
                # https: false
            }

            req_url = URLS['cert']
            resp = self.session.send(req_url, method='post', data=json.dumps(params).encode('utf-8'))
            cert_info = resp.json()
            if cert_info.get('data').get('status'):
                log_info(f'replace {domain} =>{cert_info}')
                success_domain.append(domain)
            else:
                fail_domain.append(domain)
        return success_domain, fail_domain

    def get_cert_by_domain(self):
        # https://console.upyun.com/api/https/services/manager?domain=wwj.hlsgl.top
        """ 根据域名获取cert
        :return {
            data": {
                "result": [{
                    brand: ""
                    certificate_id: "5d67ce8e92af59c83526965774c6cf31"
                    commonName: "hlsgl.top"
                    crt_type: "custom"
                    crt_type_pay: ""
                    domain_type: ""
                    force_https: false
                    https: false
                    organization: ""
                    payment_type: "free"
                    pro: false
                    source_https: false
                    validity: {start: 1546753173000, end: 1554529173000}
                    end: 1554529173000
                    start: 1546753173000
                    validity: {start: 1546753173000, end: 1554529173000}
                }]
                "status"
            }
        }
        """
        req_url = URLS['cert_service']
        params = {'domain': self.domain[0]}
        resp = self.session.send(req_url, method='GET', params=params)
        if not resp:
            return None, None
        cert_info = json.loads(resp.content.decode())

        certificate_id = None
        pre_cert_id = None  # 上一次证书的id
        if cert_info.get('data').get('status') == 0:
            cert_list = cert_info['data']['result']
            if len(cert_list) > 0:
                cert_list = sorted(cert_list, key=lambda x: x['validity']['end'], reverse=True)
                certificate = cert_list[0]
                if len(cert_list) > 1:
                    pre_cert = cert_list[1]
                    pre_cert_id = pre_cert['certificate_id']
                # 过期时间大于３天的证书
                if (int(certificate['validity']['end'])/1000) - int(time.time()) > 259200:
                    certificate_id = certificate['certificate_id']
        log_info(f'获取{params["domain"]}最新证书=>{certificate_id}')
        return certificate_id, pre_cert_id

    def get_bucket_info(self, bucket_name):
        """ 获取bucket信息
        :return {
            data: {
                approval_domains: ["wwj.invit.vip", "wwj.hlsgl.top"]
                approval_domains_https: {wwj.hlsgl.top: true}
                approvaling_domains: []
                bucket_name: "funclaw"
                business_type: "file"
                created_at: "2017-07-17 11:59:10"
                status: "enabled"
            }
        }
        """
        req_url = URLS['bucket']
        certificate_info = self.session.send(req_url, method='GET', data={'bucket_name': bucket_name})
        return certificate_info

    def add_bucket_domain(self, bucket_name, domain):
        """ 绑定域名或添加域名
        :return {
            data: {result: true}
        }
        """
        params = {
            "domain": domain,
            "bucket_name": bucket_name
        }
        req_url = URLS['bucket_domain']
        certificate_info = self.session.send(req_url,
                                             method='PUT',
                                             data=json.dumps(params).encode('utf-8'))
        return certificate_info

    def del_cert(self, certificate_id):
        # /api/https/certificate/?certificate_id=c16c706e7306f219bb854e6630b6d39e
        req_url = URLS['add_cert']
        params = {
            'certificate_id': certificate_id
        }
        certificate_info = self.session.send(req_url,
                                             method='DELETE',
                                             params=params)

    def get_domain_by_bucket(self):
        """ 根据bucket获取绑定的域名"""
        pass
