import os
from typing import Optional

from requests import HTTPError

from nc_api.base_manager import BaseManager


class PathManager(BaseManager):
    def __init__(
        self,
        NEXTCLOUD_URL: str,
        USERNAME: str,
        PASSWORD: str,
        directory_manager: Optional[object] = None,
        file_manager: Optional[object] = None,
    ) -> None:
        super().__init__(NEXTCLOUD_URL, USERNAME, PASSWORD)
        self.directory_manager = directory_manager
        self.file_manager = file_manager

    def rename_path(self, CURRENT_PATH: str, NEW_PATH: str) -> bool:
        """
        Renames or moves a file or directory in Nextcloud. If the new path requires non-existent folders, they will be created.

        :param CURRENT_PATH: The current path of the file or folder.
        :param NEW_PATH: The new path for the file or folder.
        :return: True if successful
        """
        try:
            # Ensure the paths are valid strings
            if not isinstance(CURRENT_PATH, str) or not isinstance(NEW_PATH, str):
                raise ValueError("Both CURRENT_PATH and NEW_PATH must be strings.")

            # Extract the directory part of the new path
            new_dir = "/".join(NEW_PATH.split("/")[:-1])

            # Create the new directories if they do not exist
            if new_dir and self.directory_manager:
                # Best-effort create missing directories
                try:
                    self.directory_manager.CreateDirectory(new_dir)
                except Exception:
                    pass

            # Construct the full URLs for the old and new paths
            new_url = f"{self.NEXTCLOUD_URL}{NEW_PATH}"

            # Send the MOVE request to rename/move the resource
            response = self._request_webdav(
                "MOVE",
                CURRENT_PATH,
                headers={"Destination": new_url},
            )

            # Handle the response
            if response.status_code in [200, 201, 207, 206]:
                return True
            if response.status_code == 404:
                raise RuntimeError(
                    f"The resource at '{CURRENT_PATH}' does not exist.",
                    response=response,
                )
            if response.status_code == 403:
                raise PermissionError(
                    f"Permission denied to rename/move '{CURRENT_PATH}'.",
                    response=response,
                )
            raise HTTPError(
                f"Failed to rename/move '{CURRENT_PATH}': {response.status_code} - {response.text}",
                response=response,
            )

        except Exception:
            raise

    def delete_path(self, TRAGET_PATH: str) -> bool:
        """
        Deletes a file or directory in Nextcloud. If the target is a directory, it will be deleted recursively.

        :param TRAGET_PATH: The path of the file or folder to delete.
        :return: True if successful
        """
        try:
            # Ensure the path is valid
            if not isinstance(TRAGET_PATH, str):
                raise ValueError("The target_path must be a string.")

            # Send the DELETE request
            response = self._request_webdav("DELETE", TRAGET_PATH)

            # Handle the response
            if response.status_code in [200, 201, 207, 206]:
                return f"Successfully deleted '{TRAGET_PATH}'."
            if response.status_code == 404:
                raise RuntimeError(f"The resource at '{TRAGET_PATH}' does not exist.")
            if response.status_code == 403:
                raise PermissionError(f"Permission denied to delete '{TRAGET_PATH}'.")
            raise HTTPError(
                f"Failed to delete '{TRAGET_PATH}': {response.status_code} - {response.text}",
                response=response,
            )

        except Exception:
            raise

    def upload_folder(self, LOCAL_FOLDER_PATH: str, REMOTE_FOLDER_PATH: str) -> None:
        """
        Uploads a folder and its contents to Nextcloud, overwriting any existing files.

        :param LOCAL_FOLDER_PATH: The local folder path to be uploaded.
        :param REMOTE_FOLDER_PATH: The remote folder path on Nextcloud.
        """
        try:
            for root, dirs, files in os.walk(LOCAL_FOLDER_PATH):
                relative_path = os.path.relpath(root, LOCAL_FOLDER_PATH)
                remote_path = os.path.join(REMOTE_FOLDER_PATH, relative_path).replace(
                    "\\", "/"
                )

                if not self.directory_manager.directory_exists_check(remote_path):
                    self.directory_manager.create_directory(remote_path)

                for file in files:
                    local_file_path = os.path.join(root, file)
                    remote_file_path = os.path.join(remote_path, file).replace(
                        "\\", "/"
                    )

                    with open(local_file_path, "rb") as f:
                        file_data = f.read()

                    response = self._request_webdav(
                        "PUT", remote_file_path, data=file_data
                    )
                    if response.status_code in [200, 201, 207, 206]:
                        continue
                    if response.status_code == 409:
                        # overwrite
                        response = self._request_webdav(
                            "PUT", remote_file_path, data=file_data
                        )
                        if response.status_code == 201:
                            continue

                        raise HTTPError(
                            f"Failed to overwrite {local_file_path}: {response.status_code} - {response.text}",
                            response=response,
                        )

                    raise HTTPError(
                        f"Failed to upload {local_file_path}: {response.status_code} - {response.text}",
                        response=response,
                    )
        except Exception:
            raise
