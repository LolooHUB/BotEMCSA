# ... (Configuración de Firebase y Bot igual que antes)

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.watching, name="Expreso Martín Coronado S.A.")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    try:
        await bot.tree.sync()
        print(f"🚀 Bot Online: {bot.user}")
    except Exception as e:
        print(f"❌ Error en Sync inicial: {e}")

async def main():
    async with bot:
        await load_extensions()
        token = os.getenv("DISCORD_TOKEN")
        if token:
            await bot.start(token)
        else:
            print("❌ ERROR: No se encontró el DISCORD_TOKEN.")

if __name__ == "__main__":
    asyncio.run(main())