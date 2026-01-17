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
        # 1. Limpieza de comandos duplicados
        print("--- 🗑️ Limpiando Comandos Globales ---")
        self.tree.clear(guild=None)
        await self.tree.sync(guild=None)

        # 2. Carga de Cogs (Moderación y Servicios)
        print("--- 📥 Cargando Extensiones ---")
        for extension in self.inicial_extensions:
            try:
                await self.load_extension(extension)
                print(f"✅ Extensión cargada: {extension}")
            except Exception as e:
                print(f"❌ Error cargando {extension}: {e}")

        # 3. Sincronización instantánea en tu servidor
        print("--- 🔄 Sincronizando Servidor Metropol ---")
        self.tree.copy_global_to(guild=self.GUILD_ID)
        comandos = await self.tree.sync(guild=self.GUILD_ID)
        print(f"✅ Éxito: {len(comandos)} comandos de barra activos.")

    @tasks.loop(minutes=20)
    async def presencia_loop(self):
        await self.wait_until_ready()
        estados = [
            "¿Cuándo pasa la 65?", 
            "La Nueva Metropol S.A.", 
            "Control de Unidades", 
            "¡Qué lindos los ints!"
        ]
        await self.change_presence(activity=discord.Game(name=random.choice(estados)))

    async def on_ready(self):
        if not self.presencia_loop.is_running():
            self.presencia_loop.start()
        print(f"--- 🤖 BOT ONLINE COMO: {self.user.name} ---")

# Instancia
bot = MetropolBot()

# --- EVENTOS DE BIENVENIDA Y AUDITORÍA ---
@bot.event
async def on_member_join(member):
    canal = bot.get_channel(bot.canal_logs_id)
    if canal:
        embed = discord.Embed(
            title="📥 Nuevo Miembro", 
            description=f"{member.mention} se unió al servidor de la Metropol.", 
            color=discord.Color.green(), 
            timestamp=datetime.now()
        )
        await canal.send(embed=embed)

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"❌ Error en comando /{interaction.command.name if interaction.command else 'N/A'}: {error}")

# --- COMANDOS CLÁSICOS (!) Y MENCIONES ---
@bot.event
async def on_message(message):
    if message.author.bot: return

    # Respuesta a menciones del bot
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        respuestas = ["¿Necesitás ayuda? Usá !ayuda", "¿Ya te inscribiste a Metropol?", "¡QUÉ QUERÉEEEEES!"]
        await message.reply(random.choice(respuestas))

    # Comandos de texto clásicos
    contenido = message.content.lower()
    
    if contenido == "!ayuda":
        await message.reply("📖 **Comandos disponibles:**\n`!formularios` - Enlaces de inscripción.\n`!ayuda` - Este mensaje.\nPara auxilio mecánico, usá `/auxilio`.")
    
    elif contenido == "!formularios":
        await message.reply("📋 Encontrá todos los formularios necesarios en <#1390152260578967558>")

    elif contenido == "!sync" and message.author.guild_permissions.administrator:
        await bot.tree.sync(guild=discord.Object(id=1390152252143964260))
        await message.reply("🔄 Sincronización forzada completada.")

    # Procesar comandos clásicos adicionales (si los hubiera)
    await bot.process_commands(message)

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ ERROR: No se encontró el DISCORD_TOKEN en los Secrets.")
