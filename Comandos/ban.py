import discord
from discord import app_commands
from datetime import datetime
import firebase_admin
from firebase_admin import firestore

class BanModal(discord.ui.Modal, title='Baneo de Usuario'):
    motivo = discord.ui.TextInput(label='Motivo', style=discord.TextStyle.paragraph)
    duracion = discord.ui.TextInput(label='Duración', placeholder='Ej: 7 días o Permanente')

    def __init__(self, member, evidencia=None):
        super().__init__()
        self.member = member
        self.evidencia = evidencia

    async def on_submit(self, interaction: discord.Interaction):
        db = firestore.client()
        
        # Guardar en Firebase
        data = {
            'Usuario': str(self.member.id),
            'Moderador': str(interaction.user.id),
            'Motivo': self.motivo.value,
            'Fecha': datetime.now(),
            'Tipo': 'Ban'
        }
        db.collection('Baneos').add(data)

        # Banear en Discord
        await self.member.ban(reason=self.motivo.value)

        # Embed de respuesta
        embed = discord.Embed(title="⛔ Usuario Baneado", color=discord.Color.red())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Usuario", value=self.member.mention)
        embed.add_field(name="Motivo", value=self.motivo.value)
        embed.add_field(name="Duración", value=self.duracion.value)
        if self.evidencia:
            embed.add_field(name="Evidencia", value="Adjunta en mensaje")
        
        embed.set_footer(text=f"La Nueva Metropol S.A. | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        canal_sanciones = interaction.guild.get_channel(1397738825609904242)
        file = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        await canal_sanciones.send(file=file, embed=embed)
        await interaction.response.send_message("Usuario baneado con éxito.", ephemeral=True)
