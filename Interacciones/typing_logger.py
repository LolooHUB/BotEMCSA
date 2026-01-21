import discord
from discord.ext import commands
from datetime import datetime

class TypingLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1456385261239013437

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        # Esto solo lo registra internamente para no saturar el canal, 
        # pero puedes activarlo si quieres que el bot haga algo específico.
        pass

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction, command):
        # LOGS DE TODOS LOS COMANDOS
        log_channel = interaction.guild.get_channel(self.log_channel_id)
        embed = discord.Embed(title="LOG: Comando Ejecutado", color=discord.Color.blue())
        embed.add_field(name="Usuario", value=interaction.user.name)
        embed.add_field(name="Comando", value=f"/{command.name}")
        embed.add_field(name="Canal", value=interaction.channel.name)
        embed.set_footer(text=f"ID: {interaction.user.id} | {datetime.now().strftime('%H:%M:%S')}")
        await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TypingLogger(bot))
