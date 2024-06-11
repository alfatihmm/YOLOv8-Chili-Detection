from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from datetime import datetime

bot_token = '6905591584:AAHAKjWUvEX5tZ5XkPUIzUv12I0d6aAf4gA'  # Ganti dengan token bot Anda

gauth = GoogleAuth()
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'penyakitlombok-396692ec95bf.json', 
    scopes=['https://www.googleapis.com/auth/drive'])
drive = GoogleDrive(gauth)

gc = gspread.authorize(gauth.credentials)

# ID spreadsheet Google Sheets
spreadsheet_id = '15Ci-7AqYHvzznvsXP46c7bCnfPKGR0usUSs622aNL6Q'
sheet = gc.open_by_key(spreadsheet_id).sheet1

bot = telegram.Bot(token=bot_token)

def start(update, context):
    user = update.effective_user
    update.message.reply_text(f"Selamat datang, {user.first_name}! \nBot ini disediakan untuk mendapatkan laporan deteksi yang telah Anda lakukan.")
    
    # Menu Keyboard
    custom_keyboard = [['Menu']]
    reply_markup_keyboard = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    update.message.reply_text("Tekan tombol menu pada keyboard untuk menampilkan menu.", reply_markup=reply_markup_keyboard)

def show_inline_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Kirim Laporan Terbaru", callback_data='latest_pdf')],
        [InlineKeyboardButton("Pilih Tanggal", callback_data='choose_date')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Pilih menu dibawah ini:', reply_markup=reply_markup)

def handle_message(update, context):
    text = update.message.text

    if text == 'Menu':
        show_inline_menu(update, context)
    elif text.isdigit() and len(text) == 6:  # Pastikan input adalah 6 digit angka
        handle_date_input(update, context)
    else:
        update.message.reply_text("Mohon masukkan format tanggal yang benar (DDMMYY).")

def get_latest_pdf():
    values = sheet.get_all_values()
    if len(values) > 1:
        latest_pdf = None
        latest_date = None
        for entry in values[1:]:
            date = datetime.strptime(entry[1], "%Y-%m-%d")
            if date <= datetime.now() and (latest_date is None or date > latest_date):
                latest_date = date
                latest_pdf = entry[3]
        return latest_pdf
    return None

def choose_date(update, context):
    message_text = 'Masukkan tanggal (DDMMYY):\nContoh: 190424 untuk 19 April 2024'
    update.callback_query.message.reply_text(message_text)

def handle_date_input(update, context):
    date_input = update.message.text
    values = sheet.get_all_values()
    found_files = []
    for entry in values[1:]:
        date_sheet = datetime.strptime(entry[1], "%Y-%m-%d").strftime("%y%m%d")
        date_input_formatted = datetime.strptime(date_input, "%d%m%y").strftime("%y%m%d")
        if date_sheet == date_input_formatted:
            found_files.append(entry[0])  # Mengambil nama file dari kolom pertama

    if found_files:
        context.chat_data['found_files'] = found_files  # Simpan daftar file yang ditemukan di dalam chat data
        keyboard = [[InlineKeyboardButton(file_name, callback_data=str(index))] for index, file_name in enumerate(found_files)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Pilih file yang ingin Anda terima:', reply_markup=reply_markup)
    else:
        update.message.reply_text('Tidak ada PDF pada tanggal tersebut.')


def handle_pdf_selection(update, context):
    query = update.callback_query
    file_index = int(query.data)
    found_files = context.chat_data.get('found_files')
    if found_files:
        selected_file = found_files[file_index]
        # Dapatkan link file PDF dari Google Sheet
        values = sheet.get_all_values()
        pdf_link = None
        for entry in values[1:]:
            if entry[0] == selected_file:
                pdf_link = entry[3]
                break
        if pdf_link:
            # Kirim link file PDF yang dipilih ke pengguna
            update.callback_query.message.reply_text(f"Berikut adalah link untuk laporan yang anda pilih: \n\n{pdf_link}")
        else:
            update.callback_query.message.reply_text("Maaf, link untuk file yang dipilih tidak ditemukan.")
    query.answer()



def button(update, context):
    query = update.callback_query
    query.answer()
    
    if query.data == 'latest_pdf':
        latest_pdf = get_latest_pdf()
        if latest_pdf:
            update.callback_query.message.reply_text(f"Berikut adalah link untuk PDF Laporan terbaru:\n{latest_pdf}")
        else:
            query.message.reply_text('Tidak ada PDF Laporan terbaru.')
    
    elif query.data == 'choose_date':
        choose_date(update, context)

    # Tambahkan bagian ini untuk menangani pemilihan file PDF
    else:
        handle_pdf_selection(update, context)

def main():
    updater = Updater(token=bot_token, use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

