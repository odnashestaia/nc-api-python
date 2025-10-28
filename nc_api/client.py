from nc_api.base_manager import BaseManager
from nc_api.directory_manager import DirectoryManager
from nc_api.file_manager import FileManager
from nc_api.path_manager import PathManager
from nc_api.user_manager import UserManager


class NextcloudClient(BaseManager):
    """Aggregates all managers into a single entry point."""

    def __init__(self, NEXTCLOUD_URL: str, USERNAME: str, PASSWORD: str) -> None:
        super().__init__(NEXTCLOUD_URL, USERNAME, PASSWORD)
        self.dirs = DirectoryManager(NEXTCLOUD_URL, USERNAME, PASSWORD)
        self.files = FileManager(
            NEXTCLOUD_URL, USERNAME, PASSWORD, directory_manager=self.dirs
        )
        self.paths = PathManager(
            NEXTCLOUD_URL,
            USERNAME,
            PASSWORD,
            directory_manager=self.dirs,
            file_manager=self.files,
        )
        self.users = UserManager(NEXTCLOUD_URL, USERNAME, PASSWORD)
