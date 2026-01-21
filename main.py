import discord
from discord.ext import commands
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import asyncio

# --- CONFIGURACIÓN DEL BOT ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- FIREBASE (Desde el Secret como recordamos) ---
firebase_config = os.getenv("FIREBASE_CONFIG")
bot.db = None
if firebase_config:
    try:
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        bot.db = firestore.client()
        print("✅ Firebase conectado.")
    except Exception as e:
        print(f"❌ Error Firebase: {e}")

# --- CARGA DE EXTENSIONES ---
async def load_extensions():
    for folder in ['Comandos', 'Interacciones']:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith('.py'):
                    try:
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                        print(f'✅ Cargado: {filename}')
                    except Exception as e:
                        print(f'❌ Error cargando {filename}: {e}')

@bot.event
async def on_ready():
    print(f"🚀 Bot iniciado como: {bot.user}")
    print("👉 Escribí !setup en tu servidor para activar los comandos.")

# --- COMANDO DE EMERGENCIA ---
@bot.command(name="setup")
async def setup_servidor(ctx):
    # ID del rol Staff que me pasaste
    staff_role_id = 1448477246221189234
    if not any(role.id == staff_role_id for role in ctx.author.roles):
        return await ctx.send("❌ No tenés el rol de Staff.")

    await ctx.send("⚙️ **Sincronizando comandos en este servidor...**")
    try:
        # Esto trae todos los comandos de las carpetas y los activa en tu server
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"✅ ¡LISTO! Se activaron {len(synced)} comandos. Si no los ves, reiniciá el Discord (Ctrl+R).")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

async def main():
    async with bot:
        await load_extensions()
        token = os.getenv("DISCORD_TOKEN")
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
