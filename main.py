import discord
from discord.ext import commands
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import asyncio

# 1. CONFIGURACIÓN DEL BOT (Mover aquí arriba)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# 2. CONFIGURACIÓN DE FIREBASE
firebase_config = os.getenv("FIREBASE_CONFIG")
db = None

if firebase_config:
    try:
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        bot.db = db # Ahora sí podemos asignar db al bot
        print("✅ Firebase Conectado correctamente.")
    except Exception as e:
        print(f"❌ Error al conectar Firebase: {e}")

# 3. CARGA DE EXTENSIONES
async def load_extensions():
    for folder in ['Comandos', 'Interacciones']:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith('.py'):
                    try:
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                        print(f'✅ Extensión cargada: {folder}/{filename}')
                    except Exception as e:
                        print(f'❌ Error cargando {filename}: {e}')

# 4. EVENTOS (Ahora 'bot' ya existe)
@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.watching, name="Expreso Martín Coronado S.A.")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    try:
        await bot.tree.sync()
        print(f"🚀 Bot Online: {bot.user} | Comandos Sincronizados")
    except Exception as e:
        print(f"❌ Error en Sync inicial: {e}")

# 5. ARRANQUE
async def main():
    async with bot:
        await load_extensions()
        token = os.getenv("DISCORD_TOKEN")
        if token:
            await bot.start(token)
        else:
            print("❌ ERROR: No se encontró el DISCORD_TOKEN.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass