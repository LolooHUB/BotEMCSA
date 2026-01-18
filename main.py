import discord
from discord.ext import commands
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import asyncio

# --- CONFIGURACIÓN DE FIREBASE ---
firebase_config = os.getenv("FIREBASE_CONFIG")
db = None

if firebase_config:
    try:
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase Conectado (FIREBASE_CONFIG)")
    except Exception as e:
        print(f"❌ Error Firebase: {e}")

# --- CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.db = db

# --- CARGA DINÁMICA DE COMANDOS ---
async def load_extensions():
    # Solo cargamos archivos de estas carpetas
    for folder in ['Comandos', 'Interacciones']:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith('.py'):
                    try:
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                        print(f'✅ Extensión cargada: {filename}')
                    except Exception as e:
                        print(f'❌ Error cargando {filename}: {e}')

@bot.event
async def on_ready():
    # Status del bot
    activity = discord.Activity(type=discord.ActivityType.watching, name="La Nueva Metropol S.A.")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    # Sincronización (Limpia lo viejo y pone lo nuevo)
    try:
        await bot.tree.sync()
        print(f"🚀 Bot Online: {bot.user} | Comandos Sincronizados")
    except Exception as e:
        print(f"❌ Error Sync: {e}")

# --- COMANDO DE EMERGENCIA PARA LIMPIAR CACHÉ ---
@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    """Escribe !sync si ves comandos duplicados"""
    await ctx.send("♻️ Limpiando caché de comandos y re-sincronizando...")
    try:
        # Borra los comandos locales del servidor antes de subir los nuevos
        bot.tree.clear(guild=ctx.guild)
        await bot.tree.sync(guild=ctx.guild)
        # Sincroniza los comandos globales
        await bot.tree.sync()
        await ctx.send("✅ Limpieza completada. Si siguen duplicados, reiniciá tu Discord (Ctrl+R).")
    except Exception as e:
        await ctx.send(f"❌ Falló la limpieza: {e}")

# --- INICIO ---
async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
