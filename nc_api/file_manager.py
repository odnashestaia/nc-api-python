import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional, Union

from requests import HTTPError

from nc_api.base_manager import BaseManager
from nc_api.xml_query.file_manager import propfind_xml


class FileManager(BaseManager):
    def __init__(
        self,
        NEXTCLOUD_URL: str,
        USERNAME: str,
        PASSWORD: str,
        directory_manager: Optional[Any] = None,
    ) -> None:
        super().__init__(NEXTCLOUD_URL, USERNAME, PASSWORD)
        self.directory_manager = directory_manager

    def upload_file(
        self,
        LOCAL_UPLOAD_PATH: Optional[str] = None,
        FILE: Optional[bytes] = None,
        REMOTE_UPLOAD_PATH: Optional[str] = None,
    ) -> bool:
        """
        Uploads a file to Nextcloud. Creates target directory if needed.

        :param LOCAL_UPLOAD_PATH: Local file path to upload
        :param FILE: Raw file bytes to upload (alternative to LOCAL_UPLOAD_PATH)
        :param REMOTE_UPLOAD_PATH: Remote path in Nextcloud
        :return: True if successful
        """
        try:
            # Extract directory path from the REMOTE_UPLOAD_PATH
            remote_dir = "/".join(REMOTE_UPLOAD_PATH.split("/")[:-1])

            # Check if the directory exists
            dir_check = self.directory_manager.directory_exists_check(remote_dir)
            if not dir_check:
                raise HTTPError(f"Directory does not exist: {remote_dir}")

            # Proceed with file upload
            if FILE:
                response = self._request_webdav("PUT", REMOTE_UPLOAD_PATH, data=FILE)
            else:
                with open(LOCAL_UPLOAD_PATH, "rb") as file:
                    file_data = file.read()
                response = self._request_webdav(
                    "PUT", REMOTE_UPLOAD_PATH, data=file_data
                )
            if response.status_code in [200, 201, 207, 206]:
                return True
            else:
                raise HTTPError(
                    f"Failed to upload file: {response.status_code} - {response.text}",
                    response=response,
                )
        except Exception as e:
            raise Exception(f"Failed to upload file: {e}") from e

    def download_file(
        self, LOCAL_DOWNLOAD_PATH: str, REMOTE_DOWNLOAD_PATH: str
    ) -> bool:
        """
        Downloads a file from Nextcloud.

        :param LOCAL_DOWNLOAD_PATH: Local path to save the file
        :param REMOTE_DOWNLOAD_PATH: Remote path to download from
        :return: True if successful
        """
        try:
            # Send a request to GET a file from REMOTE_DOWNLOAD_PATH.
            response = self._request_webdav("GET", REMOTE_DOWNLOAD_PATH)
            if response.status_code in [200, 201, 207, 206]:
                with open(LOCAL_DOWNLOAD_PATH, "wb") as file:
                    file.write(response.content)
                return True
            else:
                raise HTTPError(
                    f"Failed to download file: {response.status_code} - {response.text}",
                    response=response,
                )
        except Exception as e:
            raise Exception(f"Failed to download file: {e}") from e

    def get_data_file(self, REMOTE_FILE_PATH: str) -> Union[Dict[str, str], str]:
        """
        Retrieves metadata of a file from Nextcloud via WebDAV PROPFIND.

        :param REMOTE_FILE_PATH: Remote file path in Nextcloud
        :return: Dict with metadata or error string
        """
        try:
            # Send PROPFIND request
            response = self._request_webdav(
                "PROPFIND",
                REMOTE_FILE_PATH,
                data=propfind_xml,
                headers={"Depth": "0", "Content-Type": "application/xml"},
            )

            if response.status_code in [200, 201, 207, 206]:
                # Parse XML response
                root = ET.fromstring(response.text)

                # Collect properties
                namespace = {
                    "d": "DAV:",
                    "oc": "http://owncloud.org/ns",
                    "nc": "http://nextcloud.org/ns",
                }

                file_data = {}

                for response_elem in root.findall(".//d:response", namespace):
                    href = response_elem.find(".//d:href", namespace)
                    if href is not None:
                        file_data["href"] = href.text

                    propstat = response_elem.find(".//d:propstat", namespace)
                    if propstat is not None:
                        prop = propstat.find(".//d:prop", namespace)
                        if prop is not None:
                            # Flatten properties
                            for elem in prop:
                                tag_name = elem.tag
                                # Strip namespace
                                if "}" in tag_name:
                                    tag_name = tag_name.split("}")[1]

                                value = elem.text if elem.text else ""
                                file_data[tag_name] = value

                return file_data
            elif response.status_code == 404:
                raise RuntimeError(
                    f"File not found: {REMOTE_FILE_PATH}", response=response
                )
            else:
                raise HTTPError(
                    f"HTTP error: {response.status_code} - {response.text}",
                    response=response,
                )

        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML: {e}") from e
        except Exception as e:
            raise Exception(f"Failed to retrieve file metadata: {e}") from e
