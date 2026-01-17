import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import random
from firebase_admin import firestore

class AuxilioButtons(discord.ui.View):
    def __init__(self, caso_id):
        super().__init__(timeout=None)
        self.caso_id = caso_id

    async def actualizar_db(self, interaction, estado, color, emoji):
        db = firestore.client()
        db.collection("SolicitudesAuxilio").document(self.caso_id).update({
            "estado": estado, "auxiliar": interaction.user.name
        })
        embed = interaction.message.embeds[0]
        embed.title = f"{emoji} Caso #{self.caso_id}: {estado}"
        embed.color = color
        embed.set_footer(text=f"Atendido por {interaction.user.name}")
        
        view = None if estado in ["Finalizado", "Rechazado"] else self
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.orange, emoji="🚨")
    async def camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.actualizar_db(interaction, "En Camino", discord.Color.orange(), "🚑")

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.green, emoji="✅")
    async def fin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.actualizar_db(interaction, "Finalizado", discord.Color.green(), "🏁")

class Servicios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="auxilio", description="Solicitar auxilio mecánico")
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        if interaction.channel_id != 1390464495725576304:
            return await interaction.response.send_message("❌ Canal incorrecto.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        caso_id = str(random.randint(100000, 999999))
        db = firestore.client()
        db.collection("SolicitudesAuxilio").document(caso_id).set({
            "chofer": chofer.name, "lugar": lugar, "motivo": motivo, "estado": "Pendiente", "fecha": datetime.now()
        })

        canal_dest = self.bot.get_channel(1461926580078252054)
        embed = discord.Embed(title=f"🚨 Solicitud #{caso_id}", color=discord.Color.red(), timestamp=datetime.now())
        embed.add_field(name="Chofer", value=chofer.mention, inline=True)
        embed.add_field(name="Lugar", value=lugar, inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        embed.set_image(url=foto.url)
        
        await canal_dest.send(content="<@&1390152252143964268>", embed=embed, view=AuxilioButtons(caso_id))
        await interaction.followup.send(f"✅ Caso #{caso_id} enviado.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Servicios(bot))
