import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scrapy-tor-ip-rotator",
    version="1.0.7",
    author="Elves M. Rodrigues",
    author_email="elvesmateusrodrigues@gmail.com",
    description="Rotacionador de IP para o Scrapy via Tor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elvesrodrigues/scrapy-tor-ip-rotator",
    packages=setuptools.find_packages(),
    install_requires=[
        'pysocks==1.7.1',
        'requests==2.23.0',
        'stem==1.8.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
    python_requires='>=3.6',
)
