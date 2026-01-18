import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from firebase_admin import firestore

# Definimos la vista afuera para que no interfiera con el registro del comando
class AuxilioButtons(discord.ui.View):
    def __init__(self, chofer_id, lugar):
        super().__init__(timeout=None)
        self.chofer_id = chofer_id
        self.lugar = lugar

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.orange, emoji="🚛")
    async def en_camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Asistencia marcada en camino.", ephemeral=True)

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.green, emoji="✅")
    async def finalizado(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Auxilio finalizado.", ephemeral=True)
        await interaction.message.delete()

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red, emoji="🛑")
    async def rechazar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Solicitud rechazada.", ephemeral=True)
        await interaction.message.delete()

class Auxiliar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Cambiamos el nombre interno de la función para que no choque con el nombre del comando
    @app_commands.command(name="auxilio", description="Solicitar asistencia mecánica Metropol")
    async def solicitar_auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        """Comando para solicitar auxilio"""
        
        # Validaciones movidas aquí adentro para que no bloqueen el registro del comando
        if interaction.channel_id != 1390464495725576304:
            return await interaction.response.send_message("Usa el canal de auxilio.", ephemeral=True)

        # Crear el mensaje
        embed = discord.Embed(title="📛 Solicitud de Auxilio", color=discord.Color.orange())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Chofer", value=chofer.mention)
        embed.add_field(name="Lugar", value=lugar)
        embed.add_field(name="Motivo", value=motivo)
        embed.set_image(url=foto.url)
        embed.set_footer(text=f"La Nueva Metropol S.A. | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        canal_destino = interaction.guild.get_channel(1461926580078252054)
        file = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        
        view = AuxilioButtons(chofer.id, lugar)
        await canal_destino.send(content="<@&1390152252143964268> NUEVA SOLICITUD", file=file, embed=embed, view=view)
        
        await interaction.response.send_message("✅ Solicitud enviada.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Auxiliar(bot))
