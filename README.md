# censorship-feed

Автоматическая выгрузка свежих issues, PR и комментариев из репозиториев о цензуре и средствах обхода в один JSON-файл. Файл читается без GitHub API, напрямую через `raw.githubusercontent.com`.

Зачем: в некоторых окружениях (песочницы, ограниченные прокси, сети с фильтрацией) `api.github.com` недоступен, а raw-файлы доступны. Выгрузку делает GitHub Action со встроенным токеном, так что лимиты API не мешают.

## Что отслеживается

| Репозиторий | Тема |
|---|---|
| [net4people/bbs](https://github.com/net4people/bbs) | форум об интернет-цензуре, отчёты по странам |
| [yggdrasil-network/yggdrasil-go](https://github.com/yggdrasil-network/yggdrasil-go) | Yggdrasil |
| [PurpleI2P/i2pd](https://github.com/PurpleI2P/i2pd) | I2P (C++) |
| [markqvist/Reticulum](https://github.com/markqvist/Reticulum) | Reticulum |
| [XTLS/Xray-core](https://github.com/XTLS/Xray-core) | VLESS / Reality / XHTTP |
| [amnezia-vpn/amnezia-client](https://github.com/amnezia-vpn/amnezia-client) | AmneziaVPN / AmneziaWG |
| [apernet/hysteria](https://github.com/apernet/hysteria) | Hysteria2 |

Список меняется в `REPOS` в [`scripts/dump.py`](scripts/dump.py).

## Как работает

- [`.github/workflows/dump.yml`](.github/workflows/dump.yml) запускается каждые 3 часа (или вручную: **Actions → dump-issues → Run workflow**).
- [`scripts/dump.py`](scripts/dump.py) собирает issues/PR и комментарии, обновлённые за последние **48 часов**, и записывает их в `data/latest.json`. Коммит создаётся только если данные изменились.

## Формат `data/latest.json`

```json
{
  "generated_at": "2026-10-13T06:17:00Z",
  "since": "2026-10-11T06:17:00Z",
  "repos": {
    "net4people/bbs": {
      "issues":   [{"number": 1, "title": "...", "is_pr": false, "state": "open",
                    "created_at": "...", "updated_at": "...", "user": "...",
                    "url": "https://github.com/...", "body": "..."}],
      "comments": [{"id": 123, "issue": 1, "issue_title": "...",
                    "created_at": "...", "user": "...",
                    "url": "https://github.com/...#issuecomment-123", "body": "..."}]
    }
  }
}
```

- `body` обрезается до 4000 символов.
- Если репозиторий получить не удалось, вместо `issues`/`comments` будет поле `error`.
- В окно попадают элементы по `updated_at`. Для отбора действительно новых фильтруйте по `created_at`.

## Использование

```bash
curl -s https://raw.githubusercontent.com/mrgluek/censorship-feed/main/data/latest.json \
  | jq '.repos["net4people/bbs"].comments[] | {created_at, issue_title, url}'
```

raw-файлы кэшируются CDN GitHub до ~5 минут.

## Примечания

- GitHub может отключить расписание в репозитории без активности 60 дней. Если выгрузка встала, включите workflow заново во вкладке Actions.
- Данные — публичный контент перечисленных репозиториев. Авторские права на тексты принадлежат их авторам.

## Лицензия

[MIT](LICENSE)
