# TODO feat: refresh expired tokens
# TODO feat: more methods
# TODO tests: add

from dataclasses import dataclass, field
import hmac
import json
import logging
import secrets
import time
from typing import Any, Iterator, Optional, Union
from urllib.parse import quote

from requests import Session

from . import requests as _r

# === Defaults ===
DEFAULT_HEADERS = {
    "Accept": "application/json; charset=utf-8",
    "Accept-Encoding": "identity",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; GT-N7100 Build/MOB30R)",
    "X-Api-Version": "1.18",
    "X-Client-Type": "android_4.67.1",
}
DEFAULT_HOST = "api.ask.fm:443"
DEFAULT_LIMIT = 50

# === Types ===
ReqParams = dict[str, Any]
StrParams = dict[str, str]
Response = Any


@dataclass
class Request:
    method: str
    path: str
    params: ReqParams = field(default_factory=dict)
    name: Optional[str] = None
    unwrap_key: Optional[str] = None
    paginated: bool = False
    item_id_key: Optional[str] = None


class AskfmApiError(Exception):
    def __init__(self, response: Response) -> None:
        super().__init__(response["error"])


class AskfmApi:
    def __init__(
        self,
        api_key: str,
        *,
        device_id: Optional[str] = None,
        access_token: Optional[str] = None,
        host: str = DEFAULT_HOST,
        headers: dict[str, str] = DEFAULT_HEADERS,
    ) -> None:
        self.api_key = api_key.encode("ascii")
        self.device_id = device_id or secrets.token_hex(8)
        self.rt = "1"

        self.sess = Session()
        self.host = host
        self.sess.headers["Host"] = host
        self.sess.headers.update(headers)

        if access_token is None:
            access_token = self.request(_r.fetch_access_token(self.device_id))
        self.set_access_token(access_token)

    def request(
        self,
        req: Request,
        *,
        unwrap: bool = True,
        offset: int = 0,
        limit: int = DEFAULT_LIMIT,
    ) -> Response:
        if req.paginated:
            params = {"offset": offset, "limit": limit, **req.params}
        else:
            params = req.params

        res = self.request_raw(req.method, req.path, params)

        if "error" in res:
            raise AskfmApiError(res)

        if unwrap and req.unwrap_key:
            res = res[req.unwrap_key]

        return res

    def request_iter(
        self,
        req: Request,
        *,
        offset: int = 0,
        page_limit: int = DEFAULT_LIMIT,
    ) -> Iterator[Response]:
        if not req.paginated or not req.unwrap_key:
            raise TypeError("Cannot iterate non-paginated request")

        while True:
            res = self.request(req, offset=offset, limit=page_limit, unwrap=False)
            items = res[req.unwrap_key]
            if not items:  # strangely, API always returns hasMore=True
                break
            yield from items
            if not res["incomplete"] and not res["hasMore"]:
                break
            offset += len(items)

    def request_raw(
        self, method: str, path: str, params: Optional[ReqParams] = None
    ) -> Response:
        params = params or {}
        method = method.upper()
        has_body = method in ["POST", "PUT"]
        url = "https://" + self.host + path

        params = {"rt": self.rt, "ts": int(time.time()), **params}
        params = {
            k: (str(v) if isinstance(v, (int, bool)) else v) for k, v in params.items()
        }
        if has_body:
            params = {"json": json.dumps(params, sort_keys=True, separators=(",", ":"))}

        signature = f"HMAC {self.get_signature(method, path, params)}"

        data_: Optional[StrParams]
        params_: Optional[StrParams]
        if has_body:
            data_, params_ = params, None
        else:
            data_, params_ = None, params

        res = self.sess.request(
            method,
            url,
            data=data_,
            params=params_,
            headers={"Authorization": signature},
        )

        if "X-Next-Token" in res.headers:
            self.rt = res.headers["X-Next-Token"]

        res = res.json()
        return res

    def get_signature(self, method: str, path: str, params: StrParams) -> str:
        quoted = [key + "%" + quote(val, safe="!'()~") for (key, val) in params.items()]
        msg = "%".join(sorted(quoted))
        msg = "%".join([method.upper(), self.host, path, msg])

        hmac_ = hmac.new(self.api_key, msg.encode(), "sha1")
        return hmac_.hexdigest()

    def login(self, uname: str, passwd: str) -> Response:
        req = _r.login(uname, passwd, self.device_id)
        res = self.request(req)
        self.set_access_token(res["accessToken"])
        return res["user"]

    def set_access_token(self, token: str) -> None:
        self.access_token = token
        self.sess.headers["X-Access-Token"] = token
