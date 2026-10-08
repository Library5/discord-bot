import discord
from discord.ext import commands
from discord import app_commands
from config import ADMIN_ROLE
from datetime import datetime, timedelta
from collections import defaultdict
import re

class AdvancedWarningSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_warnings = defaultdict(int)  # {user_id: warning_count}
        self.muted_users = {}  # {user_id: unmute_time}
        self.log_channel = None
    
    @app_commands.command(name="warn", description="تحذير عضو")
    @app_commands.describe(member="العضو المراد تحذيره", reason="سبب التحذير")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        """تحذير عضو مع نظام متدرج"""
        if not any(role.name == ADMIN_ROLE for role in interaction.user.roles) and not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية لاستخدام هذا الأمر!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if member == interaction.user:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك تحذير نفسك!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.user_warnings[member.id] += 1
        warn_count = self.user_warnings[member.id]
        
        # إرسال رسالة خاصة للعضو
        embed_dm = discord.Embed(
            title="⚠️ تحذير رسمي",
            description=f"لقد تم تحذيرك في السيرفر **{interaction.guild.name}**",
            color=discord.Color.orange()
        )
        embed_dm.add_field(name="📝 السبب", value=reason, inline=False)
        embed_dm.add_field(name="⚠️ عدد التحذيرات", value=f"{warn_count}/3", inline=False)
        embed_dm.add_field(name="👮 تحذير من", value=interaction.user.mention, inline=False)
        
        if warn_count == 3:
            embed_dm.add_field(
                name="🚨 إجراء تلقائي",
                value="سيتم إسكاتك لمدة 5 دقائق تلقائياً!",
                inline=False
            )
        
        embed_dm.set_footer(text=f"التحذير {warn_count}/3")
        embed_dm.color = discord.Color.orange() if warn_count < 3 else discord.Color.red()
        
        try:
            await member.send(embed=embed_dm)
        except:
            pass
        
        # رسالة في السيرفر
        embed = discord.Embed(
            title="⚠️ تحذير عضو",
            description=f"**العضو:** {member.mention}\n**السبب:** {reason}",
            color=discord.Color.orange()
        )
        embed.add_field(name="⚠️ عدد التحذيرات", value=f"{warn_count}/3", inline=False)
        embed.set_footer(text=f"التحذير {warn_count}/3")
        
        await interaction.response.send_message(embed=embed)
        
        # إذا وصل 3 تحذيرات = ميوت تلقائي
        if warn_count >= 3:
            mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
            
            if not mute_role:
                try:
                    mute_role = await interaction.guild.create_role(
                        name="Muted",
                        color=discord.Color.greyple(),
                        reason="دور الإسكات التلقائي"
                    )
                except:
                    pass
            
            if mute_role:
                try:
                    await member.add_roles(mute_role, reason=f"3 تحذيرات - {reason}")
                    unmute_time = datetime.utcnow() + timedelta(minutes=5)
                    self.muted_users[member.id] = unmute_time
                    
                    embed_mute = discord.Embed(
                        title="🔇 تم إسكاتك تلقائياً",
                        description=f"تم إسكاتك لمدة **5 دقائق** بسبب 3 تحذيرات",
                        color=discord.Color.red()
                    )
                    embed_mute.add_field(name="⏰ سيتم فتح الكلام في", value=f"<t:{int(unmute_time.timestamp())}:R>", inline=False)
                    
                    try:
                        await member.send(embed=embed_mute)
                    except:
                        pass
                except:
                    pass
    
    @app_commands.command(name="clearwarnings", description="حذف التحذيرات")
    @app_commands.describe(member="العضو المراد حذف تحذيراته")
    async def clear_warnings(self, interaction: discord.Interaction, member: discord.Member):
        """حذف جميع تحذيرات عضو"""
        if not any(role.name == ADMIN_ROLE for role in interaction.user.roles) and not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        old_warnings = self.user_warnings.get(member.id, 0)
        self.user_warnings[member.id] = 0
        
        embed = discord.Embed(
            title="✅ تم حذف التحذيرات",
            description=f"**العضو:** {member.mention}\n**التحذيرات السابقة:** {old_warnings}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="warnings", description="عرض عدد التحذيرات")
    @app_commands.describe(member="العضو")
    async def show_warnings(self, interaction: discord.Interaction, member: discord.Member):
        """عرض عدد تحذيرات عضو"""
        warn_count = self.user_warnings.get(member.id, 0)
        
        embed = discord.Embed(
            title="📊 عدد التحذيرات",
            description=f"**العضو:** {member.mention}",
            color=discord.Color.blue()
        )
        embed.add_field(name="⚠️ التحذيرات", value=f"{warn_count}/3", inline=False)
        
        if warn_count >= 3:
            embed.add_field(name="🔇 الحالة", value="مسكوت (5 دقائق)", inline=False)
        elif warn_count > 0:
            embed.add_field(name="⚠️ تنبيه", value=f"يتبقى {3 - warn_count} تحذيرات قبل الإسكات", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AdvancedWarningSystem(bot))
