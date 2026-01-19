import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone

# --- CONFIGURACIÓN HORA ARGENTINA ---
tz_arg = timezone(timedelta(hours=-3))

# Canal de Solicitudes (donde se hace el ping al chofer)
CANAL_SOLICITUDES_ID = 1390464495725576304
# Canal de Mecánica (donde llega el auxilio)
CANAL_MECANICA_ID = 1461926580078252054

# --- VISTA SECUNDARIA (SOLO MECÁNICO - EPHEMERAL) ---
class AuxilioGestion(discord.ui.View):
    def __init__(self, data, original_msg):
        super().__init__(timeout=None)
        self.data = data
        self.original_msg = original_msg

    async def guardar_db(self, interaction, estado):
        db = interaction.client.db
        fecha_arg = datetime.now(tz_arg).strftime("%d/%m/%Y %H:%M:%S")
        if db:
            try:
                db.collection("Auxilios").add({
                    **self.data,
                    "mecanico": interaction.user.name,
                    "fecha": fecha_arg,
                    "estado": estado
                })
            except Exception as e: print(f"Error Firebase: {e}")

    @discord.ui.button(label="Marcar como Finalizada", style=discord.ButtonStyle.success, emoji="✅")
    async def finalizar_op(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.guardar_db(interaction, "Completado")
        
        embed = self.original_msg.embeds[0]
        embed.title = "✅ AUXILIO FINALIZADO"
        embed.color = discord.Color.green()
        embed.add_field(name="🏁 Resultado", value=f"Finalizado por {interaction.user.mention}", inline=False)
        
        await self.original_msg.edit(embed=embed, view=None)
        await interaction.response.send_message("📥 Registro guardado como Finalizado.", ephemeral=True)

    @discord.ui.button(label="No se encontró la alerta", style=discord.ButtonStyle.secondary, emoji="🔍")
    async def no_encontrado_op(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.guardar_db(interaction, "No Encontrado")
        
        embed = self.original_msg.embeds[0]
        embed.title = "⚠️ AUXILIO SIN RESULTADO"
        embed.color = discord.Color.light_grey()
        embed.add_field(name="🏁 Resultado", value=f"El mecánico {interaction.user.mention} no encontró la unidad.", inline=False)
        
        await self.original_msg.edit(embed=embed, view=None)
        await interaction.response.send_message("📥 Registro guardado como No Encontrado.", ephemeral=True)

# --- VISTA PRINCIPAL (CANAL MECÁNICA) ---
class AuxilioButtons(discord.ui.View):
    def __init__(self, chofer, lugar, motivo):
        super().__init__(timeout=None)
        self.chofer = chofer # Objeto Member para el ping
        self.data = {
            "chofer_id": str(chofer.id),
            "chofer_nombre": chofer.name,
            "lugar": lugar,
            "motivo": motivo
        }

    @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.success, emoji="🛠️")
    async def aceptar(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. Avisar al chofer en el canal de solicitudes
        canal_solicitudes = interaction.guild.get_channel(CANAL_SOLICITUDES_ID)
        if canal_solicitudes:
            await canal_solicitudes.send(f"{self.chofer.mention} **¡Un Auxiliar va en camino!** 🚛")

        # 2. Bloquear botones y actualizar embed de mecánica
        for child in self.children:
            child.disabled = True
        
        embed = interaction.message.embeds[0]
        embed.title = "🛠️ AUXILIO EN PROCESO"
        embed.color = discord.Color.blue()
        embed.add_field(name="👨‍🔧 Mecánico a cargo", value=interaction.user.mention, inline=False)
        
        await interaction.message.edit(embed=embed, view=self)
        
        # 3. Enviar menú secreto al mecánico
        view_gestion = AuxilioGestion(self.data, interaction.message)
        await interaction.response.send_message("Menú de gestión final:", view=view_gestion, ephemeral=True)

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.danger, emoji="✖️")
    async def rechazar(self, interaction: discord.Interaction, button: discord.ui.Button):
        db = interaction.client.db
        fecha_arg = datetime.now(tz_arg).strftime("%d/%m/%Y %H:%M:%S")
        
        if db:
            db.collection("Auxilios").add({**self.data, "mecanico": interaction.user.name, "fecha": fecha_arg, "estado": "Rechazado"})

        embed = interaction.message.embeds[0]
        embed.title = "❌ AUXILIO RECHAZADO"
        embed.color = discord.Color.red()
        
        await interaction.message.edit(embed=embed, view=None)
        await interaction.response.send_message(f"Auxilio rechazado.", ephemeral=True)

# --- COMANDO ---
class Auxiliar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="auxilio", description="Solicitar asistencia mecánica")
    async def auxilio(self, interaction: discord.Interaction, chofer: discord.Member, lugar: str, motivo: str, foto: discord.Attachment):
        if interaction.channel_id != CANAL_SOLICITUDES_ID:
            return await interaction.response.send_message(f"❌ Solo en <#{CANAL_SOLICITUDES_ID}>.", ephemeral=True)

        ahora_arg = datetime.now(tz_arg)
        embed = discord.Embed(title="📛 SOLICITUD DE ASISTENCIA", color=discord.Color.orange(), timestamp=ahora_arg)
        embed.set_author(name="La Nueva Metropol S.A.", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.add_field(name="👤 Chofer", value=chofer.mention, inline=True)
        embed.add_field(name="📍 Lugar", value=lugar, inline=True)
        embed.add_field(name="🛠️ Motivo", value=f"```\n{motivo}\n```", inline=False)
        if foto: embed.set_image(url=foto.url)
        embed.set_footer(text=f"Solicitado por: {interaction.user.name}")
        

        canal_destino = interaction.guild.get_channel(CANAL_MECANICA_ID)
        if canal_destino:
            # Enviamos el objeto 'chofer' completo para poder hacerle el ping luego
            view = AuxilioButtons(chofer, lugar, motivo)
            await canal_destino.send(content="<@&1390152252143964268> ⚠️ **NUEVA SOLICITUD**", embed=embed, view=view)
            await interaction.response.send_message("✅ Tu solicitud ha sido enviada a los mecánicos.", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Auxiliar(bot))
