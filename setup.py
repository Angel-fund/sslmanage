# coding: utf-8
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sslmanage",
    version="1.0.5",
    description="七牛，又拍云证书更新",
    author="osmen",
    license='BSD License',
    keywords="七牛，又拍云证书更新",
    author_email="lijiguan1@gmail.com",
    # py_modules=['qiniu_ssl', 'upyun_ssl', 'base'],
    classifiers=['Programming Language :: Python :: 3.6'],
    url='https://github.com/Angel-fund/sslmanage',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests==2.20.1',
        'qiniu==7.1.4',
    ]
)
