import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from firebase_admin import firestore
import os

tz_arg = timezone(timedelta(hours=-3))

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1390152252169125992, 1445570965852520650, 1397020690435149824]

    @app_commands.command(name="ban", description="Banear a un usuario de La Nueva Metropol S.A.")
    @app_commands.describe(usuario="Usuario a banear", motivo="Razón", duracion="Tiempo", evidencia="Prueba")
    async def ban(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str, duracion: str, evidencia: discord.Attachment = None):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)

        fecha_ahora = datetime.now(tz_arg)
        fecha_str = fecha_ahora.strftime('%d/%m/%Y %H:%M')
        db = firestore.client()
        
        try:
            # Guardar en Firebase
            db.collection("Baneos").add({
                "Usuario": usuario.name, "UsuarioID": str(usuario.id),
                "Moderador": interaction.user.name, "Fecha": fecha_str,
                "Motivo": motivo, "Duracion": duracion
            })

            await usuario.ban(reason=motivo)

            # --- PREPARACIÓN DE ARCHIVOS ---
            file_logo = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
            file_banner = discord.File("Imgs/Banner.png", filename="Banner.png")

            # --- EMBED PARA CANAL PÚBLICO (SANCIONES) ---
            embed_pub = discord.Embed(title="⛔ Usuario Baneado", color=discord.Color.red(), timestamp=fecha_ahora)
            embed_pub.set_author(name="Expreso Martín Coronado S.A.", icon_url="attachment://LogoPFP.png")
            embed_pub.set_image(url="attachment://Banner.png") # Banner para el público
            embed_pub.add_field(name="Usuario", value=usuario.mention, inline=False)
            embed_pub.add_field(name="Motivo", value=f"```\n{motivo}\n```", inline=False)
            embed_pub.add_field(name="Duración", value=duracion, inline=False)
            embed_pub.set_footer(text=f"Expreso Martín Coronado S.A. | {fecha_str}")

            # --- EMBED PARA LOGS (CON EVIDENCIA) ---
            embed_log = embed_pub.copy()
            embed_log.set_image(url=evidencia.url if evidencia else None) # Evidencia para logs
            embed_log.add_field(name="Administrador", value=interaction.user.mention, inline=False)

            # --- ENVÍO A CANALES ---
            canal_sanciones = interaction.guild.get_channel(1397738825609904242) # Ajustar ID si es distinto
            
            # Mandar al canal con BANNER
            if canal_sanciones:
                # Reiniciamos los archivos para el segundo envío
                f1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
                f2 = discord.File("Imgs/Banner.png", filename="Banner.png")
                await canal_sanciones.send(files=[f1, f2], embed=embed_pub)

            await interaction.response.send_message(f"✅ Se ha baneado a {usuario.name} correctamente.", ephemeral=True)

        except discord.Forbidden:
            await interaction.response.send_message("❌ No tengo permisos para banear a este usuario.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ban(bot))
