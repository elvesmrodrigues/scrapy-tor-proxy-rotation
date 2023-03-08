# scrapy-tor-proxy-rotation
The purpose of this module is to allow rotation of IPs to [Scrapy](https://scrapy.org/) via Tor.

## Installation

Simple way to install, via **pip**:

```bash
pip install scrapy-tor-proxy-rotation
```

## Configuring Tor

You need to configure **Tor**. First, install it:

```bash
sudo apt-get install tor
```

Stop its execution to perform configuration:

```bash
sudo service tor stop
```

Open your configuration file as root, available at `/etc/tor/torrc`, for example using nano:

```bash
sudo nano /etc/tor/torrc
```

Insert the lines below and save:

```
ControlPort 9051
CookieAuthentication 0
```

Restart Tor:

```bash
sudo service tor start
```

You can check your machine's IP and compare it with Tor's by doing the following:

- To see your machine's IP:
    ```bash
    ```bash
    curl http://icanhazip.com/
    ```
- To see Tor's IP:
    ```bash
    torify curl http://icanhazip.com/   
    ```

Tor proxies are not supported by Scrapy. To get around this problem, it is necessary to use an intermediary, in this case **[Privoxy](https://www.privoxy.org/)**.

> The Tor proxy server is by default at 127.0.0.1:9050

## Installing and configuring **Privoxy**:
- Install: 
    ```bash
    sudo apt install privoxy
    ```
- Stop its execution:
    ```bash
    sudo service privoxy stop
    ```
- Configure it to use TOr, open its configuration file:
    ```bash
    sudo nano /etc/privoxy/config
    ```
- Add the following lines:
    ```bash
    forward-socks5t / 127.0.0.1:9050 .
    ``` 
- Start it up: 
    ```
    service privoxy start
    ```

> By default, privoxy will run at the address 127.0.0.1:8118 

Test: 
```bash
torify curl http://icanhazip.com/
```
```bash
curl -x 127.0.0.1:8118 http://icanhazip.com/
```

The IP shown in the two steps above must be the same.

## How to use

After you have made these settings, you can now integrate Tor with Scrapy.

- Configure the middleware in your project's configuration file (**settings.py**):
    ```python
    DOWNLOADER_MIDDLEWARES = {
        ...,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        'tor_ip_rotator.middlewares.TorProxyMiddleware': 100
    }
    ```
    
- Enable the use of extension:  
    ```python
    TOR_IPROTATOR_ENABLED = True
    TOR_IPROTATOR_CHANGE_AFTER = #number of requests made on the same Tor's IP address
    ```

By default, an IP can be reused after 10 other uses. This value can be changed by the variable TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER, as below:

```python
TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER = 0 #another integer value
```

A number too large for TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER may make it slower to retrieve a new IP for use or not find one at all. If the value is 0, there will be no record of used IPs.
