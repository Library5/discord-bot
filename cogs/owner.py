import discord
from discord.ext import commands
from config import OWNER_USERNAME, OWNER_ID

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def is_owner(self, ctx):
        """التحقق من أن المستخدم هو صاحب البوت"""
        # التحقق باستخدام الاسم أو الـ ID
        return ctx.author.name == OWNER_USERNAME or ctx.author.id == OWNER_ID or ctx.author.id == ctx.guild.owner_id
    
    @commands.command(name='status')
    @commands.check(lambda ctx: OwnerCommands(ctx.bot).is_owner(ctx))
    async def status(self, ctx, *, activity):
        """تغيير ستاتيوس البوت
        الاستخدام: !status <النص>
        مثال: !status Playing Vortex 🎮
        """
        try:
            # تحليل النشاط
            activity_text = activity.strip()
            
            # تحديد نوع النشاط
            if activity_text.lower().startswith('playing'):
                activity_type = discord.ActivityType.playing
                activity_name = activity_text[7:].strip()
            elif activity_text.lower().startswith('listening'):
                activity_type = discord.ActivityType.listening
                activity_name = activity_text[9:].strip()
            elif activity_text.lower().startswith('watching'):
                activity_type = discord.ActivityType.watching
                activity_name = activity_text[8:].strip()
            elif activity_text.lower().startswith('streaming'):
                activity_type = discord.ActivityType.streaming
                activity_name = activity_text[9:].strip()
            else:
                activity_type = discord.ActivityType.playing
                activity_name = activity_text
            
            # تغيير الستاتيوس
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=activity_type,
                    name=activity_name
                )
            )
            
            # حفظ الحالة في البوت
            self.bot.current_status = activity_text
            
            # إرسال رسالة تأكيد
            embed = discord.Embed(
                title="✅ تم تغيير الستاتيوس",
                description=f"**الستاتيوس الجديد:** {activity_text}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"غُير بواسطة {ctx.author.name}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='getstatus')
    async def get_status(self, ctx):
        """الحصول على الستاتيوس الحالي للبوت"""
        current = self.bot.current_status if hasattr(self.bot, 'current_status') else "لا يوجد"
        
        embed = discord.Embed(
            title="📊 الستاتيوس الحالي",
            description=f"**الستاتيوس:** {current}",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='botinfo')
    async def bot_info(self, ctx):
        """معلومات عن البوت"""
        embed = discord.Embed(
            title="🤖 معلومات البوت",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="اسم البوت", value=self.bot.user.name, inline=False)
        embed.add_field(name="ID", value=self.bot.user.id, inline=False)
        embed.add_field(name="صاحب البوت", value=OWNER_USERNAME, inline=False)
        embed.add_field(name="عدد السيرفرات", value=len(self.bot.guilds), inline=False)
        embed.add_field(name="عدد المستخدمين", value=sum(g.member_count for g in self.bot.guilds), inline=False)
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text="Vortex Bot | Made with ❤️")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))
