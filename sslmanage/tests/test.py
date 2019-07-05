# coding: utf-8
import argparse
from sslmanage import QnCertManager
from sslmanage import HTTPClient, UpLogin, UpCertManager
from sslmanage import Mail


def _qiniu_ssl(cert_option):
    access_key = 'xx'
    secret_key = 'xx'
    cmd = QnCertManager(cert_option['root_domain'],
                        cert_option['domain']['qiniu'],
                        cert_option['cert_file'],
                        cert_option['key_file'],
                        access_key,
                        secret_key)
    # 上传ssl
    # cmd.upload_ssl()

    cmd.handle()


def _upyun_ssl(cert_option):
    req_session = HTTPClient()
    stmpSvr = Mail(smtp_host="smtp.exmail.qq.com",
                   smtp_prot="465",
                   smtp_user="xx",
                   smtp_pass="xx",
                   receiver_mail="x@qq.com")
    #  登录
    UpLogin(req_session, user='x', passwd='x')
    certManager = UpCertManager(req_session,
                                domain=cert_option['domain']['upyun'],
                                cert_file=cert_option['cert_file'],
                                key_file=cert_option['key_file'],
                                mail_svr=stmpSvr)
    # 获取证书
    # certManager.get_cert_by_domain()

    # 上传证书
    certManager.add_cert()
    # 更新证书
    certManager.set_cert()


def run_test(platform, cert_option):
    platform_task = {
        'upyun': _upyun_ssl,
        'qiniu': _qiniu_ssl
    }
    platforms = platform.split(',')
    for task in platforms:
        taskcall = platform_task.get(task)
        taskcall and taskcall(cert_option)


if __name__ == '__main__':
    # python test.py --domain hlsgl.top --cert_dir /home/kaifazhe/Downloads/invit.vip/ --platform qiniu,upyun
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", help="根域如invit.vip 不加二级域名", type=str)
    parser.add_argument("--cert_dir", help="证书目录", type=str)
    parser.add_argument("--platform", help="七牛｜又拍云", type=str)
    args = parser.parse_args()

    cert_task_map = {
        'hlsgl.top': {
            'root_domain': 'hlsgl.top',
            'domain': {
                'upyun': ['wwj.hlsgl.top'],
                'qiniu': ['mt-avatar.hlsgl.top', 'mt-share.hlsgl.top', 'mt-card.hlsgl.top']
            },
            'cert_file': f'{args.cert_dir}fullchain.cer',
            'key_file': f'{args.cert_dir}{args.domain}.key'
        },
        'invit.vip': {
            'root_domain': 'invit.vip',
            'domain': {
                'qiniu': 'img1.invit.vip'
            },
            'cert_file': f'{args.cert_dir}{args.domain}.crt',
            'key_file': f'{args.cert_dir}{args.domain}.key'
        }
    }
    run_test(args.platform, cert_task_map[args.domain])
