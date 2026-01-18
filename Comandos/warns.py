import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from firebase_admin import firestore
import os

class Warns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin_roles = [1390152252169125992, 1445570965852520650, 1397020690435149824]

    @app_commands.command(name="warn", description="Warnear a un usuario")
    async def warn(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("No tienes permisos.", ephemeral=True)

        # Conexión a DB
        db = firestore.client()
        warns_ref = db.collection("Warns").where("UsuarioID", "==", str(usuario.id))
        docs = warns_ref.get()
        count = len(docs) + 1

        # Guardado en Firebase
        db.collection("Warns").add({
            "UsuarioID": str(usuario.id),
            "UsuarioNombre": usuario.name,
            "Moderador": interaction.user.name,
            "Motivo": motivo,
            "Fecha": datetime.now()
        })

        # Timeout con manejo de error (por si el usuario es admin o tiene mayor rango)
        try:
            await usuario.timeout(timedelta(minutes=5), reason=f"Warn #{count}: {motivo}")
        except Exception:
            pass

        # --- CONFIGURACIÓN DE IMAGEN Y EMBED ---
        path_imagen = "Imgs/LogoPFP.png"
        
        # Verificamos si la imagen existe antes de intentar mandarla
        if not os.path.exists(path_imagen):
            return await interaction.response.send_message(f"❌ Error: No se encontró la imagen en {path_imagen}", ephemeral=True)

        # Creamos el archivo
        file = discord.File(path_imagen, filename="LogoPFP.png")

        embed = discord.Embed(title="📛 Usuario Warneado", color=discord.Color.yellow())
        
        # Para usar attachment en el author, el filename debe coincidir
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        
        # Campos en VERTICAL
        embed.add_field(name="Usuario", value=usuario.mention, inline=False)
        embed.add_field(name="Moderador", value=interaction.user.mention, inline=False)
        embed.add_field(name="Motivo", value=f"```\n{motivo}\n```", inline=False)
        embed.add_field(name="Warn N°", value=str(count), inline=False)

        embed.set_footer(text=f"La Nueva Metropol S.A. | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        # Canal de Logs
        channel = interaction.guild.get_channel(1397738825609904242)
        
        if channel:
            # Enviamos el archivo junto con el embed al canal de logs
            await channel.send(file=file, embed=embed)
            await interaction.response.send_message(f"✅ Warn aplicado a {usuario.name}.", ephemeral=True)
        else:
            # Si el canal no existe, lo mandamos como respuesta
            await interaction.response.send_message(file=file, embed=embed, ephemeral=True)

    @app_commands.command(name="clearwarnings", description="Eliminar warns de un usuario")
    async def clear(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str, cantidad: int):
        if not any(role.id in self.admin_roles for role in interaction.user.roles):
            return await interaction.response.send_message("No tienes permisos.", ephemeral=True)
        
        await interaction.response.send_message("Warnings removidos de la base de datos.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Warns(bot))
