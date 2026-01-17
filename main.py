import discord
from discord.ext import commands
import os

class MetropolBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        # Objeto del servidor Metropol
        self.GUILD_ID = discord.Object(id=1390152252143964260)

    async def setup_hook(self):
        # Intentar cargar extensiones
        for ext in ['Comandos.moderacion', 'Comandos.servicios']:
            try:
                await self.load_extension(ext)
                print(f"✅ {ext} cargado.")
            except Exception as e:
                print(f"❌ No se pudo cargar {ext}: {e}")

    async def on_ready(self):
        print(f"--- 🤖 ONLINE: {self.user.name} ---")
        # Sincronización automática
        try:
            self.tree.copy_global_to(guild=self.GUILD_ID)
            await self.tree.sync(guild=self.GUILD_ID)
            print("🚀 ÉXITO: Comandos sincronizados.")
        except discord.errors.Forbidden:
            print("❌ ERROR 403: Todavía no has entrado al link para autorizar 'applications.commands'.")

bot = MetropolBot()

@bot.event
async def on_message(message):
    if message.author.bot: return

    # Si pones !test y responde, el bot está bien configurado
    if message.content.lower() == "!test":
        await message.reply("✅ El bot está vivo. Si no ves los '/', usá el link de arriba.")

    # Sincronización manual solo si eres Admin
    if message.content.lower() == "!fuerza":
        if message.author.guild_permissions.administrator:
            try:
                await bot.tree.sync(guild=discord.Object(id=1390152252143964260))
                await message.channel.send("⚡ Sincronización manual enviada. Reiniciá Discord con Ctrl+R.")
            except Exception as e:
                await message.channel.send(f"⚠️ Error: {e}")

    await bot.process_commands(message)

# Comandos de prefijo (Siempre funcionan)
@bot.command()
async def ayuda(ctx):
    await ctx.send("📖 **Metropol:**\n`/auxilio` - Pedir mecánica.\n`!formularios` - Enlaces.")

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
