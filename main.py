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

# إنشاء البوت مع دعم Slash Commands
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# متغير لتخزين حالة البوت الحالية
bot.current_status = "Online 🟢"

@bot.event
async def on_ready():
    """عند جاهزية البوت"""
    print(f"✅ تم تسجيل الدخول باسم {bot.user}")
    print(f"🤖 البوت جاهز!")
    print(f"📊 عدد السيرفرات: {len(bot.guilds)}")
    print(f"👥 عدد المستخدمين: {sum(g.member_count for g in bot.guilds)}")
    
    # مزامنة Slash Commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ تم مزامنة {len(synced)} أوامر سلاش")
    except Exception as e:
        print(f"❌ خطأ في مزامنة أوامر سلاش: {e}")
    
    # تعيين الحالة
    activity = discord.Activity(type=discord.ActivityType.watching, name=f"{PREFIX}help")
    await bot.change_presence(activity=activity)

@bot.event
async def on_command_error(ctx, error):
    """معالج أخطاء الأوامر العادية"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ استخدم الأمر بشكل صحيح! اكتب `{PREFIX}help <اسم الأمر>`")
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
            title="📚 قائمة الأوامر الشاملة",
            description="استخدم `/` لـ Slash Commands أو `!` للأوامر العادية",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🛡️ أوامر إدارية",
            value="`/kick` | `/ban` | `/mute` | `/unmute` | `/clear` | `/warn`",
            inline=False
        )
        
        embed.add_field(
            name="🎉 أوامر جيفاوي",
            value="`/giveaway` | `/endgiveaway`",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ أوامر الإشراف",
            value="`/slowmode` | `/lock` | `/unlock` | `/announce` | `/role` | `/channelinfo`",
            inline=False
        )
        
        embed.add_field(
            name="📊 أوامر المعلومات",
            value="`/serverinfo` | `/userinfo` | `/botinfo` | `/ping` | `/getstatus`",
            inline=False
        )
        
        embed.add_field(
            name="👑 أوامر صاحب البوت",
            value="`/status` | `/guilds` | `/leave` | `/setlogchannel`",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ الأوامر العادية",
            value="`!help` | `!sync` | `!ping` | `!botinfo`",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ نظام مكافحة السبام",
            value="يكتشف البوت السبام تلقائياً وينبه المستخدم عبر DM\n`/setlogchannel` - لتحديد قناة السجلات",
            inline=False
        )
        
        embed.set_footer(text="Vortex Bot v2.0 | Made with ❤️ by g_8ia")
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"ℹ️ لم أجد معلومات عن الأمر: {cmd}")

@bot.command(name='sync')
@commands.is_owner()
async def sync_commands(ctx):
    """مزامنة أوامر سلاش يدوياً (صاحب البوت فقط)"""
    try:
        synced = await bot.tree.sync()
        embed = discord.Embed(
            title="✅ تم المزامنة",
            description=f"تم مزامنة {len(synced)} أوامر سلاش",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ",
            description=f"حدث خطأ: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

async def load_cogs():
    """تحميل جميع الـ Cogs"""
    if not os.path.exists('./cogs'):
        os.makedirs('./cogs')
        print("✅ تم إنشاء مجلد cogs")
    
    cog_files = [
        'admin.py',
        'admin_slash.py',
        'giveaway.py',
        'giveaway_slash.py',
        'owner.py',
        'moderator.py',
        'antispam.py'
    ]
    
    for filename in cog_files:
        filepath = os.path.join('./cogs', filename)
        if os.path.exists(filepath):
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
    print("=" * 50)
    asyncio.run(main())
