from setuptools import setup, find_packages

setup(
    name='nameko-mongodb',
    version='0.1-alpha',
    description='@TODO',
    long_description='@TODO',
    author='Fill Q',
    author_email='fill@njoyx.net',
    url='https://github.com/NJoyX/nameko-mongodb',
    license='Apache License, Version 2.0',
    packages=find_packages(),
    install_requires=[
        "nameko",
        "monotonic",
        "pymongo",
        "mongoengine"
    ],
    include_package_data=True,
    zip_safe=False,
    keywords=['nameko', 'cassandra', 'database', 'bigdata'],
    classifiers=[
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ]
)
