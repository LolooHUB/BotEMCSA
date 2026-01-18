import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Sincronizando comandos de barra...")
    try:
        # Cargar todos los cogs antes de sincronizar
        for folder in ['Comandos', 'Interacciones']:
            for filename in os.listdir(f'./{folder}'):
                if filename.endswith('.py'):
                    await bot.load_extension(f'{folder}.{filename[:-3]}')
        
        synced = await bot.tree.sync()
        print(f"Se han sincronizado {len(synced)} comandos.")
    except Exception as e:
        print(f"Error sincronizando: {e}")
    await bot.close()

bot.run(os.getenv("DISCORD_TOKEN"))
