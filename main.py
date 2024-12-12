import telebot
from telebot import types
import qrcode
import base64
import os
import random
import string
import uuid
import requests
from PIL import Image

API_KEY = os.environ.get('API_KEY', "")
bot = telebot.TeleBot(API_KEY)

# Base URL for the Lanzou Cloud API
API_BASE_URL = "https://v2.xxapi.cn/api/lanzou?url="

# Define the main keyboard
keyboard = types.ReplyKeyboardMarkup(row_width=4, resize_keyboard=True)
# Add buttons to the keyboard
button1 = types.KeyboardButton('Text to QR Code')
button2 = types.KeyboardButton('Base64 Encode')
button3 = types.KeyboardButton('Base64 Decode')
button4 = types.KeyboardButton('Random Password Generator')
button5 = types.KeyboardButton('UUID Generator')
button6 = types.KeyboardButton('Bing Daily Wallpaper')
button7 = types.KeyboardButton('Image to ICO Icon')
button8 = types.KeyboardButton('Diary of a Licker')
button9 = types.KeyboardButton('Netease Cloud Hot Comments')
button10 = types.KeyboardButton('Lanzou Cloud Parser')
button11 = types.KeyboardButton('Hitokoto')
button12 = types.KeyboardButton('Close Keyboard')

keyboard.add(button1, button2, button3, button4, button5, button6, button7, button8, button9, button10, button11, button12)

# /start command handler
@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_message = (
        "Welcome to the Toolbox Bot! 🎈\n\n"
        "Send /start to start the program\n"
        "Send /menu to open the keyboard\n"
        "Send /close to close the keyboard\n"
        "Send /help to get the commands"
    )
    bot.send_message(message.chat.id, welcome_message, reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_message = (
        "/start - Start the program\n"
        "/menu - Open the keyboard\n"
        "/close - Close the keyboard\n"
        "/help - Get the commands"
    )
    bot.send_message(message.chat.id, help_message, reply_markup=keyboard)

# Text message handler
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == '/menu':
        bot.send_message(message.chat.id, "Keyboard enabled", reply_markup=keyboard)
    elif message.text == 'Close Keyboard' or message.text == '/close':
        bot.send_message(message.chat.id, "Keyboard closed", reply_markup=types.ReplyKeyboardRemove())
    elif message.text == 'Text to QR Code':
        bot.send_message(message.chat.id, "Please reply with the text you want to convert into a QR Code:")
        bot.register_next_step_handler(message, generate_qrcode)
    elif message.text == 'Base64 Encode':
        bot.send_message(message.chat.id, "Please reply with the text you want to Base64 encode:")
        bot.register_next_step_handler(message, encode_base64)
    elif message.text == 'Base64 Decode':
        bot.send_message(message.chat.id, "Please reply with the Base64 encoded text to decode:")
        bot.register_next_step_handler(message, decode_base64)
    elif message.text == 'Random Password Generator':
        bot.send_message(message.chat.id, generate_random_password())
    elif message.text == 'UUID Generator':
        bot.send_message(message.chat.id, generate_uuid())
    elif message.text == 'Bing Daily Wallpaper':
        download_bing_wallpaper(message.chat.id)
    elif message.text == 'Image to ICO Icon':
        bot.send_message(message.chat.id, "Please reply with a JPG or PNG image file:")
        bot.register_next_step_handler(message, convert_to_ico)
    elif message.text == 'Diary of a Licker':
        send_request_data(message.chat.id, 'https://cloud.qqshabi.cn/api/tiangou/api.php')
    elif message.text == 'Netease Cloud Hot Comments':
        send_request_data(message.chat.id, 'https://cloud.qqshabi.cn/api/comments/api.php?format=text')
    elif message.text == 'Hitokoto':
        send_request_data(message.chat.id, 'https://cloud.qqshabi.cn/api/hitokoto/hitokoto.php')
    elif message.text == 'Lanzou Cloud Parser':
        bot.send_message(message.chat.id, "Please send the Lanzou Cloud link to parse:")
        bot.register_next_step_handler(message, handle_lanzou_url)

# Lanzou Cloud parsing handler
def handle_lanzou_url(message):
    user_url = message.text.strip()
    api_url = API_BASE_URL + user_url

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if data.get("code") == 200 and "data" in data:
            download_url = data["data"]
            bot.send_message(message.chat.id, f"Parsing successful! Download link:\n{download_url}")
        else:
            bot.send_message(message.chat.id, "Parsing failed. No download link found in the response.")
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, f"An error occurred during the request: {e}")

# Utility functions
def generate_qrcode(message):
    text = message.text
    img = qrcode.make(text)
    img.save('qrcode.png')
    with open('qrcode.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    os.remove('qrcode.png')

def encode_base64(message):
    text_bytes = message.text.encode('utf-8')
    base64_text = base64.b64encode(text_bytes).decode('ascii')
    bot.send_message(message.chat.id, base64_text)

def decode_base64(message):
    try:
        decoded_text = base64.b64decode(message.text).decode('utf-8')
        bot.send_message(message.chat.id, decoded_text)
    except Exception:
        bot.send_message(message.chat.id, "Decoding failed. Please ensure the input is valid Base64 encoded text.")

def generate_random_password():
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(12))

def generate_uuid():
    return str(uuid.uuid4())

def download_bing_wallpaper(chat_id):
    url = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US'
    try:
        response = requests.get(url)
        wallpaper_path = response.json()['images'][0]['url']
        wallpaper_url = 'https://www.bing.com' + wallpaper_path
        wallpaper_response = requests.get(wallpaper_url)

        with open('bing_wallpaper.jpg', 'wb') as f:
            f.write(wallpaper_response.content)

        with open('bing_wallpaper.jpg', 'rb') as photo:
            bot.send_photo(chat_id, photo)
        os.remove('bing_wallpaper.jpg')
    except Exception as e:
        bot.send_message(chat_id, "An error occurred while downloading the wallpaper.")

def convert_to_ico(message):
    try:
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
            file = requests.get(f'https://api.telegram.org/file/bot{API_KEY}/{file_info.file_path}')
            with open('temp_image.png', 'wb') as f:
                f.write(file.content)

            img = Image.open('temp_image.png')
            img.save('icon.ico', format='ICO')

            with open('icon.ico', 'rb') as f:
                bot.send_document(message.chat.id, f)
            os.remove('temp_image.png')
            os.remove('icon.ico')
        else:
            bot.send_message(message.chat.id, "Please send an image file.")
    except Exception:
        bot.send_message(message.chat.id, "An error occurred while processing the image.")

def send_request_data(chat_id, url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            bot.send_message(chat_id, response.text)
        else:
            bot.send_message(chat_id, "Failed to fetch data. Please try again later.")
    except Exception:
        bot.send_message(chat_id, "An error occurred during the request.")

# Start the bot
bot.polling()
