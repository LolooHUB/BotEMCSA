import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from firebase_admin import firestore
import os

# --- CONFIGURACIÓN HORA ARGENTINA ---
tz_arg = timezone(timedelta(hours=-3))

class InfoUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1448477246221189234]

    @app_commands.command(name="info-user", description="Ver historial de un usuario")
    async def info_user(self, interaction: discord.Interaction, usuario: discord.Member):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)

        db = firestore.client()
        
        # Consultas a Firebase
        warns = len(db.collection("Warns").where("UsuarioID", "==", str(usuario.id)).get())
        kicked_docs = db.collection("Kicks").where("UsuarioID", "==", str(usuario.id)).get()
        kicked = "SÍ" if len(kicked_docs) > 0 else "NO"
        
        # Tiempo en el servidor (Ajustado a UTC para evitar errores de offset)
        ahora_utc = datetime.now(timezone.utc)
        tiempo_srv = ahora_utc - usuario.joined_at
        dias = tiempo_srv.days

        # Hora Argentina para el footer
        fecha_arg = datetime.now(tz_arg)
        fecha_str = fecha_arg.strftime('%d/%m/%Y %H:%M')

        # --- CREAR EMBED ---
        embed = discord.Embed(title="📊 Historial de Usuario", color=discord.Color.blue(), timestamp=fecha_arg)
        embed.set_author(name="Expreso Martín Coronado S.A.", icon_url="attachment://LogoPFP.png")
        embed.set_thumbnail(url=usuario.display_avatar.url)
        
        embed.add_field(name="👤 Usuario", value=usuario.mention, inline=False)
        embed.add_field(name="⚠️ Warns Totales", value=f"**{warns}**", inline=True)
        embed.add_field(name="👢 Kickeado anteriormente", value=f"**{kicked}**", inline=True)
        embed.add_field(name="📅 Antigüedad", value=f"**{dias} días** en el servidor", inline=False)
        
        # Imagen Banner
        embed.set_image(url="attachment://Banner.png")
        embed.set_footer(text=f"Consulta realizada por: {interaction.user.name} | {fecha_str}")

        # --- PREPARACIÓN DE ARCHIVOS ---
        file1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        file2 = discord.File("Imgs/Banner.png", filename="Banner.png")

        await interaction.response.send_message(files=[file1, file2], embed=embed)

async def setup(bot):
    await bot.add_cog(InfoUser(bot))
