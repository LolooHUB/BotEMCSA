import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from firebase_admin import firestore

# --- VISTA DE BOTONES PARA AUXILIARES ---
class AuxilioButtons(discord.ui.View):
    def __init__(self, chofer, lugar):
        super().__init__(timeout=None) # Los botones serán persistentes
        self.chofer = chofer
        self.lugar = lugar

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.orange, emoji="🚛")
    async def en_camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.chofer.send(f"✅ ¡Atención! Un Auxiliar de **La Nueva Metropol** va en camino a tu ubicación: **{self.lugar}**.")
        except:
            pass # Si el chofer tiene MD cerrados
        await interaction.response.send_message(f"Has marcado que vas en camino para asistir a {self.chofer.name}.", ephemeral=True)

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.green, emoji="✅")
    async def finalizado(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Registro en Firebase
        try:
            db = firestore.client()
            db.collection("Auxilios").add({
                "Chofer": self.chofer.name,
                "Auxiliar": interaction.user.name,
                "Lugar": self.lugar,
                "Fecha": datetime.now()
            })
        except Exception as e:
            print(f"Error Firebase: {e}")

        await interaction.response.send_message(f"Auxilio en {self.lugar} finalizado y registrado en base de datos.", ephemeral=True)
        # Desactivar botones y limpiar
        self.stop()
        await interaction.message.delete()

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red, emoji="🛑")
    async def rechazar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Avisar al chofer del rechazo
        try:
            await self.chofer.send(f"❌ Tu solicitud de auxilio en **{self.lugar}** ha sido rechazada por el personal de mantenimiento.")
        except:
            pass
        await interaction.response.send_message("Solicitud rechazada correctamente.", ephemeral=True)
        await interaction.message.delete()

# --- CLASE DEL COMANDO ---
class Auxiliar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="auxilio", description="Solicitar auxilio mecánico a la central")
    @app_commands.describe(
        chofer="Usuario del chofer que solicita",
        lugar="Lugar exacto del incidente",
        motivo="Descripción de la falla",
        foto="Imagen de la unidad o del lugar"
    )
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        # ID Canal Solicitud: 1390464495725576304
        if interaction.channel_id != 1390464495725576304:
            return await interaction.response.send_message("❌ Este comando solo funciona en el canal <#1390464495725576304>.", ephemeral=True)

        # Verificar que el ejecutor no sea Cliente (Rol: 1390152252143964262)
        if any(r.id == 1390152252143964262 for r in interaction.user.roles):
            return await interaction.response.send_message("❌ Los Clientes no tienen permiso para solicitar auxilio mecánico.", ephemeral=True)

        # Crear Embed del reporte
        embed = discord.Embed(title="📛 Solicitud de Auxilio", color=discord.Color.orange())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        
        embed.add_field(name="👤 Chofer", value=chofer.mention, inline=True)
        embed.add_field(name="📍 Lugar", value=lugar, inline=True)
        embed.add_field(name="🛠️ Motivo", value=motivo, inline=False)
        
        if foto:
            embed.set_image(url=foto.url)
            
        embed.set_footer(text=f"La Nueva Metropol S.A. | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        # ID Canal Destino (EMBED AUXILIO): 1461926580078252054
        canal_destino = interaction.guild.get_channel(1461926580078252054)
        file = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        
        # Ping al rol Auxiliar: 1390152252143964268
        view = AuxilioButtons(chofer, lugar)
        await canal_destino.send(content="<@&1390152252143964268> ⚠️ **NUEVA SOLICITUD**", file=file, embed=embed, view=view)
        
        await interaction.response.send_message("✅ Solicitud enviada a la central de auxiliares.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Auxiliar(bot))
