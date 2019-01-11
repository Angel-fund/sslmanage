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
# 获取证书
# certManager.get_cert_by_domain()

# 上传证书
certManager.add_cert()
# 更新证书
certManager.set_cert()
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

###