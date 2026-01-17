import discord
from discord.ext import commands
import os

class MetropolBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.GUILD_ID = discord.Object(id=1390152252143964260)

    async def setup_hook(self):
        print("--- 🛠️ Buscando archivos en carpeta Comandos ---")
        # Lista de archivos a cargar (Asegúrate de que se llamen así)
        extensiones = ['Comandos.moderacion', 'Comandos.servicios']
        
        for ext in extensiones:
            try:
                await self.load_extension(ext)
                print(f"✅ Cargado exitosamente: {ext}")
            except Exception as e:
                print(f"❌ No se pudo cargar {ext}. Error: {e}")

    async def on_ready(self):
        print(f"--- 🤖 BOT ONLINE: {self.user.name} ---")
        try:
            # Sincronizamos los comandos del árbol (tree) con el servidor
            self.tree.copy_global_to(guild=self.GUILD_ID)
            await self.tree.sync(guild=self.GUILD_ID)
            print("🚀 ÉXITO: Los comandos '/' fueron enviados al servidor.")
        except Exception as e:
            print(f"❌ Error al sincronizar con Discord: {e}")

bot = MetropolBot()

@bot.command()
async def test(ctx):
    await ctx.send("✅ ¡Bot escuchando! Si no ves los comandos '/', reiniciá Discord con Ctrl+R.")

@bot.command()
async def fuerza(ctx):
    if ctx.author.guild_permissions.administrator:
        try:
            await bot.tree.sync(guild=discord.Object(id=1390152252143964260))
            await ctx.send("⚡ Sincronización manual completada.")
        except Exception as e:
            await ctx.send(f"⚠️ Error: {e}")

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
