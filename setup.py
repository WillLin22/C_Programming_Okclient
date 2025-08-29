from setuptools import setup, find_packages
import client

VERSION = client.__version__ 
setup(
    name="okpy-slim",
    version=VERSION,
    author="WillLin",
    description="A lightweight OK client implementation for assignments.",
    url="https://github.com/WillLin22/C_Programming_Okclient.git",  # 你如果没有 GitHub 可以删掉
    license="Apache License, Version 2.0",
    keywords=["education", "autograding"],
    packages=find_packages(include=["client", "client.*"]),
    entry_points={
        "console_scripts": [
            "ok = client.ok:main",  # 这里假设 client/ok.py 里面有 main()
        ],
    },
    install_requires=[
        "pyaes>=1.6.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)