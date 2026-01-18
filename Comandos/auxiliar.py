import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

class AuxilioButtons(discord.ui.View):
    def __init__(self, chofer_id, lugar):
        super().__init__(timeout=None)
        self.chofer_id = chofer_id
        self.lugar = lugar

    @discord.ui.button(label="En Camino", style=discord.ButtonStyle.primary, emoji="🚛")
    async def en_camino(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Asistencia marcada en camino.", ephemeral=True)

    @discord.ui.button(label="Finalizado", style=discord.ButtonStyle.success, emoji="✅")
    async def finalizado(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Auxilio finalizado.", ephemeral=True)
        await interaction.message.delete()

class Auxiliar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="auxilio", description="Solicitar auxilio mecánico")
    @app_commands.describe(
        chofer="El chofer que necesita ayuda",
        lugar="¿Dónde estás?",
        motivo="¿Qué pasó?",
        foto="Foto de la unidad"
    )
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        # ID CANAL SOLICITUD (Donde se escribe el comando)
        if interaction.channel_id != 1390464495725576304:
            return await interaction.response.send_message("❌ Usa este comando en el canal de auxilios.", ephemeral=True)

        # Crear el aviso para los mecánicos
        embed = discord.Embed(title="📛 Solicitud de Auxilio", color=discord.Color.orange())
        embed.add_field(name="Chofer", value=chofer.mention, inline=True)
        embed.add_field(name="Lugar", value=lugar, inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        
        if foto:
            embed.set_image(url=foto.url)
            
        embed.set_footer(text=f"Metropol S.A. | {datetime.now().strftime('%H:%M')}")

        # ID CANAL DESTINO (Donde llega el mensaje a los mecánicos)
        canal_destino = interaction.guild.get_channel(1461926580078252054)
        
        if canal_destino:
            view = AuxilioButtons(chofer.id, lugar)
            # Rol Auxiliar para el ping: 1390152252143964268
            await canal_destino.send(content="<@&1390152252143964268> ⚠️ **NUEVA SOLICITUD DE ASISTENCIA**", embed=embed, view=view)
            await interaction.response.send_message("✅ Solicitud enviada a la central.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Error: No se encontró el canal de destino.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Auxiliar(bot))
