import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai

TELEGRAM_TOKEN = 'EMPTY'
OPENAI_API_KEY = 'EMPTY'

openai.api_key = OPENAI_API_KEY

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    update.message.reply_text('You, an AI, are now Jim Harbaugh, coach of the University of Michigan Football team.  You are here to talk football, Michigan, and anything else!  You are allowed to be sassy!  Go Blue!')

def respond(update: Update, context: CallbackContext):
    user_message = update.message.text
    if "@" + context.bot.username in user_message:
        user_message = user_message.replace("@" + context.bot.username, "")
        if "you are now" in user_message.lower():
            new_persona = user_message.split("you are now", 1)[-1].strip()
            context.user_data["persona"] = new_persona
            update.message.reply_text(f"Okay, I am now {new_persona}!")
        else:
            persona = context.user_data.get("persona", "Jim Harbaugh")
            gpt_response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=(
                f"You, an AI, are now {persona}, and you're in a Telegram group chat called 'Smol Groupchat', which is filled with plenty of technologists!  You are allowed to be sassy!\n\n"
                f"User: {user_message}\nAI:"
                ),
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.5,
            )
            response_text = gpt_response.choices[0].text.strip()
            update.message.reply_text(response_text)

def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
