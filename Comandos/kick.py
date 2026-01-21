import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from firebase_admin import firestore
import os

# --- CONFIGURACIÓN HORA ARGENTINA ---
tz_arg = timezone(timedelta(hours=-3))

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1390152252169125992, 1445570965852520650, 1397020690435149824]

    @app_commands.command(name="kick", description="Kickear a un usuario del servidor")
    @app_commands.describe(usuario="Usuario a expulsar", motivo="Razón", evidencia="Prueba de la falta")
    async def kick(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str, evidencia: discord.Attachment = None):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("❌ Permisos insuficientes.", ephemeral=True)

        fecha_ahora = datetime.now(tz_arg)
        fecha_str = fecha_ahora.strftime('%d/%m/%Y %H:%M')
        db = firestore.client()

        try:
            # 1. Guardar en Firebase
            db.collection("Kicks").add({
                "UsuarioID": str(usuario.id),
                "Moderador": interaction.user.name,
                "Motivo": motivo,
                "Fecha": fecha_str 
            })

            # 2. Expulsar al usuario
            await usuario.kick(reason=motivo)

            # --- EMBED BASE ---
            embed = discord.Embed(title="⛔ Usuario Kickeado", color=discord.Color.orange(), timestamp=fecha_ahora)
            embed.set_author(name="Expreso Martín Coronado S.A.", icon_url="attachment://LogoPFP.png")
            embed.add_field(name="Usuario", value=usuario.mention, inline=False)
            embed.add_field(name="Motivo", value=f"```\n{motivo}\n```", inline=False)
            embed.add_field(name="Administrador", value=interaction.user.mention, inline=False)
            embed.set_footer(text=f"Expreso Martín Coronado S.A. | {fecha_str}")

            # --- ENVÍO A CANAL PÚBLICO (CON BANNER) ---
            canal_sanciones = interaction.guild.get_channel(1397738825609904242)
            if canal_sanciones:
                embed_pub = embed.copy()
                embed_pub.set_image(url="attachment://Banner.png")
                # Archivos para el canal público
                f1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
                f2 = discord.File("Imgs/Banner.png", filename="Banner.png")
                await canal_sanciones.send(files=[f1, f2], embed=embed_pub)

            # --- ENVÍO A LOGS (CON EVIDENCIA) ---
            # Si tenés un canal de logs diferente, poné el ID acá. 
            # Si usás el mismo, podés omitir este paso o mandarlo al mismo canal con la foto.
            canal_logs = interaction.guild.get_channel(1397738825609904242) # Usando el mismo ID de tu código
            if canal_logs and evidencia:
                embed_log = embed.copy()
                embed_log.set_image(url=evidencia.url)
                embed_log.title = "📂 Log de Evidencia - Kick"
                f3 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
                await canal_logs.send(file=f3, embed=embed_log)

            await interaction.response.send_message(f"✅ {usuario.name} ha sido expulsado.", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Kick(bot))
