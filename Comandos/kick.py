import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from firebase_admin import firestore

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1390152252169125992, 1445570965852520650, 1397020690435149824]

    @app_commands.command(name="kick", description="Kickear a un usuario del servidor")
    @app_commands.describe(usuario="Usuario a expulsar", motivo="Razón", evidencia="Prueba de la falta")
    async def kick(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str, evidencia: discord.Attachment = None):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("❌ Permisos insuficientes.", ephemeral=True)

        db = firestore.client()

        try:
            db.collection("Kicks").add({
                "UsuarioID": str(usuario.id),
                "Moderador": interaction.user.name,
                "Motivo": motivo,
                "Fecha": datetime.now()
            })

            await usuario.kick(reason=motivo)

            embed = discord.Embed(title="⛔ Usuario Kickeado", color=discord.Color.orange())
            embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
            embed.add_field(name="Usuario", value=usuario.mention, inline=False)
            embed.add_field(name="Motivo", value=motivo, inline=False)
            embed.add_field(name="Evidencia", value=evidencia.url if evidencia else "No proporcionada", inline=False)
            embed.add_field(name="Administrador", value=interaction.user.mention, inline=False)
            embed.set_footer(text=f"La Nueva Metropol S.A. | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

            channel = interaction.guild.get_channel(1397738825609904242)
            file = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
            await channel.send(file=file, embed=embed)
            
            await interaction.response.send_message(f"✅ {usuario.name} ha sido expulsado.", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Kick(bot))
