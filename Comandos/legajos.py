import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from firebase_admin import firestore
import os

# --- CONFIGURACIÓN HORA ARGENTINA ---
tz_arg = timezone(timedelta(hours=-3))

class LegajoModal(discord.ui.Modal, title='Registro de Legajo Laboral'):
    interno = discord.ui.TextInput(label='Número de Interno', placeholder='Ej: 4502', min_length=1, max_length=10)
    lineas = discord.ui.TextInput(label='Línea(s) Asignada(s)', placeholder='Ej: 194, 195, 228', min_length=1)
    # El tiempo en la empresa lo calcularemos automáticamente, pero si querés que lo editen:
    notas = discord.ui.TextInput(label='Observaciones de Legajo', style=discord.TextStyle.paragraph, required=False, placeholder='Ej: Chofer con excelente puntualidad.')

    def __init__(self, usuario, db):
        super().__init__()
        self.usuario = usuario
        self.db = db

    async def on_submit(self, interaction: discord.Interaction):
        # Calcular antigüedad automáticamente (hace cuanto está en el server)
        antiguedad = datetime.now(timezone.utc) - self.usuario.joined_at
        dias_empresa = antiguedad.days

        # Guardar/Actualizar en Firebase usando el ID como nombre de documento
        legajo_data = {
            "UsuarioID": str(self.usuario.id),
            "Nombre": self.usuario.name,
            "Interno": self.interno.value,
            "Lineas": self.lineas.value,
            "Notas": self.notas.value or "Sin observaciones.",
            "DiasEnEmpresa": dias_empresa,
            "UltimaActualizacion": datetime.now(tz_arg).strftime('%d/%m/%Y %H:%M')
        }
        
        self.db.collection("Legajos").document(str(self.usuario.id)).set(legajo_data)

        await interaction.response.send_message(f"✅ Legajo de **{self.usuario.name}** actualizado correctamente.", ephemeral=True)

class Legajos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1390152252169125992, 1445570965852520650, 1397020690435149824]

    @app_commands.command(name="editar-legajo", description="Crear o editar el legajo de un chofer")
    @app_commands.describe(usuario="Chofer al que se le asignará el legajo")
    async def editar_legajo(self, interaction: discord.Interaction, usuario: discord.Member):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("❌ No tienes permisos para editar legajos.", ephemeral=True)
        
        db = firestore.client()
        await interaction.response.send_modal(LegajoModal(usuario, db))

    @app_commands.command(name="legajo", description="Consultar el legajo de un usuario")
    @app_commands.describe(usuario="Usuario a consultar")
    async def legajo(self, interaction: discord.Interaction, usuario: discord.Member):
        db = firestore.client()
        doc_ref = db.collection("Legajos").document(str(usuario.id))
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.response.send_message(f"❌ El usuario {usuario.mention} no tiene un legajo registrado.", ephemeral=True)

        data = doc.to_dict()
        fecha_ahora = datetime.now(tz_arg)

        # --- DISEÑO DEL EMBED ---
        embed = discord.Embed(title=f"📋 Legajo Personal - {usuario.name}", color=discord.Color.blue(), timestamp=fecha_ahora)
        embed.set_author(name="La Nueva Metropol S.A. | Recursos Humanos", icon_url="attachment://LogoPFP.png")
        embed.set_thumbnail(url=usuario.display_avatar.url)
        embed.set_image(url="attachment://Banner.png")

        # Campos en Vertical
        embed.add_field(name="👤 Nombre del Chofer", value=usuario.mention, inline=False)
        embed.add_field(name="🚍 Interno Asignado", value=f"**{data['Interno']}**", inline=False)
        embed.add_field(name="🛤️ Línea(s)", value=f"**{data['Lineas']}**", inline=False)
        embed.add_field(name="📅 Antigüedad", value=f"**{data['DiasEnEmpresa']} días** en la empresa", inline=False)
        embed.add_field(name="📝 Observaciones", value=f"```\n{data['Notas']}\n```", inline=False)
        
        embed.set_footer(text=f"Última actualización: {data['UltimaActualizacion']}")

        # Archivos
        f1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        f2 = discord.File("Imgs/Banner.png", filename="Banner.png")

        await interaction.response.send_message(files=[f1, f2], embed=embed)

async def setup(bot):
    await bot.add_cog(Legajos(bot))
