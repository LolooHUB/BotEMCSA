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
        print("✅ Firebase Conectado correctamente.")
    except Exception as e:
        print(f"❌ Error al conectar Firebase: {e}")

# --- CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.db = db # Compartimos la DB para que los comandos la usen

# --- CARGA DE EXTENSIONES (Carpetas) ---
async def load_extensions():
    for folder in ['Comandos', 'Interacciones']:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith('.py'):
                    try:
                        # Evitamos cargar archivos duplicados o temporales
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                        print(f'✅ Extensión cargada: {folder}/{filename}')
                    except Exception as e:
                        print(f'❌ Error cargando {filename}: {e}')

@bot.event
async def on_ready():
    # Establecer Status
    activity = discord.Activity(type=discord.ActivityType.watching, name="Expreso Martín Coronado S.A.")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    # Sincronización inicial rápida
    try:
        await bot.tree.sync()
        print(f"🚀 Bot Online: {bot.user} | Comandos Sincronizados")
    except Exception as e:
        print(f"❌ Error en Sync inicial: {e}")

# --- COMANDO PARA LIMPIAR DUPLICADOS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def sync(ctx):
    """Limpia la caché de comandos y resincroniza todo"""
    await ctx.send("♻️ **Limpiando comandos duplicados...** esto puede tardar unos segundos.")
    try:
        # 1. Limpia los comandos del árbol interno
        bot.tree.clear_commands(guild=ctx.guild)
        
        # 2. Sincroniza (esto pisa cualquier comando viejo en el servidor)
        await bot.tree.sync(guild=ctx.guild)
        await bot.tree.sync() # Sincronización global
        
        await ctx.send("✅ **Limpieza completada.**\n⚠️ **IMPORTANTE:** Si seguís viendo duplicados, presioná `Ctrl + R` en PC o reiniciá la app en el celular.")
    except Exception as e:
        await ctx.send(f"❌ Error durante la sincronización: {e}")

# --- ARRANQUE DEL BOT ---
async def main():
    async with bot:
        await load_extensions()
        token = os.getenv("DISCORD_TOKEN")
        if token:
            await bot.start(token)
        else:
            print("❌ ERROR: No se encontró el DISCORD_TOKEN en los Secrets.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
