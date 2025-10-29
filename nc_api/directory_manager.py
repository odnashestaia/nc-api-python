from typing import Union

from requests import HTTPError

from nc_api.base_manager import BaseManager


class DirectoryManager(BaseManager):
    def __init__(self, NEXTCLOUD_URL, USERNAME, PASSWORD):
        super().__init__(NEXTCLOUD_URL, USERNAME, PASSWORD)

    def directory_exists_check(self, DIRECTORY_PATH: str) -> Union[bool, str]:
        """
        Checks if a directory exists in Nextcloud storage.

        :param DIRECTORY_PATH: The path of the directory to check.
        :return: True if exists, False if not, or error message string.
        """
        try:
            # Send a PROPFIND request to check if the directory exists
            response = self._request(
                "PROPFIND",
                DIRECTORY_PATH,
                headers={"Depth": "1"},
            )
            if response.status_code == 207:
                # 207 means directory exists (WebDAV specific)
                return True
            else:
                raise HTTPError(
                    f"Failed to check if directory exists: {response.status_code} - {response.text}",
                    response=response,
                )
        except Exception:
            return False

    def create_directory(self, DIRECTORY_PATH: str) -> bool:
        """
        Создаёт директорию в Nextcloud с помощью WebDAV MKCOL.

        :param DIRECTORY_PATH: Путь директории для создания.
        :return: True при успехе или если директория уже существует.
        """
        if not isinstance(DIRECTORY_PATH, str) or not DIRECTORY_PATH:
            raise ValueError("DIRECTORY_PATH must be a non-empty string.")

        response = self._request("MKCOL", DIRECTORY_PATH)

        if response.status_code == 201:
            return True
        if response.status_code == 405:
            return True
        if response.status_code == 409:
            raise FileNotFoundError(
                f"Parent directory does not exist for '{DIRECTORY_PATH}'."
            )

        raise HTTPError(
            f"Failed to create directory '{DIRECTORY_PATH}': {response.status_code} - {response.text}",
            response=response,
        )
