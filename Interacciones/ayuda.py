import discord
from discord.ext import commands

class Ayuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ayuda")
    async def ayuda(self, ctx):
        mensaje = (
            "Si queres obtener informacion acerca de los formularios ejecuta `!formularios` 🔰\n"
            "¿Queres hablar con el staff?, podes abrir un ticket en <#1390152260578967559>"
        )
        await ctx.send(mensaje, delete_after=30) # Ephemeral simulado para prefix

    @commands.command(name="formularios")
    async def formularios(self, ctx):
        await ctx.send("Fijate el estado de nuestros formularios de ingreso en <#1390152260578967558> 💯")

async def setup(bot):
    await bot.add_cog(Ayuda(bot))
