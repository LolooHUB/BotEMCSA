import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from firebase_admin import firestore
import os

class DesvioModal(discord.ui.Modal, title='Informe Desvío'):
    lugar = discord.ui.TextInput(label='Lugar', placeholder='Ej: Av. General Paz y Constituyentes')
    descripcion = discord.ui.TextInput(label='Describí lo sucedido', style=discord.TextStyle.paragraph)

    def __init__(self, tipo_alerta, bot_db):
        super().__init__()
        self.tipo_alerta = tipo_alerta
        self.db = bot_db

    async def on_submit(self, interaction: discord.Interaction):
        # --- CONFIGURAR HORA ARGENTINA ---
        tz_arg = timezone(timedelta(hours=-3))
        fecha_arg = datetime.now(tz_arg).strftime('%d/%m/%Y %H:%M')
        
        # --- GUARDAR EN FIREBASE ---
        if self.db:
            try:
                self.db.collection("Desvios").add({
                    "Informante": interaction.user.name,
                    "InformanteID": str(interaction.user.id),
                    "Tipo": self.tipo_alerta,
                    "Lugar": self.lugar.value,
                    "Descripcion": self.descripcion.value,
                    "Fecha": fecha_arg
                })
            except Exception as e:
                print(f"Error al guardar desvío: {e}")

        # --- CREAR EMBED ---
        embed = discord.Embed(title="🚨 Informe Alertas", color=discord.Color.yellow())
        embed.set_author(name="La Nueva Metropol S.A.", icon_url="attachment://LogoPFP.png")
        
        # Agregamos el Banner al Embed
        embed.set_image(url="attachment://Banner.png")
        
        embed.add_field(name="Informante", value=interaction.user.mention, inline=False)
        embed.add_field(name="Tipo de Alerta", value=self.tipo_alerta, inline=False)
        embed.add_field(name="Lugar", value=self.lugar.value, inline=False)
        embed.add_field(name="Descripción", value=f"```\n{self.descripcion.value}\n```", inline=False)
        
        embed.set_footer(text=f"La Nueva Metropol S.A. | {fecha_arg} (ARG)")

        # --- PREPARACIÓN DE ARCHIVOS ---
        file1 = discord.File("Imgs/LogoPFP.png", filename="LogoPFP.png")
        file2 = discord.File("Imgs/Banner.png", filename="Banner.png")
        
        canal_cortes = interaction.guild.get_channel(1392951234796978298)
        
        if canal_cortes:
            # Enviamos ambos archivos en una lista
            await canal_cortes.send(files=[file1, file2], embed=embed)
            await interaction.response.send_message("✅ Informe enviado y guardado correctamente.", ephemeral=True)
        else:
            await interaction.response.send_message(files=[file1, file2], embed=embed, ephemeral=True)

class Desvio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles_permitidos = [1390152252169125992, 1390152252143964267, 1390152252143964266]

    @app_commands.command(name="desvio", description="Reportar un desvío o corte")
    @app_commands.choices(tipo=[
        app_commands.Choice(name="Desvio", value="Desvio"),
        app_commands.Choice(name="Corte de Calle", value="Corte de Calle"),
        app_commands.Choice(name="Otro", value="Otro")
    ])
    async def desvio(self, interaction: discord.Interaction, tipo: app_commands.Choice[str]):
        if not any(r.id in self.roles_permitidos for r in interaction.user.roles):
            return await interaction.response.send_message("❌ No tienes permiso.", ephemeral=True)
        
        db_actual = firestore.client()
        await interaction.response.send_modal(DesvioModal(tipo.value, db_actual))

async def setup(bot):
    await bot.add_cog(Desvio(bot))
