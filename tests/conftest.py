import os

import pytest

from nc_api.base_manager import BaseManager
from nc_api.client import NextcloudClient
from nc_api.directory_manager import DirectoryManager
from nc_api.file_manager import FileManager
from nc_api.path_manager import PathManager
from nc_api.user_manager import UserManager


@pytest.fixture(scope="session")
def nc_url() -> str:
    return os.environ.get("NC_URL", "https://f75180c6f4db.ngrok-free.app")


@pytest.fixture(scope="session")
def nc_user() -> str:
    return os.environ.get("NC_USER", "admin")


@pytest.fixture(scope="session")
def nc_pass() -> str:
    return os.environ.get("NC_PASS", "admin")


class WebDavDirectoryHelper(BaseManager):
    """Минимальный помощник для операций MKCOL/PROPFIND без изменения исходников."""

    def DirectoryExists_Check(self, path: str) -> bool:
        r = self._request_webdav("PROPFIND", path, headers={"Depth": "1"})
        if r.status_code == 207:
            return True
        if r.status_code == 404:
            return False
        raise RuntimeError(f"Unexpected response: {r.status_code} - {r.text}")

    def CreateDirectory(self, path: str) -> bool:
        r = self._request_webdav("MKCOL", path)
        if r.status_code in (201, 405):
            return True
        raise RuntimeError(f"Failed to create dir: {r.status_code} - {r.text}")


@pytest.fixture()
def managers(nc_url: str, nc_user: str, nc_pass: str):
    base = BaseManager(nc_url + "/remote.php/dav/files/" + nc_user, nc_user, nc_pass)
    helper = WebDavDirectoryHelper(
        nc_url + "/remote.php/dav/files/" + nc_user, nc_user, nc_pass
    )

    dirs = DirectoryManager(
        nc_url + "/remote.php/dav/files/" + nc_user, nc_user, nc_pass
    )
    files = FileManager(
        nc_url + "/remote.php/dav/files/" + nc_user,
        nc_user,
        nc_pass,
        directory_manager=helper,
    )
    paths = PathManager(
        nc_url + "/remote.php/dav/files/" + nc_user,
        nc_user,
        nc_pass,
        directory_manager=helper,
        file_manager=files,
    )
    users = UserManager(nc_url, nc_user, nc_pass)
    client = NextcloudClient(
        nc_url + "/remote.php/dav/files/" + nc_user, nc_user, nc_pass
    )
    return {
        "base": base,
        "dirs": dirs,
        "files": files,
        "paths": paths,
        "users": users,
        "client": client,
        "helper": helper,
    }
