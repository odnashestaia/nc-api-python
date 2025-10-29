from typing import Any, Dict, Optional

import requests
from requests import Response
from requests.auth import HTTPBasicAuth


class BaseManager:
    def __init__(self, NEXTCLOUD_URL: str, USERNAME: str, PASSWORD: str) -> None:
        self.NEXTCLOUD_URL: str = NEXTCLOUD_URL
        self.USERNAME: str = USERNAME
        self.PASSWORD: str = PASSWORD

    def _request_webdav(
        self,
        method: str,
        path: str,
        data: Optional[bytes | str] = None,
        headers: Optional[Dict[str, str]] = None,
        is_rest: bool = False,
        **kwargs: Any,
    ) -> Response:
        """
        Unified entry point for all HTTP requests to the Nextcloud API.

        :param method: HTTP method (GET, PUT, POST, DELETE, PROPFIND, MOVE, etc.)
        :param path: Path on the Nextcloud server
        :param data: Data to send (for PUT/POST)
        :param headers: Additional headers
        :param kwargs: Additional parameters for requests
        :return: requests.Response object
        """
        if is_rest:
            url = "/"
        else:
            url = "/remote.php/dav/files/" + self.USERNAME
        url = self.NEXTCLOUD_URL + url + path
        auth = HTTPBasicAuth(self.USERNAME, self.PASSWORD)

        request_headers: Dict[str, str] = headers or {}

        response: Response = requests.request(
            method=method,
            url=url,
            data=data,
            headers=request_headers,
            auth=auth,
            **kwargs,
        )

        return response
