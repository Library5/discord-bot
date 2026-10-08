import discord
from discord.ext import commands
import os
from config import TOKEN, PREFIX
import asyncio

# إعداد الـ Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True

# إنشاء البوت
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# متغير لتخزين حالة البوت الحالية
bot.current_status = "Online 🟢"

@bot.event
async def on_ready():
    """عند جاهزية البوت"""
    print(f"✅ تم تسجيل الدخول باسم: {bot.user}")
    print(f"🤖 البوت جاهز للعمل!")
    print(f"📊 عدد السيرفرات: {len(bot.guilds)}")
    print(f"👥 عدد المستخدمين: {sum(g.member_count for g in bot.guilds)}")
    
    # تعيين الحالة الأولية
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"{PREFIX}help"
        )
    )

@bot.event
async def on_command_error(ctx, error):
    """معالج أخطاء الأوامر"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ استخدم الأمر بشكل صحيح! اكتب `{PREFIX}help`")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("❌ ليس لديك الصلاحية لاستخدام هذا الأمر!")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(f"❌ خطأ: {str(error)}")
        await ctx.send(f"❌ حدث خطأ: {str(error)}")

@bot.command(name='help')
async def help_command(ctx, cmd=None):
    """أمر المساعدة"""
    if cmd is None:
        embed = discord.Embed(
            title="📚 قائمة الأوامر",
            description="استخدم `!help <اسم_الأمر>` للحصول على تفاصيل",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🛡️ أوامر إدارية",
            value="`kick` | `ban` | `mute` | `unmute` | `clear`",
            inline=False
        )
        
        embed.add_field(
            name="🎉 أوامر جيفاوي",
            value="`giveaway` | `endgiveaway`",
            inline=False
        )
        
        embed.add_field(
            name="👑 أوامر خاصة",
            value="`status` (صاحب البوت فقط)",
            inline=False
        )
        
        embed.set_footer(text="Vortex Bot | Made with ❤️ by g_8ia")
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"ℹ️ لم أجد معلومات عن الأمر: {cmd}")

async def load_cogs():
    """تحميل جميع الـ Cogs"""
    if not os.path.exists('./cogs'):
        os.makedirs('./cogs')
        print("✅ تم إنشاء مجلد cogs")
    
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('_'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"✅ تم تحميل: {filename}")
            except Exception as e:
                print(f"❌ خطأ في تحميل {filename}: {str(e)}")

async def main():
    """الدالة الرئيسية"""
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == '__main__':
    print("🚀 جاري تشغيل البوت...")
    asyncio.run(main())
