import logging
import asyncio
import nest_asyncio
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

nest_asyncio.apply()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Load data from vector.json
with open('vector.json', 'r') as f:
    data = json.load(f)

qa_pairs = data.get('qa_pairs', {})
responses = data.get('responses', {})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! Welcome to the setup guide bot.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("""
    The following commands are available:
    
    /start -> Welcome to the bot
    /help -> This message
    /create_vpc -> How to create a VPC network
    /setup_firewall -> How to set up firewall rules
    /create_droplet -> How to create a droplet
    /add_droplet_to_firewall -> How to add a droplet to firewall rules
    /setup_nms -> How to set up NMS
    /log_gcp_console -> How to log onto the GCP Console
    /setup_vpc_gcp -> How to set up a VPC on GCP
    /setup_firewall_policy_gcp -> How to set up a firewall policy on GCP
    /create_vm_gcp -> How to create a VM on GCP
    /vultr_node_setup -> Vultr node setup procedure
    /aws_access_rules -> How to set up access rules in AWS
    /aws_node_registration -> Node registration procedure in AWS
    """)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.lower().strip()
    for question, response in qa_pairs.items():
        if question in user_message :
            await update.message.reply_text(response)
            return
        
    await update.message.reply_text("I'm sorry, I don't have information on that topic. Use /help to see the available commands.")

   

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command = update.message.text[1:].lower()  # Remove the leading '/' and convert to lowercase
    response = responses.get(command, "I'm sorry, I don't have information on that topic. Use /help to see the available commands.")
    await update.message.reply_text(response)

async def main() -> None:
    application = Application.builder().token("7434489725:AAEiQyYSq_isbD0xukUt5oVOEwAuowVxHDs").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("create_vpc", handle_command))
    application.add_handler(CommandHandler("setup_firewall", handle_command))
    application.add_handler(CommandHandler("create_droplet", handle_command))
    application.add_handler(CommandHandler("add_droplet_to_firewall", handle_command))
    application.add_handler(CommandHandler("setup_nms", handle_command))
    application.add_handler(CommandHandler("log_gcp_console", handle_command))
    application.add_handler(CommandHandler("setup_vpc_gcp", handle_command))
    application.add_handler(CommandHandler("setup_firewall_policy_gcp", handle_command))
    application.add_handler(CommandHandler("create_vm_gcp", handle_command))
    application.add_handler(CommandHandler("vultr_node_setup", handle_command))
    application.add_handler(CommandHandler("aws_access_rules", handle_command))
    application.add_handler(CommandHandler("aws_node_registration", handle_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())