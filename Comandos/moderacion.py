import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import os
import json

class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles_admin = [1390152252169125992, 1445570965852520650, 1397020690435149824]
        self.canal_sanciones_id = 1397738825609904242
        self.path_logo = "./Imgs/LogoPFP.png"
        
        # --- CONEXIÓN A FIREBASE ---
        try:
            if not firebase_admin._apps:
                fb_config = os.getenv('FIREBASE_CONFIG')
                db_url = os.getenv('FIREBASE_DB_URL')
                if fb_config and db_url:
                    cred_dict = json.loads(fb_config.strip())
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred, {'databaseURL': db_url})
                    print("✅ [Metropol] Firebase conectado en Moderación.")
        except Exception as e:
            print(f"❌ [Metropol] Error Firebase: {e}")
            
        # Referencias a Colecciones
        self.db_warns = db.reference('Warns')
        self.db_bans = db.reference('Baneos')
        self.db_kicks = db.reference('Kicks')

    def es_admin(self, interaction: discord.Interaction):
        return any(role.id in self.roles_admin for role in interaction.user.roles)

    @app_commands.command(name="ban", description="Baneo administrativo de usuarios")
    async def ban(self, interaction: discord.Interaction, usuario: discord.User, motivo: str, duracion: str, evidencia: discord.Attachment = None):
        if not self.es_admin(interaction):
            return await interaction.response.send_message("❌ No tienes rango administrativo.", ephemeral=True)
        
        try:
            await interaction.guild.ban(usuario, reason=motivo)
            
            # Guardar en Colección Baneos
            self.db_bans.push({
                "usuario_nom": usuario.name,
                "usuario_id": usuario.id,
                "motivo": motivo,
                "duracion": duracion,
                "admin": interaction.user.name,
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            })

            file = discord.File(self.path_logo, filename="LogoPFP.png")
            embed = discord.Embed(title="⛔ Usuario Baneado", color=discord.Color.red(), timestamp=datetime.now())
            embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
            embed.add_field(name="Usuario", value=usuario.mention, inline=True)
            embed.add_field(name="Motivo", value=motivo, inline=True)
            embed.add_field(name="Evidencia", value=evidencia.url if evidencia else "No proporcionada", inline=False)
            embed.set_footer(text="La Nueva Metropol S.A.")

            await interaction.guild.get_channel(self.canal_sanciones_id).send(file=file, embed=embed)
            await interaction.response.send_message(f"✅ {usuario.name} baneado y registrado.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    @app_commands.command(name="kick", description="Expulsión administrativa de usuarios")
    async def kick(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str):
        if not self.es_admin(interaction):
            return await interaction.response.send_message("❌ No tienes rango administrativo.", ephemeral=True)
        
        try:
            await usuario.kick(reason=motivo)

            # Guardar en Colección Kicks
            self.db_kicks.push({
                "usuario_nom": usuario.name,
                "usuario_id": usuario.id,
                "motivo": motivo,
                "admin": interaction.user.name,
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            })
            
            file = discord.File(self.path_logo, filename="LogoPFP.png")
            embed = discord.Embed(title="⛔ Usuario Kickeado", color=discord.Color.orange(), timestamp=datetime.now())
            embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
            embed.add_field(name="Usuario", value=usuario.mention, inline=True)
            embed.add_field(name="Motivo", value=motivo, inline=True)
            embed.set_footer(text="La Nueva Metropol S.A.")

            await interaction.guild.get_channel(self.canal_sanciones_id).send(file=file, embed=embed)
            await interaction.response.send_message(f"✅ {usuario.name} expulsado y registrado.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    @app_commands.command(name="warn", description="Advertencia + Timeout de 5 min")
    async def warn(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str):
        if not self.es_admin(interaction):
            return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        
        # Guardar en Colección Warns
        user_ref = self.db_warns.child(str(usuario.id))
        actual = user_ref.get() or 0
        nuevas = actual + 1
        user_ref.set(nuevas)

        t_msg = "⏱️ Timeout de 5m aplicado."
        try:
            await usuario.timeout(timedelta(minutes=5), reason=f"Warn automático: {motivo}")
        except:
            t_msg = "⚠️ No se pudo aplicar timeout."

        file = discord.File(self.path_logo, filename="LogoPFP.png")
        embed = discord.Embed(title="📛 Usuario Warneado", color=discord.Color.yellow(), timestamp=datetime.now())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Usuario", value=usuario.mention, inline=True)
        embed.add_field(name="Warn N°", value=f"{nuevas}", inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        embed.set_footer(text=f"La Nueva Metropol S.A. | {t_msg}")

        await interaction.guild.get_channel(self.canal_sanciones_id).send(file=file, embed=embed)
        await interaction.response.send_message(f"✅ Warn #{nuevas} aplicado.", ephemeral=True)

    @app_commands.command(name="clearwarnings", description="Remover advertencias de Firebase")
    async def clearwarnings(self, interaction: discord.Interaction, usuario: discord.Member, cant: int, motivo: str):
        if not self.es_admin(interaction):
            return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        
        user_ref = self.db_warns.child(str(usuario.id))
        actual = user_ref.get() or 0
        nuevas = max(0, actual - cant)
        user_ref.set(nuevas)

        embed = discord.Embed(title="✅ Warnings Removidas", color=discord.Color.green(), timestamp=datetime.now())
        embed.add_field(name="Usuario", value=usuario.mention, inline=True)
        embed.add_field(name="Restantes", value=f"{nuevas}", inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        
        await interaction.guild.get_channel(self.canal_sanciones_id).send(embed=embed)
        await interaction.response.send_message(f"✅ Historial de {usuario.name} actualizado.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderacion(bot))
