from setuptools import setup, find_packages

setup(
    name="misaka-network-v2",
    version="2.0.0",
    author="御坂美琴本尊",
    author_email="misaka@example.com",
    description="御坂网络 V2 - 四角色闭环管理系统",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="."),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
)
