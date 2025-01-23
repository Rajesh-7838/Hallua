import os
import asyncio
from telethon import TelegramClient, events

# Replace these with your own values
API_ID = '28234107'
API_HASH = '2f54dbcf4783b0d161654a4e1d48370e'
BOT_TOKEN = '7792807152:AAGIIuWmUTaci_giatgZfQBMvs8ErHd91Cg'
OWNER_ID = 7638980494  # Use integer ID
APPROVED_USERS = {7638980494}  # Use integer IDs

# Group usernames for approved users
GROUPS = {
    7638980494: 'private_check2',  # Group username for OWNER_ID
}

# Initialize the last group number used
last_group_number = len(GROUPS)  # This will be 6 based on the current GROUPS

# Telegram API credentials for module_2
phone_number = '+917990678233'  # Your phone number with country code
bot_username = '@FroxtCheck_bot'  # Username of the bot to wait for replies
MESSAGE_DELAY = 2  # seconds (set to 2 seconds)
REPLY_WAIT_TIME = 5  # seconds
APPROVED_TEXT = "Approved"  # Text to check for in the reply

# Transformation map for the reply text
transformation_map = {
    'Card': '𝗖𝗮𝗿𝗱',
    '𝐆𝐚𝐭𝐞𝐰𝐚𝐲': '𝗚𝗮𝘁𝗲𝘄𝗮𝘆',
    '𝐒𝐭𝐚𝐭𝐮𝐬': '𝗦𝘁𝗮𝘁𝘂𝘀',
    '𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞': '𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲',
    '𝐓𝐢𝐦𝐞': '𝗧𝗶𝗺𝗲',
    'Stripe': '𝖲𝗍𝗋𝗂𝗉𝖾',
    'Declined': '𝖣𝖾𝖼𝗅𝗂𝗇𝖾𝖽',
    'Your card was declined.': '𝖸𝗈𝗎𝗋 𝖢𝖺𝗋𝖽 𝗐𝖺𝗌 𝖽𝖾𝖼𝗅𝗂𝗇𝖾𝖽.',
    'Declined ❌': '𝖣𝖾𝖼𝗅𝗂𝗇𝖾𝖽 ❌',
    'Approved ✅': '𝖠𝗉𝗉𝗋𝗈𝗏𝖾𝖽 ✅',
    'Payment Successful': '𝖯𝖺𝗒𝗆𝖾𝗇𝗍 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅'
}

# Initialize the Telegram client for the logged-in user
user_client = TelegramClient('user_session', API_ID, API_HASH)

# Initialize the Telegram client for the bot
bot_client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Dictionary to track processing status for each user
processing_status = {}

# Dictionary to track the current task for each user
current_task = {}

@bot_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Welcome! Send your combo File (Filtered Format- CC|MM|YY|YY) 𝗗𝗲𝘃 - @Spixom_xd")

@bot_client.on(events.NewMessage(pattern='/approve (\\d+)'))
async def approve_user(event):
    if event.sender_id != OWNER_ID:
        await event.respond("You are not authorized to approve users.")
        return

    # Extract the user ID from the command
    user_id = int(event.pattern_match.group(1))

    # Check if the user is already approved
    if user_id in APPROVED_USERS:
        await event.respond(f"User {user_id} is already approved.")
        return

    # Add the user to the approved users
    APPROVED_USERS.add(user_id)

    # Increment the last group number and assign the user to a group
    global last_group_number
    last_group_number += 1  # Increment the last group number
    group_username = f'private_check{last_group_number}'  # Create a new group username
    GROUPS[user_id] = group_username

    # Send the authorization message to the approved user
    await bot_client.send_message(user_id, "Bot Has Been Reset and you are now Authorized to use me. Send your Combo File now.")

    await event.respond(f"User {user_id} has been approved and assigned to group {group_username}.")

@bot_client.on(events.NewMessage(pattern='/disapprove (\\d+)'))
async def disapprove_user(event):
    if event.sender_id != OWNER_ID:
        await event.respond("You are not authorized to disapprove users.")
        return

    # Extract the user ID from the command
    user_id = int(event.pattern_match.group(1))

    # Check if the user is approved
    if user_id not in APPROVED_USERS:
        await event.respond(f"User {user_id} is not approved.")
        return

    # Check if there is an ongoing task for the user
    if user_id in current_task and current_task[user_id]:
        current_task[user_id].cancel()  # Cancel the ongoing task
        await bot_client.send_message(user_id, "Your Plan has been expired. Renew Now @Spixom_xd")  # Notify the user

    # Remove the user from the approved users
    APPROVED_USERS.remove(user_id)

    # Remove the user from the GROUPS dictionary
    if user_id in GROUPS:
        del GROUPS[user_id]

    await event.respond(f"User {user_id} has been disapproved and removed from the group.")

@bot_client.on(events.NewMessage())
async def handle_file(event):
    if event.message.file:
        user_id = event.sender_id

        # Check if user is approved
        if user_id not in APPROVED_USERS:
            await event.respond("You are not authorized to use this bot. Contact @Spixom_xd")
            return

        # Check if the user is already processing a file
        if user_id in processing_status and processing_status[user_id]:
            await event.respond("Currently Checking 💫\nType /stop to stop Checking then send another file.")
            return  # Stop processing the new file

        # Notify the user that processing is starting
        await event.respond("Processing, wait for hits.. 🔍")
        processing_status[user_id] = True  # Mark as processing

        # Save the file with unique naming
        file_name = get_unique_file_name()
        await bot_client.download_media(event.message, file_name)

        # Process the file
        current_task[user_id] = asyncio.create_task(process_file(file_name, user_id))

