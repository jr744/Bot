import os
import sys
import discord
import logging
from discord.ext import commands
from discord import app_commands

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'DiscordTicketBot')))



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ticket_bot')

os.makedirs('data', exist_ok=True)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = "MTM0ODAxNzczOTUzMjQ3MjM2Mg.GlnOCv.EHmKNmQcOwwdAKJxPgjOkgdgDRfVId7_H-xhx8"
if not TOKEN:
    logger.error("Token não encontrado!")
    exit(1)

@bot.event
async def on_ready():
    logger.info(f'Bot logged in as {bot.user.name} (ID: {bot.user.id})')
    print(f'Bot logged in as {bot.user.name} (ID: {bot.user.id})')
    try:
        print("Verificando tickets para canais inexistentes...")
        await verify_ticket_channels()
        print("Verificação de tickets concluída")
    except Exception as e:
        logger.error(f"Erro ao verificar tickets: {e}")
        print(f"Erro ao verificar tickets: {e}")
    
    try:
        print("Loading cogs...")
        await bot.load_extension("cogs.ticket_commands")
        print("- Ticket commands loaded")
        await bot.load_extension("cogs.ticket_buttons")
        print("- Ticket buttons loaded")
        await bot.load_extension("cogs.ticket_dropdowns")
        print("- Ticket dropdowns loaded")
        await bot.load_extension("cogs.ticket_modals")
        print("- Ticket modals loaded")
        logger.info("All cogs loaded successfully")
        print("All cogs loaded successfully")
    except Exception as e:
        logger.error(f"Error loading cogs: {e}")
        print(f"Error loading cogs: {e}")
    
    try:
        print("Syncing commands...")
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
        print(f"Failed to sync commands: {e}")

    activity = discord.Game(name="Gerenciando Tickets 🎟️")
    await bot.change_presence(status=discord.Status.online, activity=activity)

async def verify_ticket_channels():
    from DiscordTicketBot.utils.config_manager import _load_json, delete_ticket_data
    tickets_file = "data/tickets.json"
    tickets = _load_json(tickets_file)
    
    removed_count = 0
    
    for guild_id, guild_tickets in list(tickets.items()):
        try:
            guild = bot.get_guild(int(guild_id))
            if not guild:
                logger.warning(f"Guild {guild_id} não encontrada, pulando verificação")
                continue
                
            for channel_id in list(guild_tickets.keys()):
                try:
                    channel = guild.get_channel(int(channel_id))
                    if not channel:
                        delete_ticket_data(guild_id, channel_id)
                        logger.info(f"Ticket removido: canal {channel_id} não existe mais no servidor {guild_id}")
                        removed_count += 1
                except Exception as e:
                    logger.error(f"Erro ao verificar canal {channel_id}: {e}")
        except Exception as e:
            logger.error(f"Erro ao verificar tickets do servidor {guild_id}: {e}")
    
    if removed_count > 0:
        logger.info(f"Total de {removed_count} tickets removidos durante a verificação")
        print(f"Total de {removed_count} tickets removidos durante a verificação")

@bot.event
async def on_guild_join(guild):
    logger.info(f"Bot joined a new guild: {guild.name} (ID: {guild.id})")
    from DiscordTicketBot.utils.config_manager import initialize_guild_config
    initialize_guild_config(guild.id)

@bot.event
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("Você não tem permissão para usar este comando!", ephemeral=True)
    else:
        logger.error(f"Command error: {error}")
        await interaction.response.send_message(f"Ocorreu um erro ao executar o comando: {error}", ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
