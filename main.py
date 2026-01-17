import discord
from discord.ext import commands
import os
import sys
import random
from datetime import datetime

class MetropolBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!", 
            intents=intents, 
            help_command=None
        )
        self.inicial_extensions = ['Comandos.moderacion', 'Comandos.servicios']
        # Objeto del servidor para sincronización rápida
        self.GUILD_ID = discord.Object(id=1390152252143964260) 

    async def setup_hook(self):
        print("--- 📥 Cargando Extensiones ---")
        for extension in self.inicial_extensions:
            try:
                await self.load_extension(extension)
                print(f"✅ Extensión cargada: {extension}")
            except Exception as e:
                print(f"❌ Error cargando {extension}: {e}")

        print("--- 🔄 Sincronizando Comandos ---")
        try:
            # Copia los comandos al servidor específico
            self.tree.copy_global_to(guild=self.GUILD_ID)
            await self.tree.sync(guild=self.GUILD_ID)
            print("🚀 Sincronización exitosa en el servidor.")
        except discord.errors.Forbidden:
            print("❌ ERROR 403: No tengo permiso 'applications.commands'.")
            print("👉 RE-INVITA AL BOT USANDO: https://discord.com/api/oauth2/authorize?client_id=" + str(self.user.id if self.user else "ID_DEL_BOT") + "&permissions=8&scope=bot%20applications.commands")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

    async def on_ready(self):
        print(f"--- 🤖 BOT ONLINE: {self.user.name} ---")

bot = MetropolBot()

@bot.event
async def on_message(message):
    if message.author.bot: return

    # Comando de prueba rápido
    if message.content.lower() == "!test":
        await message.reply("✅ El sistema de mensajes funciona correctamente.")

    # Sincronización manual solo para Admins
    if message.content.lower() == "!fuerza":
        if message.author.guild_permissions.administrator:
            try:
                await bot.tree.sync(guild=discord.Object(id=1390152252143964260))
                await message.channel.send("⚡ Sincronización forzada completada.")
            except Exception as e:
                await message.channel.send(f"⚠️ Error: {e}")

    await bot.process_commands(message)

# Comandos de prefijo clásicos
@bot.command()
async def ayuda(ctx):
    await ctx.send("📖 Usa `/auxilio` para pedir mecánica o `!formularios`.")

@bot.command()
async def formularios(ctx):
    await ctx.send("📋 Encontrá los formularios en <#1390152260578967558>")

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ ERROR: No se encontró el token en los Secrets.")
