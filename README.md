## Описание проекта

`nc_api` — простая библиотека для работы с Nextcloud через WebDAV и OCS API: файлы, директории, операции над путями и пользователи. Единая точка входа — `NextcloudClient`.

## Инициализация проекта

### Установка

```bash
cd /home/odna/python/nc-api-python
/usr/bin/python setup.py sdist bdist_wheel
pip install -U dist/nc_api-0.1.0-py3-none-any.whl
```

### Базовая инициализация клиента

```python
from nc_api import NextcloudClient

# Базовый URL должен указывать на WebDAV-директорию пользователя
BASE = "http://localhost:8088/remote.php/dav/files/admin"
client = NextcloudClient(BASE, "admin", "admin")
```

## Функционал модулей

### DirectoryManager
- **directory_exists_check(path: str) -> bool | str**: проверка существования директории через WebDAV PROPFIND.

### FileManager
- **upload_file(LOCAL_UPLOAD_PATH | FILE, REMOTE_UPLOAD_PATH) -> bool**: загрузка файла; при необходимости создаёт каталоги (при наличии `directory_manager`).
- **download_file(LOCAL_DOWNLOAD_PATH, REMOTE_DOWNLOAD_PATH) -> bool**: скачивание файла.
- **get_data_file(REMOTE_FILE_PATH) -> dict | str**: метаданные файла через WebDAV PROPFIND (XML).

### PathManager
- **rename_path(CURRENT_PATH, NEW_PATH) -> bool**: переименование/перемещение ресурса (MOVE); создаёт недостающие каталоги.
- **delete_path(TARGET_PATH) -> bool**: удаление файла/директории (DELETE).
- **UploadFolder(LOCAL_FOLDER_PATH, REMOTE_FOLDER_PATH) -> None**: рекурсивная загрузка каталога.

### UserManager (OCS API)
- **get_users(search=None, limit=None, offset=None) -> list[str] | str**: список пользователей.
- **get_user(username=None, user_id=None, name=None) -> dict | str**: данные пользователя.

## Использование через единую точку входа

```python
from nc_api import NextcloudClient

BASE = "http://localhost:8088/remote.php/dav/files/admin"
client = NextcloudClient(BASE, "admin", "admin")

# Файлы
client.files.upload_file(FILE=b"hello", REMOTE_UPLOAD_PATH="/tmp/hello.txt")
client.files.download_file("./hello.txt", "/tmp/hello.txt")

# Пути
client.paths.rename_path("/tmp/hello.txt", "/tmp/hi.txt")
client.paths.delete_path("/tmp/hi.txt")

# Директории
client.dirs.directory_exists_check("/tmp")

# Пользователи (OCS)
client.users.get_users(limit=10)
client.users.get_user(username="admin")
```

Примечание: `BASE` должен указывать на корень WebDAV для конкретного пользователя: `http(s)://<host>/remote.php/dav/files/<username>`.


