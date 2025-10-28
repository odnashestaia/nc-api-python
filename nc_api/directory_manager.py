from typing import Union

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
            elif response.status_code == 404:
                return False
            else:
                return f"Unexpected response: {response.status_code} - {response.text}"
        except Exception as e:
            return f"An error occurred while checking the directory: {e}"
