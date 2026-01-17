import discord
from discord.ext import commands
import os
import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
import json

async def sincronizar():
    # Inicializar Firebase para que no de error al cargar los Cogs
    if not firebase_admin._apps:
        fb_config = os.getenv('FIREBASE_CONFIG')
        if fb_config:
            cred = credentials.Certificate(json.loads(fb_config.strip()))
            firebase_admin.initialize_app(cred)

    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    extensions = ['Comandos.moderacion', 'Comandos.servicios']
    
    async with bot:
        print("--- 🗑️ Limpiando comandos antiguos ---")
        await bot.login(os.getenv('DISCORD_TOKEN'))
        
        # Sincronizar vacío para limpiar la caché de Discord
        bot.tree.clear(guild=None)
        await bot.tree.sync()
        
        print("--- 📥 Cargando extensiones nuevas ---")
        for ext in extensions:
            try:
                await bot.load_extension(ext)
                print(f"✅ Cargado: {ext}")
            except Exception as e:
                print(f"❌ Error en {ext}: {e}")
        
        # Sincronizar los comandos reales
        print("--- 🚀 Sincronizando comandos de Firestore ---")
        comandos = await bot.tree.sync()
        
        print(f"--- ✅ ÉXITO ---")
        print(f"Se registraron {len(comandos)} comandos. El bot ya debería reconocer /auxilio.")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(sincronizar())
