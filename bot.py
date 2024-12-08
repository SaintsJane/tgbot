import pandas as pd
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import schedule
import time
import threading

# Установите уровень логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Хранилище для пользователей
user_ids = {}
added_count = 0

# Функция для аутентификации в Google Sheets
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('path/to/credentials.json', scope)
    client = gspread.authorize(creds)
    return client

# Функция для отправки уведомлений
def send_notification(user_id, account_number, amount, due_date):
    message = f'Оплата хостинга {account_number} на сумму {amount}. Хостинг отключится {due_date}.'
    context.bot.send_message(chat_id=user_id, text=message)

# Функция для планирования уведомлений
def schedule_notifications(context):
    for phone, user_id in user_ids.items():
        # Логика получения информации о сроках оплаты
        account_number = "12345"  # Заглушка
        amount = "1000"            # Заглушка
        due_date = "2023-12-31"    # Заглушка
        send_notification(user_id, account_number, amount, due_date)

# Функция для запуска планировщика в отдельном потоке
def run_scheduler():
    schedule.every(1).day.at("10:00").do(schedule_notifications)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Функция старта
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот для уведомлений о сроках оплаты хостинга.')

# Функция для загрузки данных
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        return "Файл не найден."
    except Exception as e:
        return f"Произошла ошибка: {e}"

# Функция для добавления пользователей
def add_users(update: Update, context: CallbackContext) -> None:
    global added_count
    if added_count >= 200:
        update.message.reply_text('Достигнут лимит добавлений пользователей (200 в сутки).')
        return

    file_path = context.args[0] if context.args else None
    if file_path:
        df = load_data(file_path)
        for index, row in df.iterrows():
            phone_number = row['phone']
            user_id = row['user_id']  # Предполагается, что ID пользователя хранится в таблице
            user_ids[phone_number] = user_id
            added_count += 1
            update.message.reply_text(f'Пользователь {phone_number} добавлен.')
    else:
        update.message.reply_text('Не указан файл для загрузки.')

# Основная функция
def main():
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add_users", add_users, pass_args=True))
    
    # Запуск планировщика в отдельном потоке
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
