import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
import sqlite3
from urllib.parse import urlparse, urlunparse

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Загрузка конфигурации
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
TOKEN = config['TOKEN']
WHITELIST = set(config['WHITELIST'])

# Файл базы данных
DATABASE_FILE = 'links.db'

# Словарь для хранения состояния пользователей
user_state = {}

def create_table():
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def normalize_url(url):
    """Нормализует URL для сравнения."""
    parsed = urlparse(url)
    scheme = parsed.scheme if parsed.scheme else 'http'
    netloc = parsed.netloc or parsed.path
    path = parsed.path.rstrip('/')
    normalized_url = urlunparse((scheme, netloc, path, '', '', ''))
    return normalized_url

def add_link_to_db(url):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    normalized_url = normalize_url(url)
    try:
        c.execute('INSERT INTO links (url) VALUES (?)', (normalized_url,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Ссылка уже существует
    conn.close()

def remove_link_from_db(url):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    normalized_url = normalize_url(url)
    c.execute('DELETE FROM links WHERE url = ?', (normalized_url,))
    conn.commit()
    conn.close()

def link_exists(url):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    normalized_url = normalize_url(url)
    c.execute('SELECT COUNT(*) FROM links WHERE url = ?', (normalized_url,))
    exists = c.fetchone()[0] > 0
    conn.close()
    return exists

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Привет! Отправьте мне ссылку для проверки или используйте команду /add <ссылка> для добавления.')

async def handle_message(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    if user_id in user_state and user_state[user_id] == 'waiting_for_url_add':
        url = update.message.text

        if update.message.text.lower() in ['отмена', 'cancel', '/отмена', '/cancel']:
            user_state.pop(user_id, None)
            await update.message.reply_text('Отменено')
            return

        if not link_exists(url):
            add_link_to_db(url)
            await update.message.reply_text(f'Ссылка добавлена: {url}')
        else:
            await update.message.reply_text('Ссылка уже существует.')
        user_state.pop(user_id, None)

    elif user_id in user_state and user_state[user_id] == 'waiting_for_url_remove':

        url = update.message.text

        if update.message.text.lower() in ['отмена', 'cancel', '/отмена', '/cancel']:
            user_state.pop(user_id, None)
            await update.message.reply_text('Отменено')
            return

        if link_exists(url):
            remove_link_from_db(url)
            await update.message.reply_text(f'Ссылка удалена: {url}')
        else:
            await update.message.reply_text('Ссылка не найдена.')
        user_state.pop(user_id, None)

    else:
        url = update.message.text
        if link_exists(url):
            await update.message.reply_text(f'Ссылка найдена: {url}')
        else:
            await update.message.reply_text('Ссылка не найдена. Используйте команду /add для добавления.')

async def add_link(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    if user_id not in WHITELIST:
        await update.message.reply_text('У вас нет прав для добавления ссылок.')
        return

    if context.args:
        url = ' '.join(context.args)
        if not link_exists(url):
            add_link_to_db(url)
            await update.message.reply_text(f'Ссылка добавлена: {url}')
        else:
            await update.message.reply_text('Ссылка уже существует.')
    else:
        user_state[user_id] = 'waiting_for_url_add'
        await update.message.reply_text('Пожалуйста, отправьте ссылку, которую хотите добавить.')

async def remove_link(update: Update, context: CallbackContext):
    user_id = str(update.message.from_user.id)
    if user_id not in WHITELIST:
        await update.message.reply_text('У вас нет прав для удаления ссылок.')
        return

    if context.args:
        url = ' '.join(context.args)
        if link_exists(url):
            remove_link_from_db(url)
            await update.message.reply_text(f'Ссылка удалена: {url}')
        else:
            await update.message.reply_text('Ссылка не найдена.')
    else:
        user_state[user_id] = 'waiting_for_url_remove'
        await update.message.reply_text('Пожалуйста, отправьте ссылку, которую хотите удалить.')

async def send_id(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    message = f"Ваш ID: <code>{user_id}</code>"
    await update.message.reply_text(message, parse_mode='HTML')

def main():
    create_table()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('add', add_link))
    application.add_handler(CommandHandler('remove', remove_link))
    application.add_handler(CommandHandler('myid', send_id))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
