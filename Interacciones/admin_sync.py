import discord
from discord.ext import commands

class AdminSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.staff_role_id = 1448477246221189234

    @commands.command(name="limpiar")
    async def limpiar(self, ctx):
        """Borra TODOS los comandos (Globales y Locales) para quitar duplicados"""
        if not any(role.id == self.staff_role_id for role in ctx.author.roles):
            return await ctx.send("❌ No tienes permiso.")

        await ctx.send("🧹 **Iniciando limpieza profunda...**")
        try:
            # 1. Borra comandos globales (tardan en actualizarse)
            self.bot.tree.clear_commands(guild=None)
            await self.bot.tree.sync(guild=None)

            # 2. Borra comandos de este servidor
            self.bot.tree.clear_commands(guild=ctx.guild)
            await self.bot.tree.sync(guild=ctx.guild)

            await ctx.send("✅ **Comandos borrados de la base de datos de Discord.**\nAhora usa `!fix` para cargar solo los de este servidor.")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

    @commands.command(name="fix")
    async def fix(self, ctx):
        """Carga los comandos correctamente solo en este servidor"""
        if not any(role.id == self.staff_role_id for role in ctx.author.roles):
            return await ctx.send("❌ No tienes permiso.")

        await ctx.send("⚙️ **Cargando comandos en este servidor...**")
        try:
            # Sincroniza las extensiones actuales al servidor local
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await ctx.send(f"🚀 **¡Listo!** Se activaron {len(synced)} comandos.\n*(Si ves duplicados, reinicia tu Discord con Ctrl+R)*")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

async def setup(bot):
    await bot.add_cog(AdminSync(bot))
