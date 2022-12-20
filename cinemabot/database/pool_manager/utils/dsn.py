from functools import lru_cache
from typing import Any, Optional, Union
from urllib.parse import urlencode

from psycopg2._psycopg import parse_dsn


def host_is_ipv6_address(host: str) -> bool:
    return host.count(":") > 1


class Dsn:
    def __init__(
        self,
        host: str,
        port: Union[str, int],
        user: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        **kwargs: dict[Any, Any],
    ) -> None:
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._dbname = dbname
        self._kwargs = kwargs
        self._compiled_dsn = self._compile_dsn()

    def _compile_dsn(self) -> str:
        dsn = "postgresql://"
        if self._user is not None:
            dsn += self._user
            if self._password is not None:
                dsn += f":{self._password}"
            dsn += "@"

        if host_is_ipv6_address(self._host):
            dsn += f"[{self._host}]:{self._port}"
        else:
            dsn += f"{self._host}:{self._port}"

        if self._dbname is not None:
            dsn += f"/{self._dbname}"

        if self._kwargs:
            qs_params = urlencode(self._kwargs, safe="/~.\"'")
            dsn += f"?{qs_params}"

        return dsn

    @lru_cache()
    def with_(self, **kwargs) -> "Dsn":  # type: ignore
        params = {
            "host": self._host,
            "port": self._port,
            "user": self._user,
            "password": self._password,
            "dbname": self._dbname,
            **self._kwargs,  # type: ignore
            **kwargs,
        }
        return self.__class__(**params)  # type: ignore

    def __str__(self) -> str:
        return self._compiled_dsn

    def __eq__(self, other: Any) -> bool:
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))


def split_dsn(dsn: str, default_port: int = 5432) -> list[Dsn]:
    parsed_dsn = parse_dsn(dsn)

    hosts = parsed_dsn["host"].split(",")
    if "port" in parsed_dsn:
        ports = parsed_dsn["port"].split(",")
        if len(ports) != len(hosts):
            raise ValueError("Host and port amounts dismatch")
    else:
        ports = [None] * len(hosts)

    splited_dsn: list[Dsn] = []
    used_dsn = set()
    for host, port in zip(hosts, ports):
        current_dsn = parsed_dsn.copy()
        current_dsn["host"] = host
        current_dsn["port"] = port or default_port
        dsn_object: Dsn = Dsn(**current_dsn)
        compiled_dsn = str(dsn_object)
        if compiled_dsn not in used_dsn:
            used_dsn.add(compiled_dsn)
            splited_dsn.append(dsn_object)
    return splited_dsn
