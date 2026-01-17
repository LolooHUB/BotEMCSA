import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from firebase_admin import db
import os

class Servicios(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.canal_auxilio_envio = 1390464495725576304
        self.canal_auxilio_embed = 1461926580078252054
        self.rol_cliente_id = 1390152252143964262
        self.rol_auxiliar_id = 1390152252143964268
        self.path_logo = "./Imgs/LogoPFP.png"
        
        # Referencia a Colección de Auxilios
        self.db_auxilios = db.reference('SolicitudesAuxilio')

    @app_commands.command(name="auxilio", description="Solicitud de auxilio mecánico en ruta")
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        if interaction.channel_id != self.canal_auxilio_envio:
            return await interaction.response.send_message(f"❌ Solo puedes usar este comando en <#{self.canal_auxilio_envio}>", ephemeral=True)
        
        if any(role.id == self.rol_cliente_id for role in interaction.user.roles):
            return await interaction.response.send_message("❌ Los Clientes no pueden solicitar auxilio.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        # --- REGISTRO EN FIREBASE ---
        try:
            # Crear ID única para el registro
            registro_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.db_auxilios.child(registro_id).set({
                "chofer_nom": chofer.name,
                "chofer_id": chofer.id,
                "lugar": lugar,
                "motivo": motivo,
                "foto_url": foto.url,
                "solicitado_por": interaction.user.name,
                "fecha_completa": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            })
        except Exception as e:
            print(f"❌ Error al registrar auxilio: {e}")

        canal_dest = interaction.guild.get_channel(self.canal_auxilio_embed)
        file = discord.File(self.path_logo, filename="LogoPFP.png")
        
        embed = discord.Embed(title="📛 Solicitud de Auxilio", color=discord.Color.orange(), timestamp=datetime.now())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        embed.add_field(name="Chofer", value=chofer.mention, inline=True)
        embed.add_field(name="Lugar", value=lugar, inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        embed.set_image(url=foto.url)
        embed.set_footer(text=f"Registro ID: {registro_id} | La Nueva Metropol S.A.")

        mencion_aux = interaction.guild.get_role(self.rol_auxiliar_id)
        await canal_dest.send(content=mencion_aux.mention if mencion_aux else "@Auxiliares", file=file, embed=embed)
        await interaction.followup.send(f"✅ Solicitud enviada y registrada (ID: {registro_id}).", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Servicios(bot))
