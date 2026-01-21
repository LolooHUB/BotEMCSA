import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from firebase_admin import firestore
import random
import os

# --- CONFIGURACIÓN HORA ARGENTINA ---
tz_arg = timezone(timedelta(hours=-3))

class LicenciaModal(discord.ui.Modal, title='Registro de Licencia Habilitante'):
    nombre_juego = discord.ui.TextInput(label='Nombre en el Juego (Nick)', placeholder='Ej: Milanesa', min_length=3)
    id_jugador = discord.ui.TextInput(label='ID de Jugador (Juego)', placeholder='Ej: 987654', min_length=1)
    exp_previa = discord.ui.TextInput(label='Empresa Anterior (Opcional)', placeholder='Ej: Línea 60 / Ninguna', required=False)

    def __init__(self, db):
        super().__init__()
        self.db = db

    async def on_submit(self, interaction: discord.Interaction):
        # Generar un ID de Licencia único
        lic_id = f"LNM-{random.randint(1000, 9999)}"
        fecha_emision = datetime.now(tz_arg).strftime('%d/%m/%Y')

        data = {
            "UsuarioID": str(interaction.user.id),
            "LicenciaID": lic_id,
            "Nick": self.nombre_juego.value,
            "ID_Juego": self.id_jugador.value,
            "Experiencia": self.exp_previa.value or "Sin experiencia",
            "FechaEmision": fecha_emision
        }

        # 1. Guardar en la colección Licencias
        self.db.collection("Licencias").document(str(interaction.user.id)).set(data)

        # 2. Vincular con el Legajo automáticamente si ya existe
        legajo_ref = self.db.collection("Legajos").document(str(interaction.user.id))
        if legajo_ref.get().exists:
            legajo_ref.update({"LicenciaID": lic_id})

        await interaction.response.send_message(f"✅ ¡Licencia tramitada! Tu ID es: **{lic_id}**. Ya podés consultar tu `/legajo`.", ephemeral=True)

class Licencia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="licencia", description="Crea o muestra tu licencia de conducir")
    async def licencia(self, interaction: discord.Interaction):
        db = firestore.client()
        doc_ref = db.collection("Licencias").document(str(interaction.user.id))
        doc = doc_ref.get()

        # Si NO tiene licencia, abrir Modal
        if not doc.exists:
            return await interaction.response.send_modal(LicenciaModal(db))

        # Si TIENE licencia, mostrarla
        data = doc.to_dict()
        
        embed = discord.Embed(title="🪪 LICENCIA DE MANEJO", color=discord.Color.green(), timestamp=datetime.now(tz_arg))
        embed.set_author(name="Expreso Martín Coronado S.A.", icon_url="attachment://LogoPFP.png")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_image(url="attachment://Banner.png")

        embed.add_field(name="🏷️ Titular", value=interaction.user.mention, inline=False)
        embed.add_field(name="🆔 ID Licencia", value=f"**{data['LicenciaID']}**", inline=False)
        embed.add_field(name="🎮 Nick en Juego", value=f"**{data['Nick']}**", inline=False)
        embed.add_field(name="🔢 ID de Jugador", value=f"**{data['ID_Juego']}**", inline=False)
        embed.add_field(name="📅 Fecha de Emisión", value=data['FechaEmision'], inline=False)

        embed.set_footer(text="Documento oficial de Expreso Martín Coronado S.A.")

        f1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        f2 = discord.File("Imgs/Banner.png", filename="Banner.png")

        await interaction.response.send_message(files=[f1, f2], embed=embed)

async def setup(bot):
    await bot.add_cog(Licencia(bot))
