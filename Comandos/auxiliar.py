import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from firebase_admin import firestore

class AuxilioButtons(discord.ui.View):
    def __init__(self, chofer, lugar):
        super().__init__(timeout=None)
        self.chofer = chofer
        self.lugar = lugar

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.orange, emoji="🚛")
    async def en_camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.chofer.send(f"✅ Tu auxilio en **{self.lugar}** está en camino.")
        await interaction.response.send_message(f"Asistiendo a {self.chofer.name}.", ephemeral=True)

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.green, emoji="✅")
    async def finalizado(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.chofer.send(f"🏁 Tu auxilio en **{self.lugar}** ha finalizado.")
        # Registro en Firebase
        db = firestore.client()
        db.collection("Auxilios").add({
            "Chofer": self.chofer.name,
            "Auxiliar": interaction.user.name,
            "Lugar": self.lugar,
            "Fecha": datetime.now()
        })
        await interaction.response.send_message("Auxilio marcado como finalizado.", ephemeral=True)

class Auxilio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="auxilio", description="Solicitar auxilio mecánico")
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        if interaction.channel_id != 1390464495725576304:
            return await interaction.response.send_message("Solo en el canal de Solicitud de Auxilio.", ephemeral=True)
        
        # Filtrar roles prohibidos (Cliente: 1390152252143964262)
        if any(r.id == 1390152252143964262 for r in interaction.user.roles):
            return await interaction.response.send_message("No tienes permiso.", ephemeral=True)

        embed = discord.Embed(title="📛 Solicitud de Auxilio", color=discord.Color.orange())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Chofer", value=chofer.mention)
        embed.add_field(name="Motivo", value=motivo)
        embed.add_field(name="Lugar", value=lugar)
        embed.set_image(url=foto.url)
        embed.set_footer(text=f"La Nueva Metropol S.A. | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        canal_embed = interaction.guild.get_channel(1461926580078252054)
        file = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        
        view = AuxilioButtons(chofer, lugar)
        await canal_embed.send(content="<@&1390152252143964268> ¡Nueva solicitud!", file=file, embed=embed, view=view)
        await interaction.response.send_message("Solicitud enviada.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Auxilio(bot))
