import discord
from discord.ext import commands, tasks
import os
import sys
import logging
import random
from datetime import datetime

# Configuración de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')

class MetropolBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            chunk_guilds_at_startup=True
        )
        self.inicial_extensions = [
            'Comandos.moderacion',
            'Comandos.servicios'
        ]
        self.canal_logs_id = 1390152261937922070

    async def setup_hook(self):
        print("--- Iniciando Carga de Extensiones ---")
        for extension in self.inicial_extensions:
            try:
                await self.load_extension(extension)
                print(f"✅ Extensión cargada: {extension}")
            except Exception as e:
                print(f"❌ Error cargando {extension}: {e}")

        print("--- Sincronizando Comandos de Barra ---")
        try:
            await self.tree.sync()
            print("✅ Sincronización completada.")
        except Exception as e:
            print(f"❌ Error sincronizando tree: {e}")

    @tasks.loop(minutes=20)
    async def presencia_loop(self):
        await self.wait_until_ready()
        estados = ["Cuando pasa la 65?", "Ya te anotaste para Metropol?", "Que lindos los ints de Metropol!"]
        nuevo_estado = random.choice(estados)
        try:
            await self.change_presence(status=discord.Status.online, activity=discord.Game(name=nuevo_estado))
        except Exception as e:
            print(f"❌ Falló presencia: {e}")

    async def on_ready(self):
        if not self.presencia_loop.is_running():
            self.presencia_loop.start()
        print(f"--- BOT ONLINE: {self.user.name} ---")

# Instancia del bot
bot = MetropolBot()

# --- EVENTOS DE AUDITORÍA Y LOGS ---
@bot.event
async def on_member_join(member):
    canal = bot.get_channel(bot.canal_logs_id)
    if canal:
        embed = discord.Embed(title="📥 Nuevo Miembro", description=f"{member.mention} se unió al servidor.", color=discord.Color.green(), timestamp=datetime.now())
        await canal.send(embed=embed)

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error):
    canal = bot.get_channel(bot.canal_logs_id)
    if canal:
        embed = discord.Embed(title="❌ Error de Comando", description=f"Usuario: {interaction.user}\nComando: {interaction.command.name if interaction.command else 'N/A'}\nError: `{error}`", color=discord.Color.red(), timestamp=datetime.now())
        await canal.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        respuestas = ["¿Necesitas ayuda?, hace !ayuda", "¿Ya te inscribiste a Metropol?", "QUE QUERESSSSSS"]
        await message.reply(random.choice(respuestas))

    contenido = message.content.lower()
    if contenido == "!ayuda":
        await message.reply("Usa !formularios o abre un ticket en <#1390152260578967559>")
    if contenido == "!formularios":
        await message.reply("Fijate en <#1390152260578967558>")
    
    await bot.process_commands(message)

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token: sys.exit(1)
    bot.run(token)
