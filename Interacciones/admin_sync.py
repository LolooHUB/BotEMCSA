import discord
from discord.ext import commands
from discord import app_commands

class AdminSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.staff_role_id = 1448477246221189234

    @commands.command(name="sync")
    async def sync(self, ctx):
        # Verificación manual del rol para que sea más rápido
        if not any(role.id == self.staff_role_id for role in ctx.author.roles):
            return await ctx.send("❌ No tienes el rol de Staff necesario.")

        await ctx.send("♻️ **Sincronizando comandos...**")
        try:
            # Esto copia los comandos globales al servidor actual
            self.bot.tree.copy_global_to(guild=ctx.guild)
            # Esto los sube a Discord solo para este servidor
            synced = await self.bot.tree.sync(guild=ctx.guild)
            
            await ctx.send(f"✅ Éxito: Se sincronizaron {len(synced)} comandos en este servidor.")
            print(f"Sincronización manual realizada por {ctx.author}")
        except Exception as e:
            await ctx.send(f"❌ Error durante la sincronización: {e}")

async def setup(bot):
    await bot.add_cog(AdminSync(bot))
