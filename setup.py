import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scrapy-tor-ip-rotator",
    version="1.0.0",
    author="Elves M. Rodrigues",
    author_email="elvesmateusrodrigues@gmail.com",
    description="Rotacionador de IP para o Scrapy via Tor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elvesrodrigues/scrapy-tor-ip-rotator",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'stem',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
