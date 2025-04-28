from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import re
import os
from telegram import Bot, Update
import logging

# Logging Setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("8051152860:AAGGpwCik-DLCgwGkMKLGe7nNSVC7K8uD7o")

# Warning Counter
user_warnings = {}

# Old Username Store
old_usernames = {}

# New Member Handler
def welcome(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        old_usernames[member.id] = member.full_name
        keyboard = [
            [InlineKeyboardButton("🔔 Subscribe YouTube", url="https://youtube.com/@alfazinfosec")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            f"👋 Welcome {member.full_name}!\n🆔 YOUR ID: `{member.id}`",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

# Detect Username Change
def detect_username_change(update: Update, context: CallbackContext):
    user = update.message.from_user
    if user.id in old_usernames and old_usernames[user.id] != user.full_name:
        update.message.reply_text(
            f"✍️ User Name Changed!\nOLD NAME: {old_usernames[user.id]}\nYOUR NAME: {user.full_name}\n Remember everyone.।"
        )
        old_usernames[user.id] = user.full_name

# Remove Links and Warn
def remove_links(update: Update, context: CallbackContext):
    if re.search(r'http[s]?://', update.message.text):
        try:
            update.message.delete()
            update.message.reply_text(f"⚠️ @{update.message.from_user.username or update.message.from_user.first_name}, Sending links is prohibited! Be careful. @alfazinfosec")
            warn_user(update, context)
        except:
            pass

# Remove Bad Words and Warn
def bad_words_filter(update: Update, context: CallbackContext):
    bad_words = ['fuck', 'shit', 'bitch', 'sex', 'dick']
    text = update.message.text.lower()
    if any(word in text for word in bad_words):
        try:
            update.message.delete()
            update.message.reply_text(f"⚠️ @{update.message.from_user.username or update.message.from_user.first_name}, Bad language is prohibited!")
            warn_user(update, context)
        except:
            pass

# Group Link Ban
def group_link_ban(update: Update, context: CallbackContext):
    if re.search(r'(t\.me\/|telegram\.me\/)', update.message.text):
        try:
            update.message.delete()
            context.bot.kick_chat_member(chat_id=update.message.chat_id, user_id=update.message.from_user.id)
            update.message.reply_text("🚫 Telegram group banned for link sharing! @alfazinfosec")
        except:
            pass

# Warn User Function (for both remove_links and bad_words_filter)
def warn_user(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    user_warnings[user_id] = user_warnings.get(user_id, 0) + 1

    warnings = user_warnings[user_id]
    if warnings >= 3:
        try:
            context.bot.kick_chat_member(chat_id=chat_id, user_id=user_id)
            update.message.reply_text(f"🚫 @{update.message.from_user.username or update.message.from_user.first_name} Banned for 3 warnings!")
        except:
            pass
    else:
        update.message.reply_text(f"⚠️ Warning {warnings}/3 @{update.message.from_user.username or update.message.from_user.first_name}")

# Manual Warn Command
def warn(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /warn @username")
        return
    
    username = context.args[0].lstrip('@')
    chat = update.effective_chat

    for member in chat.get_members():
        if member.user.username == username:
            user_id = member.user.id
            user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
            warnings = user_warnings[user_id]

            update.message.reply_text(f"⚠️ @{username} Who was given a warning! Total Warning: {warnings}/3")

            if warnings >= 3:
                try:
                    context.bot.kick_chat_member(chat.id, user_id)
                    update.message.reply_text(f"🚫 @{username} has been banned!")
                except:
                    pass
            return

# Mute Command
def mute(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /mute @username")
        return

    username = context.args[0].lstrip('@')
    chat = update.effective_chat

    members = chat.get_administrators() + chat.get_members()

    for member in members:
        if member.user.username == username:
            user_id = member.user.id
            permissions = ChatPermissions(can_send_messages=False)
            try:
                context.bot.restrict_chat_member(chat.id, user_id, permissions=permissions)
                update.message.reply_text(f"🔇 @{username} কে mute করা হয়েছে।")
            except:
                pass
            return

# Unmute Command
def unmute(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Usage: /unmute @username")
        return

    username = context.args[0].lstrip('@')
    chat = update.effective_chat

    members = chat.get_administrators() + chat.get_members()

    for member in members:
        if member.user.username == username:
            user_id = member.user.id
            permissions = ChatPermissions(can_send_messages=True)
            try:
                context.bot.restrict_chat_member(chat.id, user_id, permissions=permissions)
                update.message.reply_text(f"🔊 @{username} কে unmute করা হয়েছে।")
            except:
                pass
            return

# Start Command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Bot is active! Join @alfazinfosec")

# Main Function
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

# Handlers
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("warn", warn))
dp.add_handler(CommandHandler("mute", mute))
dp.add_handler(CommandHandler("unmute", unmute))
dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))
dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'http[s]?://'), remove_links))
dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'(t\.me\/|telegram\.me\/)'), group_link_ban))
dp.add_handler(MessageHandler(Filters.text & Filters.text, bad_words_filter))
dp.add_handler(MessageHandler(Filters.text & Filters.text, detect_username_change))

updater.start_polling()
updater.idle()
