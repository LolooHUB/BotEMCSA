import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from firebase_admin import firestore
import os

tz_arg = timezone(timedelta(hours=-3))

class LegajoModal(discord.ui.Modal, title='Registro de Legajo Laboral'):
    interno = discord.ui.TextInput(label='Número de Interno', placeholder='Ej: 4502')
    lineas = discord.ui.TextInput(label='Línea(s) Asignada(s)', placeholder='Ej: 194, 195')
    notas = discord.ui.TextInput(label='Observaciones', style=discord.TextStyle.paragraph, required=False)
    legajo = discord.ui.TextInput(label='Número de Legajo', placeholder='Ej: 1003')
    

    def __init__(self, usuario, db):
        super().__init__()
        self.usuario = usuario
        self.db = db

    async def on_submit(self, interaction: discord.Interaction):
        # Calcular antigüedad (días en el server)
        antiguedad = datetime.now(timezone.utc) - self.usuario.joined_at
        
        # Intentar buscar si ya tiene una Licencia creada para vincular el ID
        lic_doc = self.db.collection("Licencias").document(str(self.usuario.id)).get()
        lic_id = lic_doc.to_dict().get("LicenciaID", "Sin Licencia") if lic_doc.exists else "Sin Licencia"

        data = {
            "UsuarioID": str(self.usuario.id),
            "Nombre": self.usuario.name,
            "Interno": self.interno.value,
            "Lineas": self.lineas.value,
            "Notas": self.notas.value or "Sin observaciones.",
            "DiasEnEmpresa": antiguedad.days,
            "LicenciaID": lic_id,
            "NumLegajo": self.legajo.value,
            "UltimaActualizacion": datetime.now(tz_arg).strftime('%d/%m/%Y %H:%M')
        }
        
        self.db.collection("Legajos").document(str(self.usuario.id)).set(data)
        await interaction.response.send_message(f"✅ Legajo de **{self.usuario.name}** actualizado.", ephemeral=True)

class Legajos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1448477246221189234]

    @app_commands.command(name="editar-legajo", description="Admin: Crear/Editar legajo de un usuario")
    async def editar_legajo(self, interaction: discord.Interaction, usuario: discord.Member):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        
        db = firestore.client()
        await interaction.response.send_modal(LegajoModal(usuario, db))

    @app_commands.command(name="legajo", description="Consultar legajo de un usuario")
    async def legajo(self, interaction: discord.Interaction, usuario: discord.Member):
        db = firestore.client()
        doc = db.collection("Legajos").document(str(usuario.id)).get()

        if not doc.exists:
            return await interaction.response.send_message(f"❌ {usuario.name} no tiene legajo.", ephemeral=True)

        data = doc.to_dict()
        
        embed = discord.Embed(title=f"📋 Legajo - {usuario.name}", color=discord.Color.blue(), timestamp=datetime.now(tz_arg))
        embed.set_author(name="Expreso Martín Coronado S.A. | RR.HH.", icon_url="attachment://LogoPFP.png")
        embed.set_thumbnail(url=usuario.display_avatar.url)
        embed.set_image(url="attachment://Banner.png")

        embed.add_field(name="👤 Chofer", value=usuario.mention, inline=False)
        embed.add_field(name="🚍 Interno", value=f"**{data['Interno']}**", inline=False)
        embed.add_field(name="🛤️ Líneas", value=f"**{data['Lineas']}**", inline=False)
        embed.add_field(name="🪪 N° Legajo", value=f"**{data['NumLegajo']}**", inline=False)
        embed.add_field(name="🪪 ID Licencia", value=f"**{data.get('LicenciaID', 'No tramitada')}**", inline=False)
        embed.add_field(name="📅 Antigüedad", value=f"**{data['DiasEnEmpresa']} días**", inline=False)
        embed.add_field(name="📝 Notas", value=f"```\n{data['Notas']}\n```", inline=False)
        
        embed.set_footer(text=f"Sincronizado con Base de Datos | {data['UltimaActualizacion']}")

        f1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        f2 = discord.File("Imgs/Banner.png", filename="Banner.png")

        await interaction.response.send_message(files=[f1, f2], embed=embed)

async def setup(bot):
    await bot.add_cog(Legajos(bot))
