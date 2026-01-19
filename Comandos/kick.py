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

        # 1. Configurar Hora Argentina
        fecha_ahora = datetime.now(tz_arg)
        fecha_str = fecha_ahora.strftime('%d/%m/%Y %H:%M')

        db = firestore.client()

        try:
            # 2. Guardar en Firebase con hora argentina
            db.collection("Kicks").add({
                "UsuarioID": str(usuario.id),
                "Moderador": interaction.user.name,
                "Motivo": motivo,
                "Fecha": fecha_str 
            })

            # 3. Expulsar al usuario
            await usuario.kick(reason=motivo)

            # --- DISEÑO DEL EMBED ---
            embed = discord.Embed(title="⛔ Usuario Kickeado", color=discord.Color.orange(), timestamp=fecha_ahora)
            embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
            
            embed.add_field(name="Usuario", value=usuario.mention, inline=False)
            embed.add_field(name="Motivo", value=motivo, inline=False)
            embed.add_field(name="Evidencia", value=evidencia.url if evidencia else "No proporcionada", inline=False)
            embed.add_field(name="Administrador", value=interaction.user.mention, inline=False)
            
            # Footer con hora argentina
            embed.set_footer(text=f"La Nueva Metropol S.A. | {fecha_str}")
            embed.set_image(url="attachment://Banner.png")

            # 4. Enviar a Logs
            channel = interaction.guild.get_channel(1397738825609904242)
            file = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
            
            if channel:
                await channel.send(file=file, embed=embed)
            
            await interaction.response.send_message(f"✅ {usuario.name} ha sido expulsado.", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Kick(bot))
