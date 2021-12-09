import os
import platform
import zipfile
from urllib.request import urlopen
from warnings import warn

import setuptools

assert(platform.system() == 'Windows')

dll = 'x64/txmlconnector64.dll' if platform.machine() == 'AMD64' \
    else 'win32/txmlconnector.dll'
if not os.path.exists(dll):
    warn("Transaq Connector DLL not found, downloading from Finam")
    zip = "TXmlConnector.zip"
    url = "https://files.comon.ru/usercontent/" + zip
    open(zip, 'wb').write(urlopen(url).read())
    zipfile.ZipFile(zip, 'r').extractall()

setuptools.setup(
    name='transaq_connector',
    version='1.1',
    packages=['transaq'],
    package_dir={'transaq': '.'},
    package_data={'transaq': [dll]},
    requires=['eulxml', 'lxml'],
    url='https://github.com/ZaitsevY/transaq_connector',
    license='BSD',
    author='Roman Voropaev',
    author_email='voropaev.roma@gmail.com',
    description='Python Transaq XML Connector',
    platforms=['Windows'],
    python_requires='>=3.6',
    long_description=u"TRANSAQ Connector представляет собой открытый\
        программный интерфейс TRANSAQ (API), который позволяет\
        подключать к торговому серверу TRANSAQ собственные приложения.",
)
