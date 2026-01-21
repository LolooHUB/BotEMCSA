import discord
from discord.ext import commands
from discord import app_commands

class AdminSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.staff_role_id = 1448477246221189234 # Tu ID de Staff

    # Verificación personalizada para el rol de Staff
    def is_staff():
        async def predicate(ctx):
            staff_role_id = 1448477246221189234
            has_role = any(role.id == staff_role_id for role in ctx.author.roles)
            if not has_role:
                await ctx.send("❌ No tienes el rol necesario para ejecutar este comando.")
            return has_role
        return commands.check(predicate)

    @commands.command(name="sync")
    @is_staff()
    async def sync(self, ctx):
        """Limpia la caché de comandos y resincroniza todo (Solo Staff)"""
        await ctx.send("♻️ **Limpiando comandos duplicados...** esto puede tardar unos segundos.")
        try:
            # 1. Limpia los comandos del árbol interno
            self.bot.tree.clear_commands(guild=ctx.guild)
            
            # 2. Sincroniza
            await self.bot.tree.sync(guild=ctx.guild)
            await self.bot.tree.sync() # Sincronización global
            
            await ctx.send("✅ **Limpieza completada.**\n⚠️ **IMPORTANTE:** Si seguís viendo duplicados, presioná `Ctrl + R` en PC o reiniciá la app.")
        except Exception as e:
            await ctx.send(f"❌ Error durante la sincronización: {e}")

async def setup(bot):
    await bot.add_cog(AdminSync(bot))