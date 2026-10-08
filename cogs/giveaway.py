import discord
from discord.ext import commands, tasks
import asyncio
import random
from datetime import datetime, timedelta
from config import ADMIN_ROLE

class GiveawayManager:
    def __init__(self):
        self.giveaways = {}  # {message_id: giveaway_data}
    
    def create_giveaway(self, message_id, prize, duration, winners_count, guild_id):
        """إنشاء giveaway جديد"""
        end_time = datetime.utcnow() + timedelta(seconds=duration)
        self.giveaways[message_id] = {
            'prize': prize,
            'end_time': end_time,
            'winners_count': winners_count,
            'participants': set(),
            'guild_id': guild_id,
            'ended': False
        }
    
    def is_giveaway_active(self, message_id):
        """التحقق من كون الـ giveaway نشطاً"""
        if message_id not in self.giveaways:
            return False
        
        giveaway = self.giveaways[message_id]
        if giveaway['ended']:
            return False
        
        if datetime.utcnow() >= giveaway['end_time']:
            return False
        
        return True
    
    def add_participant(self, message_id, user_id):
        """إضافة مشارك"""
        if message_id in self.giveaways:
            self.giveaways[message_id]['participants'].add(user_id)
            return True
        return False
    
    def end_giveaway(self, message_id):
        """إنهاء giveaway واختيار الفائزين"""
        if message_id not in self.giveaways:
            return None
        
        giveaway = self.giveaways[message_id]
        giveaway['ended'] = True
        
        participants = list(giveaway['participants'])
        winners_count = min(giveaway['winners_count'], len(participants))
        
        if winners_count == 0:
            return {'winners': [], 'prize': giveaway['prize']}
        
        winners = random.sample(participants, winners_count)
        
        return {
            'winners': winners,
            'prize': giveaway['prize'],
            'total_participants': len(participants)
        }

giveaway_manager = GiveawayManager()

class GiveawayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()
    
    def is_admin(self, ctx):
        """التحقق من الصلاحيات الإدارية"""
        return any(role.name == ADMIN_ROLE for role in ctx.author.roles) or ctx.author.guild_permissions.administrator
    
    @commands.command(name='giveaway', aliases=['ga'])
    @commands.check(lambda ctx: GiveawayCog(ctx.bot).is_admin(ctx))
    async def giveaway(self, ctx, duration: int, winners: int, *, prize):
        """إنشاء giveaway جديد
        الاستخدام: !giveaway <المدة بالثواني> <عدد الفائزين> <الجائزة>
        مثال: !giveaway 3600 2 Nitro Classic
        """
        
        if duration < 60:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب أن تكون المدة على الأقل 60 ثانية!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if winners < 1:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب تحديد فائز واحد على الأقل!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # إنشاء رسالة الـ giveaway
        embed = discord.Embed(
            title="🎉 جائزة جديدة!",
            description=f"**الجائزة:** {prize}",
            color=discord.Color.gold()
        )
        
        end_time = datetime.utcnow() + timedelta(seconds=duration)
        embed.add_field(name="⏰ وقت الانتهاء", value=f"<t:{int(end_time.timestamp())}:F>", inline=False)
        embed.add_field(name="🏆 عدد الفائزين", value=f"{winners}", inline=False)
        embed.add_field(name="👥 المشاركون", value="0", inline=False)
        embed.set_footer(text="اضغط على الإيموجي 🎉 للمشاركة!")
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("🎉")
        
        # تسجيل الـ giveaway
        giveaway_manager.create_giveaway(
            message.id,
            prize,
            duration,
            winners,
            ctx.guild.id
        )
        
        confirmation = await ctx.send(f"✅ تم إنشاء جائزة جديدة! سينتهي في <t:{int(end_time.timestamp())}:R>")
        await asyncio.sleep(5)
        await confirmation.delete()
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """معالج إضافة رد فعل"""
        if user.bot:
            return
        
        if reaction.emoji != "🎉":
            return
        
        message_id = reaction.message.id
        
        if not giveaway_manager.is_giveaway_active(message_id):
            return
        
        if giveaway_manager.add_participant(message_id, user.id):
            # تحديث عدد المشاركين
            giveaway = giveaway_manager.giveaways[message_id]
            try:
                message = await reaction.message.channel.fetch_message(message_id)
                if message.embeds:
                    embed = message.embeds[0]
                    embed.set_field_at(2, name="👥 المشاركون", value=str(len(giveaway['participants'])), inline=False)
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
        
        if message_id not in giveaway_manager.giveaways:
            return
        
        giveaway = giveaway_manager.giveaways[message_id]
        if user.id in giveaway['participants']:
            giveaway['participants'].discard(user.id)
            
            try:
                message = await reaction.message.channel.fetch_message(message_id)
                if message.embeds:
                    embed = message.embeds[0]
                    embed.set_field_at(2, name="👥 المشاركون", value=str(len(giveaway['participants'])), inline=False)
                    await message.edit(embed=embed)
            except:
                pass
    
    @tasks.loop(seconds=5)
    async def check_giveaways(self):
        """فحص انتهاء الـ giveaways"""
        for message_id in list(giveaway_manager.giveaways.keys()):
            giveaway = giveaway_manager.giveaways[message_id]
            
            if giveaway['ended']:
                continue
            
            if datetime.utcnow() >= giveaway['end_time']:
                result = giveaway_manager.end_giveaway(message_id)
                
                guild = self.bot.get_guild(giveaway['guild_id'])
                if not guild:
                    continue
                
                # البحث عن رسالة الـ giveaway
                for channel in guild.text_channels:
                    try:
                        message = await channel.fetch_message(message_id)
                        
                        if result['winners']:
                            winners_mentions = " ".join([f"<@{winner_id}>" for winner_id in result['winners']])
                            embed = discord.Embed(
                                title="🎉 انتهت الجائزة!",
                                description=f"**الجائزة:** {result['prize']}\n\n**الفائزون:** {winners_mentions}",
                                color=discord.Color.green()
                            )
                            embed.add_field(name="👥 إجمالي المشاركين", value=str(result['total_participants']))
                        else:
                            embed = discord.Embed(
                                title="🎉 انتهت الجائزة!",
                                description=f"**الجائزة:** {result['prize']}\n\n**لم يكن هناك مشاركون! ❌",
                                color=discord.Color.red()
                            )
                        
                        await message.reply(embed=embed)
                        break
                    except discord.NotFound:
                        continue
                    except:
                        continue
    
    @commands.command(name='endgiveaway', aliases=['endga'])
    @commands.check(lambda ctx: GiveawayCog(ctx.bot).is_admin(ctx))
    async def end_giveaway(self, ctx, message_id: int):
        """إنهاء giveaway يدوياً
        الاستخدام: !endgiveaway <message_id>
        """
        result = giveaway_manager.end_giveaway(message_id)
        
        if not result:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لم أجد هذه الجائزة!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if result['winners']:
            winners_mentions = " ".join([f"<@{winner_id}>" for winner_id in result['winners']])
            embed = discord.Embed(
                title="🎉 انتهت الجائزة!",
                description=f"**الجائزة:** {result['prize']}\n\n**الفائزون:** {winners_mentions}",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="🎉 انتهت الجائزة!",
                description=f"**الجائزة:** {result['prize']}\n\n**لم يكن هناك مشاركون! ❌",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GiveawayCog(bot))