async def process_file(file_name, user_id):
    with open(file_name, 'r') as f:
        cards = f.readlines()

    # Convert the year from YYYY to YY and prepare the cards for sending
    formatted_cards = []
    for card in cards:
        parts = card.strip().split('|')
        if len(parts) == 4:  # Ensure the format is CC|MM|YYYY|CVV
            cc, mm, yyyy, cvv = parts
            yy = yyyy[-2:]  # Get the last two digits of the year
            formatted_cards.append(f"{cc}|{mm}|{yy}|{cvv}")  # Convert to CC|MM|YY|CVV

    # Process cards in batches of 5
    for i in range(0, len(formatted_cards), 5):
        batch = formatted_cards[i:i + 5]  # Get the next 5 cards
        await send_card_info(batch, user_id)

    # Mark processing as complete
    processing_status[user_id] = False
    del current_task[user_id]  # Remove the task from the current task dictionary

@bot_client.on(events.NewMessage(pattern='/stop'))
async def stop_checking(event):
    user_id = event.sender_id

    # Check if user is approved
    if user_id not in APPROVED_USERS:
        await event.respond("You are not authorized to use this bot. Contact @Spixom_xd")
        return

    # Check if there is an ongoing task
    if user_id in current_task and current_task[user_id]:
        current_task[user_id].cancel()  # Cancel the ongoing task
        await event.respond("Checking has been stopped. You can now send another file.")
        processing_status[user_id] = False  # Mark processing as complete
        del current_task[user_id]  # Remove the task from the current task dictionary
    else:
        await event.respond("There is no ongoing checking process to stop.")

def get_unique_file_name():
    # Generate a unique file name based on existing files
    base_name = "Cards"
    index = 0
    while os.path.exists(f"{base_name}{index}.txt"):
        index += 1
    return f"{base_name}{index}.txt"

async def send_card_info(card_batch, user_id):
    # Get the group username for the user
    group_username = GROUPS.get(user_id)
    if group_username is None:
        return  # If no group is found, exit

    for card_info in card_batch:
        command = f"/stq {card_info.strip()}"
        try:
            await user_client.send_message(group_username, command)
            print(f"Sent: {command}")

            # Wait for a reply from the bot
            await asyncio.sleep(REPLY_WAIT_TIME)  # Wait for the bot to respond

            # Get the last message from the bot
            async for message in user_client.iter_messages(group_username, limit=5):
                if message.sender_id and message.sender_id == (await user_client.get_entity(bot_username)).id:
                    reply_text = message.text
                    print(f"Received reply: {reply_text}")

                    # Check for specific keywords in the reply
                    if "Your card was declined." in reply_text:
                        # Format the response for declined cards
                        formatted_reply = f"{card_info.strip()}\n𝗦𝘁𝗮𝘁𝘂𝘀: 𝖣𝖾𝖼𝗅𝗂𝗇𝖾𝖽\n𝗥𝗲𝗽𝗹𝘆: 𝖸𝗈𝗎𝗋 𝖢𝖺𝗋𝖽 𝗐𝖺𝗌 𝖽𝖾𝖼𝗅𝗂𝗇𝖾𝖽."
                        await bot_client.send_message(user_id, formatted_reply)  # Send to the approved user
                        break  # Stop processing further cards in this batch
                    elif "expiration" in reply_text:
                        # Format the response for expired cards
                        formatted_reply = f"{card_info.strip()}\n𝗦𝘁𝗮𝘁𝘂𝘀: 𝖣𝖾𝖼𝗅𝗂𝗇𝖾𝖽\n𝗥𝗲𝗽𝗹𝗲: Error creating payment method: Your card's expiration year is invalid."
                        await bot_client.send_message(user_id, formatted_reply)  # Send to the approved user
                        break  # Stop processing further cards in this batch
                    elif "Approved" in reply_text:
                        # For other replies, check if it contains "Approved ✅"
                        transformed_reply = await transform_reply(reply_text)
                        print(f"Transformed reply: {transformed_reply}")

                        # Send the reply to the user and the owner
                        await bot_client.send_message(user_id, transformed_reply)  # Send to the approved user
                        await bot_client.send_message(OWNER_ID, transformed_reply)  # Send to the owner
                        break  # Stop processing further cards in this batch
                    else:
                        # If none of the keywords are present, notify the user
                        formatted_reply = "Your File is not filtered correctly.\nPlease Filter it properly."
                        await bot_client.send_message(user_id, formatted_reply)  # Send to the approved user
                        break  # Stop processing further cards in this batch

            await asyncio.sleep(MESSAGE_DELAY)  # Delay before sending the next command
        except Exception as e:
            print(f"Error: {e}")

async def transform_reply(reply_text):
    """Transform the reply text to the desired format."""
    for original, transformed in transformation_map.items():
        reply_text = reply_text.replace(original, transformed)

    return reply_text + "\n𝗗𝗲𝘃 - @Spixom_xd" if APPROVED_TEXT in reply_text else reply_text

# Start both clients
async def main():
    await user_client.start()
    await bot_client.start()
    await asyncio.gather(user_client.run_until_disconnected(), bot_client.run_until_disconnected())

# Check if an event loop is already running
try:
    asyncio.get_event_loop().run_until_complete(main())
except RuntimeError as e:
    if 'This event loop is already running' in str(e):
        print("Event loop is already running. Please run this script in a different environment.")
    else:
        raise e