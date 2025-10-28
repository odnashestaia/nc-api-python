# Тестирование nc_api

## Интеграционные тесты

- Требуется Docker/Compose.
- По умолчанию поднимается `nextcloud:31-apache` на `http://localhost:8088` с admin/admin.
- Переменные окружения (опционально):
  - `NC_URL` (по умолчанию `http://localhost:8088`)
  - `NC_USER` (по умолчанию `admin`)
  - `NC_PASS` (по умолчанию `admin`)
- Запуск: `pytest -q tests/integration`
  - Контейнер будет поднят автоматически перед тестами и остановлен после.

### Запуск интеграционных тестов с Docker Compose и ngrok

1) Запустите Nextcloud через Docker Compose

```bash
docker compose -f tests/docker-compose.yaml up -d
```

2) Пробросьте локальный сервис наружу через ngrok

```bash
# Требуется установленный ngrok и авторизация в ngrok
ngrok http 8088
```

Скопируйте выданный публичный адрес вида `https://<id>.ngrok-free.app`.

3) Укажите внешний URL в `tests/conftest.py`

Откройте `tests/conftest.py` и в фикстуре `nc_url` замените значение URL на ваш публичный адрес из ngrok, например:

```python
@pytest.fixture(scope="session")
def nc_url() -> str:
    return os.environ.get("NC_URL", "https://<id>.ngrok-free.app")
```

4) Зайдите в Nextcloud под admin/admin

- Откройте в браузере внешний адрес из ngrok и авторизуйтесь: login `admin`, password `admin`.

5) Запустите тесты

```bash
env PYTHONPATH=$(pwd) python -m pytest -q tests
```

При необходимости можно запускать конкретные файлы, например:

```bash
env PYTHONPATH=$(pwd) python -m pytest -q tests/test_path_manager_integration.py
```

6) Остановка окружения

```bash
docker compose -f tests/docker-compose.yaml down -v
```
