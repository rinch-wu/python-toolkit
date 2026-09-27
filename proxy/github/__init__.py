from ._github_proxy_abc import GithubProxy, split


github_proxy_list = [
    GithubProxy(
        # 85.8.68.2:80
        '/casals-ar/proxy-list',
        ['/http', '/https', '/socks4', '/socks5'],
        # lambda filepath: split(filepath)[1] + '://',
        # lambda data: data.split('\n'),
    ),
    GithubProxy(
        # http://181.78.23.194:999
        '/proxifly/free-proxy-list',
        ['/proxies/protocols/http/data.txt', '/proxies/protocols/socks4/data.txt', '/proxies/protocols/socks5/data.txt'],
        lambda filepath: '',
    ),
    GithubProxy(
        # 167.86.115.218:8888
        '/Zaeem20/FREE_PROXIES_LIST',
        ['/http.txt', '/https.txt', '/socks4.txt', '/socks5.txt'],
    ),
    GithubProxy(
        # 38.156.233.78:999
        '/prxchk/proxy-list',
        ['/http.txt', '/socks4.txt', '/socks5.txt'],
    ),
    GithubProxy(
        # 188.34.156.119:8080
        '/MuRongPIG/Proxy-Master',
        ['/http.txt', '/socks4.txt', '/socks5.txt'],
    ),
]
