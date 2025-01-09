import discord
from discord.ext import commands
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from google.colab import userdata
import logging
import nest_asyncio
nest_asyncio.apply()
import asyncio
import requests
import hashlib
import time

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
intents.voice_states = False

token = os.getenv('DISCORD_TOKEN')
if token is None:
    logging.error("TOKEN environment variable is not set")
    print("TOKEN environment variable is not set")
    exit(1)

secret = 'tB87#kPtkxqOS2'

bot = commands.Bot(command_prefix='!', intents=intents)

def log_and_print_error(message: str, error: Exception):
    logging.error(f"{message}: {str(error)}")
    print(f"{message}: {str(error)}")

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    logging.info(f"{bot.user} has connected to Discord!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.isdigit():
        id = int(message.content)
        print(f"Received ID {id} from {message.author}")
        logging.info(f"Received ID {id} from {message.author}")

        try:
            # Add reaction to the message
            await message.add_reaction("🍊")  # :tangerine:
            print("Added :tangerine: reaction to the message.")
        except discord.Forbidden:
            print("Failed to add :tangerine: reaction to the message. Missing permissions.")
            await message.channel.send("I don't have the required permissions to add reactions to this message.")

        try:
            url = 'https://wos-giftcode-api.centurygame.com/api/player'
            print(f"Sending POST request to {url}...")

            timestamp = int(time.time())
            form_data = f'fid={id}&time={timestamp}'
            signature = hashlib.md5((form_data + secret).encode()).hexdigest()
            form_data = f'sign={signature}&{form_data}'

            response = requests.post(
                url,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data=form_data
            )

            print(f"Received API response with status code {response.status_code}")

            if response.status_code == 200:
                print("Parsing API response as JSON...")
                data = response.json()

                print("Logging API response for debugging purposes...")
                logging.info(f"API response: {data}")

                print("API Response:")
                print(data)

                if 'data' in data and 'nickname' in data['data'] and 'kid' in data['data']:
                    print("Extracting nickname and server number from API response...")
                    nickname = data['data']['nickname']
                    server_number = data['data']['kid']

                    print("Changing user's nickname to retrieved nickname with server number...")
                    await message.author.edit(nick=f"[{server_number}] {nickname}")

                    print("Sending confirmation message to user...")
                    await message.channel.send(f"Nickname changed to [{server_number}] {nickname}")
                    print("Nickname changed successfully.")
                else:
                    print("Nickname or server number not found in API response.")
                    await message.channel.send("Failed to retrieve nickname or server number. Please try again by just typing in your user ID found in game, or contact the admin.")
                    log_and_print_error("Failed to retrieve nickname or server number", None)
                    print("Failed to change nickname.")
            else:
                print(f"API request failed with status code {response.status_code}")
                await message.channel.send(f"API request failed. Please try again by just typing in your user ID found in game, or contact the admin.")
                log_and_print_error(f"API request failed with status code {response.status_code}", None)
                print("API request failed.")
        except requests.exceptions.RequestException as e:
            log_and_print_error("Request error", e)
            await message.channel.send("Request error. Please try again by just typing in your user ID found in game, or contact the admin.")
            print("Request error occurred.")
        except Exception as e:
            log_and_print_error("An error occurred", e)
            await message.channel.send("An error occurred. Please try again by just typing in your user ID found in game, or contact the admin.")
            print("An error occurred.")

    await bot.process_commands(message)


async def main():
    try:
        print("Starting bot...")
        await bot.start(token)
    except KeyboardInterrupt:
        print("Stopping bot...")
        await bot.close()
        print("Bot stopped manually.")
    except Exception as e:
        log_and_print_error("An error occurred", e)

try:
    asyncio.run(main())
except Exception as e:
    log_and_print_error("An error occurred", e)
