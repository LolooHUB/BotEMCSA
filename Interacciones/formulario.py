import discord
from discord.ext import commands

class Formulario(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="formularios")
    async def formularios(self, ctx):
        """
        Responde al comando !formularios indicando el canal correspondiente.
        """
        # ID del Canal de Formularios: 1390152260578967558
        mensaje = "Fijate el estado de nuestros formularios de ingreso en <#1448481362779701541> 💯"
        
        try:
            # Intentamos borrar el mensaje del usuario para que el chat quede limpio
            await ctx.message.delete()
        except:
            pass

        # Enviamos la respuesta
        await ctx.send(mensaje)

async def setup(bot):
    await bot.add_cog(Formulario(bot))
