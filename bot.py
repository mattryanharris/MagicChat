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
    if update.message.text.startswith("/prompt"):
        prompt = update.message.text.replace("/prompt", "").strip()
        context.user_data["prompt"] = prompt
        update.message.reply_text(f"Prompt set to:\n{prompt}")
        return

    if update.message.reply_to_message and update.message.reply_to_message.from_user.username == context.bot.username:
        user_message = update.message.text
        persona = context.user_data.get("persona", "Jim Harbaugh")
        prompt = context.user_data.get("prompt", f"You, an AI, are now {persona}, and you're in a Telegram group chat called 'Smol Groupchat', which is filled with plenty of technologists!  You are allowed to be sassy!\n\n")
        gpt_response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=(
                f"{prompt}"
                f"User: {user_message}\nAI:"
            ),
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5,
        )
        response_text = gpt_response.choices[0].text.strip()
        update.message.reply_text(response_text)
    else:
        if context.bot.username in update.message.text:
            user_message = update.message.text.replace(f"@{context.bot.username} ", "")
            persona = context.user_data.get("persona", "Jim Harbaugh")
            prompt = context.user_data.get("prompt", f"You, an AI, are now {persona}, and you're in a Telegram group chat called 'Smol Groupchat', which is filled with plenty of technologists!  You are allowed to be sassy!\n\n")
            gpt_response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=(
                    f"{prompt}"
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

def set_prompt(update: Update, context: CallbackContext):
    prompt_text = update.message.text.replace("/prompt", "").strip()
    prompt_text = "You, an AI, are now " + prompt_text + ", and you're in a Telegram group chat called 'Smol Groupchat', which is filled with plenty of technologists!  You are allowed to be sassy!  They will be messaging you\n\n"
    context.user_data["prompt"] = prompt_text
    update.message.reply_text(f"Prompt set")


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to MagicChat! Here's how to use me:\n\n"
                              "To set your own prompt, just type /prompt followed by whatever you want.\n"
                              "I'll use that prompt for my responses until you change it.\n\n Please be advised these bots are good with one-off questions, but not so good with long conversations.\n\n"
                              "Go Blue!")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("prompt", set_prompt))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
