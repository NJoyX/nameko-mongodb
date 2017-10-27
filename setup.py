from setuptools import setup, find_packages
from functools import reduce

extras = dict(
    tls=['pymongo[tls]'],
    marshmallow=['marshmallow-mongoengine']
)
extras['all'] = reduce(lambda l, r: l+r, extras.values())

setup(
    name='nameko-mongodb',
    version='0.1-rc1',
    description='@TODO',
    long_description='@TODO',
    author='Fill Q',
    author_email='fill@njoyx.net',
    url='https://github.com/NJoyX/nameko-mongodb',
    license='Apache License, Version 2.0',
    packages=find_packages(),
    install_requires=[
        "six",
        "nameko",
        "monotonic",
        "pymongo",
        "mongoengine"
    ],
    extras_require=extras,
    include_package_data=True,
    zip_safe=False,
    keywords=['nameko', 'mongodb', 'database', 'nosql', 'gridfs'],
    classifiers=[
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ]
)
