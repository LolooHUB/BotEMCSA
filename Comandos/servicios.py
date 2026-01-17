import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import random
from firebase_admin import firestore

class ViewAuxilio(discord.ui.View):
    def __init__(self, caso_id, db):
        super().__init__(timeout=None)
        self.caso_id = caso_id
        self.db = db
        self.path_logo = "./Imgs/LogoPFP.png"

    async def procesar_cambio(self, interaction, estado, color, emoji):
        auxiliar = interaction.user.mention if estado != "Rechazado" else "N/A"
        
        # Guardar en Firestore
        self.db.collection("SolicitudesAuxilio").document(self.caso_id).update({
            "estado": estado,
            "auxiliar_a_cargo": interaction.user.name
        })

        # Embed de Respuesta (El que aparece al clickear)
        file = discord.File(self.path_logo, filename="LogoPFP.png")
        embed = discord.Embed(title=f"{emoji} Actualización de Caso", color=color, timestamp=datetime.now())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Caso N°", value=f"`{self.caso_id}`", inline=True)
        embed.add_field(name="Estado", value=f"**{estado}**", inline=True)
        embed.add_field(name="Auxiliar a cargo", value=auxiliar, inline=False)
        embed.set_footer(text="Sistema de Emergencias Metropol")

        # Quitar botones si terminó o se rechazó
        view_actualizada = None if estado in ["Finalizado", "Rechazado"] else self
        await interaction.response.edit_message(attachments=[file], embed=embed, view=view_actualizada)

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.orange, emoji="🚨")
    async def camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.procesar_cambio(interaction, "En Camino", discord.Color.orange(), "🚑")

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.green, emoji="✅")
    async def fin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.procesar_cambio(interaction, "Finalizado", discord.Color.green(), "✅")

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red, emoji="✖️")
    async def rechazo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.procesar_cambio(interaction, "Rechazado", discord.Color.red(), "❌")

class Servicios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.canal_envio = 1390464495725576304
        self.canal_embed = 1461926580078252054
        self.rol_cliente_id = 1390152252143964262
        self.rol_auxiliar_id = 1390152252143964268
        self.path_logo = "./Imgs/LogoPFP.png"
        self.db = firestore.client()

    @app_commands.command(name="auxilio", description="Solicitud de auxilio mecánico en ruta")
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        if interaction.channel_id != self.canal_envio:
            return await interaction.response.send_message(f"❌ Solo en <#{self.canal_envio}>", ephemeral=True)
        
        if any(role.id == self.rol_cliente_id for role in interaction.user.roles):
            return await interaction.response.send_message("❌ Clientes no autorizados.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        caso_id = str(random.randint(1000000, 9999999))

        # Registro inicial en Firestore
        self.db.collection("SolicitudesAuxilio").document(caso_id).set({
            "chofer": chofer.name, "lugar": lugar, "motivo": motivo, "estado": "Pendiente", "fecha": datetime.now()
        })

        canal_dest = interaction.guild.get_channel(self.canal_embed)
        file = discord.File(self.path_logo, filename="LogoPFP.png")
        
        # El Embed original que todos ven
        embed = discord.Embed(title=f"📛 Solicitud de Auxilio N° {caso_id}", color=discord.Color.orange(), timestamp=datetime.now())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Chofer", value=chofer.mention, inline=True)
        embed.add_field(name="Lugar", value=lugar, inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        embed.set_image(url=foto.url)
        embed.set_footer(text=f"ID Caso: {caso_id} | La Nueva Metropol S.A.")

        mencion_aux = interaction.guild.get_role(self.rol_auxiliar_id)
        await canal_dest.send(content=mencion_aux.mention if mencion_aux else "@Auxiliares", file=file, embed=embed, view=ViewAuxilio(caso_id, self.db))
        await interaction.followup.send(f"✅ Solicitud #{caso_id} enviada correctamente.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Servicios(bot))
