import discord
from discord.ext import commands
from discord import app_commands
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- VISTA DE BOTONES (USANDO ESTILOS ESTÁNDAR) ---
class AuxilioButtons(discord.ui.View):
    def __init__(self, chofer_id, lugar):
        super().__init__(timeout=None)
        self.chofer_id = chofer_id
        self.lugar = lugar

    # Estilo 1 = Azul (Primary), 2 = Gris (Secondary), 3 = Verde (Success), 4 = Rojo (Danger)
    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.primary, emoji="🚛") 
    async def en_camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Asistencia marcada en camino.", ephemeral=True)

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.success, emoji="✅") 
    async def finalizado(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Auxilio finalizado.", ephemeral=True)
        await interaction.message.delete()

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.danger, emoji="🛑") 
    async def rechazar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Solicitud rechazada.", ephemeral=True)
        await interaction.message.delete()

# --- COMANDO AUXILIO ---
@bot.tree.command(name="auxilio", description="Pedir asistencia mecanica Metropol")
async def auxilio(interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
    if interaction.channel_id != 1390464495725576304:
        return await interaction.response.send_message("Usa el canal de auxilio.", ephemeral=True)
    
    embed = discord.Embed(title="📛 Solicitud de Auxilio", color=discord.Color.orange())
    embed.add_field(name="Chofer", value=chofer.mention)
    embed.add_field(name="Lugar", value=lugar)
    embed.add_field(name="Motivo", value=motivo)
    
    if foto:
        embed.set_image(url=foto.url)
    
    canal_destino = interaction.guild.get_channel(1461926580078252054)
    if canal_destino:
        view = AuxilioButtons(chofer.id, lugar)
        await canal_destino.send(content="<@&1390152252143964268> NUEVA SOLICITUD", embed=embed, view=view)
        await interaction.response.send_message("✅ Solicitud enviada.", ephemeral=True)
    else:
        await interaction.response.send_message("Canal de destino no encontrado.", ephemeral=True)

# --- SETUP ---
@bot.event
async def setup_hook():
    for folder in ['Comandos', 'Interacciones']:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if filename.endswith('.py') and filename != 'auxiliar.py':
                    try:
                        await bot.load_extension(f'{folder}.{filename[:-3]}')
                    except Exception as e:
                        print(f'Error en {filename}: {e}')
    await bot.tree.sync()

@bot.event
async def on_ready():
    print(f'✅ Bot ONLINE: {bot.user}')

token = os.getenv("DISCORD_TOKEN")
bot.run(token)
