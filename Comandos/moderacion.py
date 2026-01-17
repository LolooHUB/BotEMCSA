import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles_admin = [1390152252169125992, 1445570965852520650, 1397020690435149824]
        self.canal_sanciones_id = 1397738825609904242
        self.canal_logs_id = 1390152261937922070
        self.path_logo = "./Imgs/LogoPFP.png"
        
        # Conexión a Firestore
        if not firebase_admin._apps:
            fb_config = os.getenv('FIREBASE_CONFIG')
            if fb_config:
                cred = credentials.Certificate(json.loads(fb_config.strip()))
                firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    async def enviar_log_central(self, titulo, descripcion, color=discord.Color.blue()):
        canal = self.bot.get_channel(self.canal_logs_id)
        if canal:
            embed = discord.Embed(title=f"⚖️ Auditoría: {titulo}", description=descripcion, color=color, timestamp=datetime.now())
            await canal.send(embed=embed)

    def es_admin(self, interaction: discord.Interaction):
        return any(role.id in self.roles_admin for role in interaction.user.roles)

    @app_commands.command(name="ver-warns", description="Ver el historial de advertencias de un chofer")
    async def ver_warns(self, interaction: discord.Interaction, usuario: discord.User):
        doc = self.db.collection("Warns").document(str(usuario.id)).get()
        if doc.exists:
            datos = doc.to_dict()
            await interaction.response.send_message(f"👤 **Chofer:** {usuario.mention}\n⚠️ **Warns Totales:** `{datos.get('cantidad', 0)}` \n📝 **Último motivo:** {datos.get('ultimo_motivo', 'N/A')}", ephemeral=True)
        else:
            await interaction.response.send_message(f"✅ {usuario.mention} no tiene advertencias registradas.", ephemeral=True)

    @app_commands.command(name="ban", description="Baneo administrativo de usuarios")
    async def ban(self, interaction: discord.Interaction, usuario: discord.User, motivo: str, duracion: str, evidencia: discord.Attachment = None):
        if not self.es_admin(interaction): return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        
        try:
            await interaction.guild.ban(usuario, reason=f"Admin: {interaction.user.name} | Motivo: {motivo}")
            self.db.collection("Baneos").add({
                "usuario": usuario.name, "id": str(usuario.id), "motivo": motivo,
                "admin": interaction.user.name, "fecha": datetime.now()
            })

            file = discord.File(self.path_logo, filename="LogoPFP.png")
            embed = discord.Embed(title="⛔ Usuario Baneado", color=discord.Color.red(), timestamp=datetime.now())
            embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
            embed.add_field(name="Usuario", value=usuario.mention, inline=True)
            embed.add_field(name="Motivo", value=motivo, inline=True)
            embed.add_field(name="Duración", value=duracion, inline=True)
            embed.add_field(name="Evidencia", value=evidencia.url if evidencia else "No proporcionada", inline=False)
            embed.set_footer(text="La Nueva Metropol S.A.")

            await interaction.guild.get_channel(self.canal_sanciones_id).send(file=file, embed=embed)
            await self.enviar_log_central("Usuario Baneado", f"Admin: {interaction.user.name}\nSancionado: {usuario.name}\nMotivo: {motivo}", discord.Color.red())
            await interaction.response.send_message(f"✅ {usuario.name} ha sido baneado.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    @app_commands.command(name="kick", description="Expulsión administrativa de usuarios")
    async def kick(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str):
        if not self.es_admin(interaction): return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        
        try:
            await usuario.kick(reason=motivo)
            self.db.collection("Kicks").add({
                "usuario": usuario.name, "id": str(usuario.id), "motivo": motivo,
                "admin": interaction.user.name, "fecha": datetime.now()
            })

            file = discord.File(self.path_logo, filename="LogoPFP.png")
            embed = discord.Embed(title="⛔ Usuario Kickeado", color=discord.Color.orange(), timestamp=datetime.now())
            embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
            embed.add_field(name="Usuario", value=usuario.mention, inline=True)
            embed.add_field(name="Motivo", value=motivo, inline=True)
            embed.set_footer(text="La Nueva Metropol S.A.")

            await interaction.guild.get_channel(self.canal_sanciones_id).send(file=file, embed=embed)
            await self.enviar_log_central("Usuario Kickeado", f"Admin: {interaction.user.name}\nSancionado: {usuario.name}", discord.Color.orange())
            await interaction.response.send_message(f"✅ {usuario.name} ha sido expulsado.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    @app_commands.command(name="warn", description="Advertencia + Timeout de 5 min")
    async def warn(self, interaction: discord.Interaction, usuario: discord.Member, motivo: str):
        if not self.es_admin(interaction): return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        
        user_ref = self.db.collection("Warns").document(str(usuario.id))
        doc = user_ref.get()
        nuevas = (doc.to_dict().get("cantidad", 0) + 1) if doc.exists else 1
        user_ref.set({"cantidad": nuevas, "usuario": usuario.name, "ultimo_motivo": motivo})

        t_msg = "⏱️ Timeout de 5m aplicado."
        try: await usuario.timeout(timedelta(minutes=5), reason=f"Warn: {motivo}")
        except: t_msg = "⚠️ No se pudo aplicar timeout."

        file = discord.File(self.path_logo, filename="LogoPFP.png")
        embed = discord.Embed(title="📛 Usuario Warneado", color=discord.Color.yellow(), timestamp=datetime.now())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Usuario", value=usuario.mention, inline=True)
        embed.add_field(name="Warn N°", value=f"{nuevas}", inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        embed.set_footer(text=f"La Nueva Metropol S.A. | {t_msg}")

        await interaction.guild.get_channel(self.canal_sanciones_id).send(file=file, embed=embed)
        await self.enviar_log_central("Warn Aplicado", f"Admin: {interaction.user.name}\nChofer: {usuario.name}\nWarn N°: {nuevas}", discord.Color.yellow())
        await interaction.response.send_message(f"✅ Warn aplicado.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderacion(bot))
