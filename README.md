# scrapy-tor-ip-rotator
Este módulo tem por finalidade permitir rotação de IPs ao [Scrapy](https://scrapy.org/) via Tor.

Esse pacote pode ser instalador via **pip**, por meio do comando:
```bash
pip install scrapy-tor-ip-rotator
```

É necessário configurar o Tor:
- Instale-o, se necessário
    ```bash
    sudo apt install tor
    ```
- Pare sua execução para configurá-lo:
    ```bash
    sudo service tor stop
    ```
- Abra a porta de controle, exetudando o comando abaixo:
    ```bash
    sudo echo "ControlPort 9051" >> /etc/tor/torrc
    ```
- Gere uma senha de acesso (lembre-se dela, será necessária posteriormente):
    ```bash
    sudo echo HashedControlPassword $(tor --hash-password "sua senha" | tail -n 1) >> /etc/tor/torrc
    ```
- Reinicie-o:
    ```bash
    sudo service tor restart
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

Proxy do Tor não são suportados pelo Scrapy, para contornar esse problema, é necessário o uso de um intermediário, nesse caso o **[Privoxy](https://www.privoxy.org/)**. 

> O servidor proxy do Tor se encontra, por padrão, no endereço 127.0.0.1:9050

Passos de instalação e configuração do **Privoxy**:
- Instalar: 
    ```bash
    sudo apt install privoxy
    ```
- Configurá-lo para usar Tor: 
    ```bash
    echo "forward-socks5t / 127.0.0.1:9050 ." >> /etc/privoxy/config
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

Após realizar essas configurações, já é possível integrar o Tor ao Scrapy.
- Ative a extensão e configure o middleware (servirá como intermediário entre as conexões) no arquivo de configuração de seu projeto (**settings.py**):
    ```python
    EXTENSIONS = {
    ...,
        'tor_ip_rotator.extensions.TorRenewIp': 1,
    }

    DOWNLOADER_MIDDLEWARES = {
        ...,
        'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        'tor_ip_rotator.middlewares.ProxyMiddleware': 90
    }
    ```
    - Sinta-se a vontade para alterar o valor de **tor_ip_rotator.middlewares.ProxyMiddleware** por outro valor.
- Habilite o funcionamento da extensão, coloque a senha de configuração do Tor que criou passos atrás e defina o número de requisições a serem feitas por um mesmo IP do Tor:  
    ```python
    TOR_RENEW_IP_ENABLED = True
    TOR_PASSWORD = #senha
    TOR_ITEMS_BY_IP = #número de requisições feitas em um mesmo endereço IP
    ```

Nem sempre ao mandar comando de mudança de IP ao Tor ele alterará para um outro nó de saída não usado. Para contornar isso, a classe TorController (presente no arquivo **tor_controller.py**) foi criada. Ela possui uma lista interna que armazena os últimos **n** IPs usados e tentará até 10 vezes encontrar um novo IP que não esteja nessa lista. 

Para alterar o tamanho dessa lista (que por padrão tem tamanho 10, isto é, um IP já usado poderá ser usado novamente após o uso de 10 outros IPs), altere o valor da variável abaixo conforme necessidade (**settings.py**):
```python
TOR_ALLOW_REUSE_IP_AFTER = #
```

Um número grande demais pode tornar mais lento recuperar um novo IP para uso ou nem encontrar. Se o valor for 0, não haverá registro de IPs usados.
