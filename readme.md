# CheckLink Telegram Bot

## Описание

CheckLink - это Telegram бот, который позволяет пользователям проверять наличие ссылок в базе данных, добавлять новые ссылки и удалять существующие. Бот использует SQLite для хранения данных и имеет функции управления доступом для добавления и удаления ссылок.

## Возможности

- **Проверка ссылки**: Отправьте ссылку боту, и он проверит, существует ли она в базе данных.
- **Добавление ссылки**: Используйте команду `/add <ссылка>` для добавления новой ссылки. Пользователи из whitelist могут добавлять ссылки.
- **Удаление ссылки**: Используйте команду `/remove <ссылка>` для удаления ссылки. Пользователи из whitelist могут удалять ссылки.
- **Получение ID**: Команда `/myid` отправит ваш Telegram ID.
- **Отмена операции**: В любой момент можно отменить добавление или удаление ссылки, отправив команду `/cancel`.

## Установка

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/kalininDanil17Y/apollo-telegram-checkbot.git
   cd apollo-telegram-checkbot
   ```
   
2. Создайте виртуальное окружение и активируйте его:
   ```commandline
   python -m venv .venv
   source .venv/bin/activate  # На Unix/Mac
   .venv\Scripts\activate     # На Windows
   ```
   
3. Установите зависимости:
   ```commandline
    pip install -r requirements.txt
    ```
4. Создайте файл конфигурации `config.json`:
   ```json
    {
      "TOKEN": "ваш_токен_бота",
      "WHITELIST": ["список_id_пользователей_с_правами"]
    }
   ```
   
5. Создайте базу данных:
   `При первом запуске бот автоматически создаст необходимую таблицу в базе данных SQLite.`

## Запуск
Для запуска бота выполните команду:
   ```commandline
   python main.py
   ```
## Использование
- Отправьте ссылку боту, чтобы проверить её наличие в базе данных.
- Используйте команду `/add <ссылка>`, чтобы добавить ссылку (только для пользователей из whitelist).
- Используйте команду `/remove <ссылка>`, чтобы удалить ссылку (только для пользователей из whitelist).
- Используйте команду `/myid`, чтобы получить ваш Telegram ID.
- Используйте команду `/cancel`, чтобы отменить текущую операцию.