import discord
from discord.ext import commands, tasks
from discord import app_commands
from config import ADMIN_ROLE
from datetime import datetime, timedelta
import re

class AdvancedGiveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaways = {}
        self.check_giveaways.start()
    
    def parse_duration(self, duration_str: str) -> int:
        """تحويل صيغ مثل 1h 30m إلى ثواني"""
        duration_str = duration_str.lower().strip()
        total_seconds = 0
        
        # البحث عن أيام
        days_match = re.search(r'(\d+)\s*d', duration_str)
        if days_match:
            total_seconds += int(days_match.group(1)) * 86400
        
        # البحث عن ساعات
        hours_match = re.search(r'(\d+)\s*h', duration_str)
        if hours_match:
            total_seconds += int(hours_match.group(1)) * 3600
        
        # البحث عن دقائق
        minutes_match = re.search(r'(\d+)\s*m', duration_str)
        if minutes_match:
            total_seconds += int(minutes_match.group(1)) * 60
        
        # البحث عن ثواني
        seconds_match = re.search(r'(\d+)\s*s', duration_str)
        if seconds_match:
            total_seconds += int(seconds_match.group(1))
        
        return total_seconds if total_seconds > 0 else None
    
    @app_commands.command(name="giveaway", description="إنشاء جائزة جديدة")
    @app_commands.describe(
        duration="المدة (1h, 30m, 2d, إلخ)",
        winners="عدد الفائزين",
        prize="اسم الجائزة"
    )
    async def giveaway(self, interaction: discord.Interaction, duration: str, winners: int, prize: str):
        """إنشاء giveaway جديد مع قبول صيغ متعددة"""
        if not any(role.name == ADMIN_ROLE for role in interaction.user.roles) and not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية لاستخدام هذا الأمر!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # تحويل المدة
        duration_seconds = self.parse_duration(duration)
        if not duration_seconds:
            embed = discord.Embed(
                title="❌ خطأ",
                description="صيغة المدة غير صحيحة! (استخدم: 1h, 30m, 2d, إلخ)",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if duration_seconds < 60:
            embed = discord.Embed(
                title="❌ خطأ",
                description="المدة الدنيا 1 دقيقة!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if winners < 1:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب تحديد فائز واحد على الأقل!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        end_time = datetime.utcnow() + timedelta(seconds=duration_seconds)
        
        # إنشاء embed الجائزة
        embed = discord.Embed(
            title="🎉 جائزة جديدة!",
            description=f"**الجائزة:** {prize}",
            color=discord.Color.gold()
        )
        embed.add_field(name="⏰ وقت الانتهاء", value=f"<t:{int(end_time.timestamp())}:F>", inline=False)
        embed.add_field(name="🏆 عدد الفائزين", value=f"**{winners}** فائزين", inline=False)
        embed.add_field(name="👥 المشاركون", value="**0** مشارك", inline=False)
        embed.add_field(name="📝 تعليمات", value="اضغط على 🎉 للمشاركة\nاضغط مرة أخرى لإلغاء المشاركة", inline=False)
        embed.set_footer(text=f"ينتهي في {duration}")
        
        await interaction.response.defer()
        message = await interaction.channel.send(embed=embed)
        await message.add_reaction("🎉")
        
        # تخزين معلومات الجائزة
        self.giveaways[message.id] = {
            'prize': prize,
            'end_time': end_time,
            'winners_count': winners,
            'participants': set(),
            'guild_id': interaction.guild.id,
            'channel_id': interaction.channel.id,
            'ended': False
        }
        
        # رسالة تأكيد
        embed_confirm = discord.Embed(
            title="✅ تم إنشاء الجائزة",
            description=f"**الجائزة:** {prize}\n**الفائزين:** {winners}",
            color=discord.Color.green()
        )
        embed_confirm.add_field(name="⏰ المدة", value=f"<t:{int(end_time.timestamp())}:R>", inline=False)
        
        await interaction.followup.send(embed=embed_confirm, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """معالج إضافة رد فعل"""
        if user.bot:
            return
        
        if reaction.emoji != "🎉":
            return
        
        message_id = reaction.message.id
        
        if message_id not in self.giveaways:
            return
        
        giveaway = self.giveaways[message_id]
        
        if giveaway['ended']:
            return
        
        if datetime.utcnow() >= giveaway['end_time']:
            return
        
        giveaway['participants'].add(user.id)
        
        try:
            message = await reaction.message.channel.fetch_message(message_id)
            if message.embeds:
                embed = message.embeds[0]
                embed.set_field_at(2, name="👥 المشاركون", value=f"**{len(giveaway['participants'])}** مشارك", inline=False)
                await message.edit(embed=embed)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        """معالج إزالة رد فعل"""
        if user.bot:
            return
        
        if reaction.emoji != "🎉":
            return
        
        message_id = reaction.message.id
        
        if message_id not in self.giveaways:
            return
        
        giveaway = self.giveaways[message_id]
        if user.id in giveaway['participants']:
            giveaway['participants'].discard(user.id)
            
            try:
                message = await reaction.message.channel.fetch_message(message_id)
                if message.embeds:
                    embed = message.embeds[0]
                    embed.set_field_at(2, name="👥 المشاركون", value=f"**{len(giveaway['participants'])}** مشارك", inline=False)
                    await message.edit(embed=embed)
            except:
                pass
    
    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        """فحص انتهاء الجوائز"""
        import random
        
        for message_id in list(self.giveaways.keys()):
            giveaway = self.giveaways[message_id]
            
            if giveaway['ended']:
                continue
            
            if datetime.utcnow() >= giveaway['end_time']:
                giveaway['ended'] = True
                
                guild = self.bot.get_guild(giveaway['guild_id'])
                if not guild:
                    continue
                
                channel = guild.get_channel(giveaway['channel_id'])
                if not channel:
                    continue
                
                try:
                    message = await channel.fetch_message(message_id)
                    
                    participants = list(giveaway['participants'])
                    winners_count = min(giveaway['winners_count'], len(participants))
                    
                    if winners_count == 0:
                        embed = discord.Embed(
                            title="🎉 انتهت الجائزة!",
                            description=f"**الجائزة:** {giveaway['prize']}",
                            color=discord.Color.red()
                        )
                        embed.add_field(
                            name="❌ لم يكن هناك مشاركون",
                            value="حظ أوفر المرة القادمة! 🍀",
                            inline=False
                        )
                    else:
                        winners = random.sample(participants, winners_count)
                        winners_mentions = " ".join([f"<@{winner_id}>" for winner_id in winners])
                        
                        embed = discord.Embed(
                            title="🎉 انتهت الجائزة!",
                            description=f"**الجائزة:** {giveaway['prize']}",
                            color=discord.Color.green()
                        )
                        embed.add_field(
                            name="🏆 الفائزون",
                            value=winners_mentions,
                            inline=False
                        )
                        embed.add_field(
                            name="👥 إجمالي المشاركين",
                            value=f"{len(participants)} مشارك",
                            inline=False
                        )
                    
                    embed.set_footer(text="شكراً على المشاركة!")
                    
                    await message.reply(embed=embed)
                    
                except:
                    pass
                
                del self.giveaways[message_id]

async def setup(bot):
    await bot.add_cog(AdvancedGiveaway(bot))
