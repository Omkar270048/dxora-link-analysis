import ipaddress
import socket
from urllib.parse import urlparse

import httpx


def validate_url(url: str) -> str:
    if not isinstance(url, str):
        raise ValueError("URL must be a string.")

    value = url.strip()
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("URL must use http or https and include a hostname.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed.")
    if parsed.port and not (1 <= parsed.port <= 65535):
        raise ValueError("URL contains an invalid port.")

    hostname = parsed.hostname.lower().rstrip(".")
    if hostname in ("localhost", "localhost.localdomain") or hostname.endswith(".localhost"):
        raise ValueError("Private or local network addresses are not allowed.")

    try:
        addresses = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80),
                                       type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("URL hostname could not be resolved.") from exc

    for info in addresses:
        ip = ipaddress.ip_address(info[4][0].split("%", 1)[0])
        if (
            ip.is_private or ip.is_loopback or ip.is_link_local
            or ip.is_multicast or ip.is_reserved or ip.is_unspecified
        ):
            raise ValueError("Private or internal network addresses are not allowed.")

    return value


async def validate_redirect_url(url: str) -> str:
    return validate_url(url)