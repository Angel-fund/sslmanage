## 示例
### 又拍云模拟登录上传更新证书
```
# 又拍云没有提供证书更新接口,用模拟登录方式更新
from sslmanage import HTTPClient, UpLogin, UpCertManager
req_session = HTTPClient()
# 又拍云模拟登录上传user: 又拍云网站用户登录名　　passwd:又拍云网站用户登录密码
UpLogin(req_session, user='xx', passwd='xx')
certManager = UpCertManager(req_session,
                            domain=['cdn.xx.com','img.xx.com'],
                            cert_file='/root/xx.com.crt',
                            key_file='/root/xx.com.key',)

# 上传证书
certManager.add_cert()
# 更新证书
certManager.set_cert()
# 获取证书
# certManager.get_cert_by_domain()
```

### 七牛上传更新证书
```
# 填写七牛api账号信息
access_key = 'xx'
secret_key = 'xx'
cmd = QnCertManager(root_domain='xx.com',
                    domain=['cdn.xx.com','img.xx.com'],
                    cert_file='/root/xx.com.crt',
                    key_file='/root/xx.com.key',
                    access_key=access_key,
                    secret_key=secret_key)
cmd.handle()
```

### 编写脚本示例
``` upssl.py
# coding: utf-8
import argparse
from sslmanage import QnCertManager, Mail
from sslmanage import HTTPClient, UpLogin, UpCertManager


def _qiniu_ssl(cert_option):
    print(cert_option)
    # 邮件通知
    stmpSvr = Mail(smtp_host="smtp.exmail.qq.com",
                   smtp_prot="465",
                   smtp_user="xx",
                   smtp_pass="xx!",
                   receiver_mail="xx@qq.com")

    access_key = 'xx'
    secret_key = 'oo'
    cmd = QnCertManager(cert_option['root_domain'],
                        cert_option['domain']['qiniu'],
                        cert_option['cert_file'],
                        cert_option['key_file'],
                        access_key,
                        secret_key,
                        mail_svr=stmpSvr)

    cmd.handle()


def _upyun_ssl(cert_option):
    print(cert_option)
    req_session = HTTPClient()
    stmpSvr = Mail(smtp_host="smtp.exmail.qq.com",
                   smtp_prot="465",
                   smtp_user="xx",
                   smtp_pass="xx!",
                   receiver_mail="xx@qq.com")
    # # # 登录
    UpLogin(req_session, user='xx', passwd='xx')
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", help="根域如invit.vip 不加二级域名", type=str)
    parser.add_argument("--cert_dir", help="证书目录", type=str)
    parser.add_argument("--platform", help="qiniu,upyun 逗号分割多平台", type=str)
    args = parser.parse_args()

    cert_task_map = {
        'xx.top': {
            'root_domain': 'xx.top',
            'domain': {
                'upyun': ['cdn.xx.top', 'mt-cdn.xx.top'],
                'qiniu': 'mt-card.xx.top'
            },
            'cert_file': f'{args.cert_dir}xx.top',
            'key_file': f'{args.cert_dir}xx.top.key'
        },
        'oo.vip': {
            'root_domain': 'oo.vip',
            'domain': {
                'qiniu': 'img1.oo.vip'
            },
            'cert_file': f'{args.cert_dir}oo.vip.crt',
            'key_file': f'{args.cert_dir}oo.vip.key'
        }
    }
    run_test(args.platform, cert_task_map[args.domain])

```

**运行脚本**
```
python upssl.py --domain xx.top --cert_dir /home/kaifazhe/Downloads/xx.top/ --platform qiniu,upyun
```

**将脚本放到 acme.sh证书颁发脚本中**
如颁发　xx.top域名，编辑配置文件
```
 vi ~/.acme.sh/xx.top/xx.top.conf
 Le_ReloadCmd='/xx/python /xxx/upssl.py --domain xx.top --cert_dir /home/kaifazhe/Downloads/xx.top/ --platform qiniu,upyun'
```
每当acme.sh　更新证书时会执行该脚本，这样妈妈再也不用担心证书过期了！