import discord
from discord.ext import commands
from discord import app_commands
from config import ADMIN_ROLE
from datetime import datetime, timedelta
from collections import defaultdict

class AntiSpamCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = defaultdict(list)  # {user_id: [(timestamp, message), ...]}
        self.warned_users = defaultdict(int)  # {user_id: warn_count}
        self.spam_threshold = 5  # عدد الرسائل
        self.spam_time_window = 5  # ثوان
        self.log_channel = None
    
    @app_commands.command(name="setlogchannel", description="تحديد قناة للتنبيهات والسجلات")
    @app_commands.describe(channel="القناة التي سيتم إرسال التنبيهات فيها")
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """تحديد قناة للتنبيهات والسجلات"""
        if not any(role.name == ADMIN_ROLE for role in interaction.user.roles) and not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية لاستخدام هذا الأمر!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.log_channel = channel
        
        embed = discord.Embed(
            title="✅ تم تحديد قناة السجل",
            description=f"**القناة:** {channel.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="📝 الملاحظات", value="سيتم إرسال جميع التنبيهات والسجلات في هذه القناة")
        
        await interaction.response.send_message(embed=embed)
    
    @commands.command(name="setlogchannel")
    async def set_log_channel_cmd(self, ctx, channel: discord.TextChannel):
        """تحديد قناة للتنبيهات والسجلات (أمر عادي)"""
        if not any(role.name == ADMIN_ROLE for role in ctx.author.roles) and not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية لاستخدام هذا الأمر!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        self.log_channel = channel
        
        embed = discord.Embed(
            title="✅ تم تحديد قناة السجل",
            description=f"**القناة:** {channel.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="📝 الملاحظات", value="سيتم إرسال جميع التنبيهات والسجلات في هذه القناة")
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """مراقبة الرسائل للكشف عن السبام"""
        if message.author.bot:
            return
        
        current_time = datetime.utcnow()
        user_id = message.author.id
        
        # إضافة الرسالة إلى السجل
        self.user_messages[user_id].append((current_time, message.content))
        
        # تنظيف الرسائل القديمة
        time_limit = current_time - timedelta(seconds=self.spam_time_window)
        self.user_messages[user_id] = [
            (msg_time, content) for msg_time, content in self.user_messages[user_id]
            if msg_time > time_limit
        ]
        
        # فحص السبام
        recent_messages = self.user_messages[user_id]
        if len(recent_messages) >= self.spam_threshold:
            await self._handle_spam(message)
    
    async def _handle_spam(self, message: discord.Message):
        """معالجة السبام"""
        user_id = message.author.id
        self.warned_users[user_id] += 1
        warn_count = self.warned_users[user_id]
        
        # إرسال تنبيه في الرسالة الخاصة
        try:
            embed = discord.Embed(
                title="⚠️ تحذير من السبام",
                description=f"تم اكتشاف سبام في السيرفر: **{message.guild.name}**",
                color=discord.Color.orange()
            )
            embed.add_field(name="📊 عدد التحذيرات", value=f"{warn_count}", inline=False)
            embed.add_field(name="💬 الرسالة", value=message.content[:100] if message.content else "[فارغة]", inline=False)
            embed.add_field(name="⏰ الوقت", value=f"<t:{int(message.created_at.timestamp())}:F>", inline=False)
            
            if warn_count >= 3:
                embed.add_field(
                    name="🚨 تنبيه",
                    value="لقد حصلت على 3 تحذيرات! قد يتم اتخاذ إجراء إداري.",
                    inline=False
                )
            
            await message.author.send(embed=embed)
        except:
            pass
        
        # إرسال تنبيه في قناة السجل إن وجدت
        if self.log_channel:
            embed = discord.Embed(
                title="⚠️ تحذير سبام",
                description=f"**المستخدم:** {message.author.mention}\n**السيرفر:** {message.guild.name}",
                color=discord.Color.orange()
            )
            embed.add_field(name="📊 عدد التحذيرات", value=f"{warn_count}", inline=False)
            embed.add_field(name="💬 الرسالة", value=message.content[:100] if message.content else "[فارغة]", inline=False)
            embed.add_field(name="🔗 الرابط", value=f"[اضغط هنا]({message.jump_url})", inline=False)
            
            try:
                await self.log_channel.send(embed=embed)
            except:
                pass

async def setup(bot):
    await bot.add_cog(AntiSpamCommands(bot))
