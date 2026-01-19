import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from firebase_admin import firestore

class InfoUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1390152252169125992, 1445570965852520650, 1397020690435149824]

    @app_commands.command(name="info-user", description="Ver historial de un usuario")
    async def info_user(self, interaction: discord.Interaction, usuario: discord.Member):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("No tienes permisos.", ephemeral=True)

        db = firestore.client()
        
        # Consultas a Firebase
        warns = len(db.collection("Warns").where("UsuarioID", "==", str(usuario.id)).get())
        kicked = "S" if len(db.collection("Kicks").where("UsuarioID", "==", str(usuario.id)).get()) > 0 else "N"
        
        # Tiempo en el servidor
        tiempo_srv = datetime.now() - usuario.joined_at.replace(tzinfo=None)
        dias = tiempo_srv.days

        embed = discord.Embed(title="📛 UserInfo", color=discord.Color.yellow())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Usuario", value=usuario.mention, inline=False)
        embed.add_field(name="Warns", value=str(warns), inline=True)
        embed.add_field(name="Ban", value="N", inline=True) # Si está en el sv, no está baneado actualmente
        embed.add_field(name="Kickeado alguna vez?", value=kicked, inline=True)
        embed.add_field(name="Tiempo en Servidor", value=f"{dias} días", inline=False)
        embed.set_footer(text=f"La Nueva Metropol S.A. | {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        embed.set_image(url="attachment://Banner.png")

        file = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        await interaction.response.send_message(file=file, embed=embed)

async def setup(bot):
    await bot.add_cog(InfoUser(bot))
