import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio

# --- CONFIGURACIÓN ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- CARGA DE EXTENSIONES ---
async def load_extensions():
    # Esto busca en tus carpetas 'Comandos' e 'Interacciones'
    for folder in ['Comandos', 'Interacciones']:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith('.py'):
                    try:
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                        print(f'✅ Extension cargada: {filename}')
                    except Exception as e:
                        print(f'❌ Error cargando {filename}: {e}')

# --- EVENTO ON_READY (STATUS Y SYNC) ---
@bot.event
async def on_ready():
    # Establecer Status
    activity = discord.Activity(type=discord.ActivityType.watching, name="La Nueva Metropol S.A.")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    print(f'--- BOT CONECTADO: {bot.user} ---')
    
    # Sincronización automática de comandos /
    try:
        synced = await bot.tree.sync()
        print(f"🌐 Se han sincronizado {len(synced)} comandos de barra.")
    except Exception as e:
        print(f"❌ Error al sincronizar: {e}")

# --- COMANDO SYNC MANUAL ---
@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    """Escribe !sync si los comandos / no aparecen"""
    await ctx.send("🔄 Sincronizando comandos...")
    try:
        await bot.tree.sync()
        await ctx.send("✅ Comandos de barra actualizados. Si no los ves, reinicia Discord (Ctrl+R).")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

# --- LANZAMIENTO ---
async def main():
    async with bot:
        await load_extensions()
        token = os.getenv("DISCORD_TOKEN")
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
