import os
import discord
import logging
from dotenv import load_dotenv
from discord.ext import commands
from expense_parser import parse_expense
from sheets_manager import ExpenseSheetManager
from config import CONFIG


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

# Create bot instance with intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)
sheets_manager = None

@bot.event
async def on_ready():
    """Event triggered when the bot is logged in and ready."""
    global sheets_manager
    
    logger.info(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info('------')
    
    # Initialize Google Sheets manager
    try:
        sheets_manager = ExpenseSheetManager()
        logger.info("Google Sheets manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets manager: {str(e)}")

@bot.event
async def on_message(message):
    """Event triggered when the bot receives a message."""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Only process direct messages
    if not isinstance(message.channel, discord.DMChannel):
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # If not a command, try to parse as an expense
    if not message.content.startswith(bot.command_prefix):
        try:
            expense = parse_expense(message.content)
            if expense:
                # Save expense to Google Sheets
                if sheets_manager:
                    result = sheets_manager.add_expense(expense)
                    await message.channel.send(f"✅ Expense saved: {expense['amount']} for {expense['category']} - {expense['description']}")
                else:
                    await message.channel.send("❌ Google Sheets connection not established. Try again later.")
            else:
                await message.channel.send("❓ I couldn't understand that expense format. Try something like: '$10 lunch' or '20 gas'")
        except Exception as e:
            logger.error(f"Error processing expense: {str(e)}")
            await message.channel.send(f"❌ Error processing expense: {str(e)}")

@bot.command(name="expensehelp")
async def expense_help_command(ctx):
    """Show help information about the bot."""
    help_text = """
**Expense Tracker Bot Help**

**Direct Message Format:**
Simply send me a message with your expense like:
- `$10 lunch`
- `20 gas`
- `15.99 groceries at Walmart`

**Commands:**
- `!expensehelp` - Show this help message
- `!recent [n]` - Show your n most recent expenses (default: 5)
- `!total [category]` - Show total expenses [in a category]
- `!categories` - List all expense categories

I'll save your expenses to a Google Sheet automatically!
    """
    await ctx.send(help_text)

@bot.command(name="recent")
async def recent_command(ctx, count: int = 5):
    """Show recent expenses."""
    if sheets_manager:
        try:
            expenses = sheets_manager.get_recent_expenses(count)
            if expenses:
                message = "**Recent Expenses:**\n"
                for expense in expenses:
                    message += f"• {expense['date']}: ${expense['amount']} for {expense['category']} - {expense['description']}\n"
                await ctx.send(message)
            else:
                await ctx.send("No recent expenses found.")
        except Exception as e:
            logger.error(f"Error retrieving recent expenses: {str(e)}")
            await ctx.send(f"❌ Error retrieving recent expenses: {str(e)}")
    else:
        await ctx.send("❌ Google Sheets connection not established. Try again later.")

@bot.command(name="total")
async def total_command(ctx, category: str = None):
    """Show total expenses, optionally filtered by category."""
    if sheets_manager:
        try:
            total, breakdown = sheets_manager.get_total_expenses(category)
            
            if category:
                message = f"**Total Expenses for {category.capitalize()}:** ${total:.2f}"
            else:
                message = f"**Total Expenses:** ${total:.2f}\n\n**Breakdown by Category:**\n"
                for cat, amount in breakdown.items():
                    message += f"• {cat}: ${amount:.2f}\n"
                    
            await ctx.send(message)
        except Exception as e:
            logger.error(f"Error retrieving total expenses: {str(e)}")
            await ctx.send(f"❌ Error retrieving total expenses: {str(e)}")
    else:
        await ctx.send("❌ Google Sheets connection not established. Try again later.")

@bot.command(name="categories")
async def categories_command(ctx):
    """List all expense categories."""
    if sheets_manager:
        try:
            categories = sheets_manager.get_categories()
            if categories:
                await ctx.send("**Available Categories:**\n• " + "\n• ".join(categories))
            else:
                await ctx.send("No expense categories found yet.")
        except Exception as e:
            logger.error(f"Error retrieving categories: {str(e)}")
            await ctx.send(f"❌ Error retrieving categories: {str(e)}")
    else:
        await ctx.send("❌ Google Sheets connection not established. Try again later.")

def start_bot():
    """Start the Discord bot with the token from environment variables."""
    token = os.environ.get('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("DISCORD_BOT_TOKEN not found in environment variables")
        raise ValueError("DISCORD_BOT_TOKEN not found in environment variables")
    
    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        raise

if __name__ == "__main__":
    start_bot()
