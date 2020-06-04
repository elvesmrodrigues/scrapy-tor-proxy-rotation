# scrapy-tor-ip-rotator
Este módulo tem por finalidade permitir rotação de IPs ao [Scrapy](https://scrapy.org/) via Tor.

## Instalação

Maneira simples de instalação, via **pip**:
```bash
pip install scrapy-tor-ip-rotator
```

## Configurando Tor
É necessário configurar o **Tor**. Primeiramente, instale-o:

```bash
sudo apt-get install tor
```

Pare sua execução para realizar configurações:

```bash
sudo service tor stop
```

Abra seu arquivo de configuração como root, disponível em */etc/tor/torrc*, por exemplo, usando o nano:

```bash
sudo nano /etc/tor/torrc
```
Coloque as linhas abaixo e salve:

```
ControlPort 9051
CookieAuthentication 0
```

Reinicie o Tor:

```bash
sudo service tor start
```


É possível verificar o IP de sua máquina e comparar com o do Tor da seguinte forma:
- Para ver seu IP:
    ```bash
    curl http://icanhazip.com/
    ```
- Para ver o IP do TOR:
    ```bash
    torify curl http://icanhazip.com/   
    ```

Proxy do Tor não são suportados pelo Scrapy. Para contornar esse problema, é necessário o uso de um intermediário, nesse caso o **[Privoxy](https://www.privoxy.org/)**. 

> O servidor proxy do Tor se encontra, por padrão, no endereço 127.0.0.1:9050

## Instalação e configuração do **Privoxy**:
- Instalar: 
    ```bash
    sudo apt install privoxy
    ```
- Pare sua execução:
    ```bash
    sudo service privoxy stop
    ```
- Configurá-lo para usar Tor, abra seu arquivo de configuração:
    ```bash
    sudo nano /etc/privoxy/config
    ```
- Adicione as seguintes linhas:
    ```bash
    forward-socks5t / 127.0.0.1:9050 .
    ``` 
- Inicie-o: 
    ```
    service privoxy start
    ```

> Por padrão, privoxy executará no endereço 127.0.0.1:8118 

Teste: 
```bash
torify curl http://icanhazip.com/
```
```bash
curl -x 127.0.0.1:8118 http://icanhazip.com/
```
O IP mostrado nos dois passos acima deve ser o mesmo.

## Uso

Após realizar essas configurações, já é possível integrar o Tor ao Scrapy.
- Ative a extensão e configure o middleware no arquivo de configuração de seu projeto (**settings.py**):
    ```python
    EXTENSIONS = {
    ...,
        'tor_ip_rotator.extensions.TorRenewIp': 1,
    }

    DOWNLOADER_MIDDLEWARES = {
        ...,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        'tor_ip_rotator.middlewares.ProxyMiddleware': 100
    }
    ```
    
- Habilite o uso da extensão:  
    ```python
    TOR_IPROTATOR_ENABLED = True
    TOR_IPROTATOR_ITEMS_BY_IP = #número de requisições feitas em um mesmo endereço IP
    ```
Por padrão, um IP poderá ser reutilizado após 10 usos de outros. Esse valor pode ser alterado pela variável TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER, como abaixo:

```python
TOR_IPROTATOR_ALLOW_REUSE_IP_AFTER = #
```

Um número grande demais pode tornar mais lento recuperar um novo IP para uso ou nem encontrar. Se o valor for 0, não haverá registro de IPs usados.

## TO-DO
- Teste de unidade 