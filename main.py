import discord
from discord.ext import commands, tasks
import os
import sys
import logging
import random
from datetime import datetime

# Configuración de Logs
logging.basicConfig(level=logging.INFO)

class MetropolBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!", 
            intents=intents, 
            help_command=None,
            chunk_guilds_at_startup=True
        )
        self.inicial_extensions = ['Comandos.moderacion', 'Comandos.servicios']
        self.canal_logs_id = 1390152261937922070
        self.GUILD_ID = discord.Object(id=1390152252143964260) 

    async def setup_hook(self):
        print("--- 📥 Cargando Extensiones ---")
        for extension in self.inicial_extensions:
            try:
                await self.load_extension(extension)
                print(f"✅ Cargado: {extension}")
            except Exception as e:
                print(f"❌ ERROR en {extension}: {e}")

        print("--- 🔄 Sincronizando Comandos en Servidor ---")
        try:
            # Esto mueve los comandos al servidor para que aparezcan rápido
            self.tree.copy_global_to(guild=self.GUILD_ID)
            comandos = await self.tree.sync(guild=self.GUILD_ID)
            print(f"✨ LISTO: {len(comandos)} comandos de barra registrados.")
        except Exception as e:
            print(f"❌ Error en sync: {e}")

    @tasks.loop(minutes=20)
    async def presencia_loop(self):
        await self.wait_until_ready()
        estados = ["¿Cuándo pasa la 65?", "La Nueva Metropol S.A.", "Control de Unidades"]
        await self.change_presence(activity=discord.Game(name=random.choice(estados)))

    async def on_ready(self):
        if not self.presencia_loop.is_running():
            self.presencia_loop.start()
        print(f"--- 🤖 BOT ONLINE: {self.user.name} ---")

bot = MetropolBot()

# --- EVENTOS ---
@bot.event
async def on_member_join(member):
    canal = bot.get_channel(bot.canal_logs_id)
    if canal:
        embed = discord.Embed(title="📥 Nuevo Miembro", description=f"{member.mention} se unió.", color=discord.Color.green(), timestamp=datetime.now())
        await canal.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot: return

    # Respuesta a menciones
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        respuestas = ["¿Necesitás ayuda? Usá !ayuda", "¡QUÉ QUERÉEEEEES!"]
        await message.reply(random.choice(respuestas))

    contenido = message.content.lower()
    if contenido == "!ayuda":
        await message.reply("📖 **Metropol Sistema:**\n`/auxilio` - Pedir mecánica.\n`!formularios` - Enlaces.")
    elif contenido == "!formularios":
        await message.reply("📋 Encontrá los formularios en <#1390152260578967558>")
    
    await bot.process_commands(message)

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ ERROR: Token no encontrado.")
