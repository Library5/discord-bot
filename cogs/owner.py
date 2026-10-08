import discord
from discord.ext import commands
from discord import app_commands
from config import OWNER_USERNAME, OWNER_ID

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def is_owner(self, ctx):
        """التحقق من أن المستخدم هو صاحب البوت"""
        return ctx.author.name == OWNER_USERNAME or ctx.author.id == OWNER_ID or ctx.author.id == ctx.guild.owner_id
    
    @commands.command(name='status')
    @commands.check(lambda ctx: OwnerCommands(ctx.bot).is_owner(ctx))
    async def status(self, ctx, *, activity):
        """تغيير ستاتيوس البوت (أمر عادي)
        الاستخدام: !status <النص>
        مثال: !status Playing Vortex 🎮
        """
        try:
            activity_text = activity.strip()
            
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
            
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=activity_type,
                    name=activity_name
                )
            )
            
            self.bot.current_status = activity_text
            
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
    
    @app_commands.command(name="status", description="تغيير ستاتيوس البوت")
    @app_commands.describe(activity="نوع النشاط والنص (Playing/Listening/Watching...)")
    async def status_slash(self, interaction: discord.Interaction, activity: str):
        """تغيير ستاتيوس البوت (أمر سلاش)"""
        if interaction.user.name != OWNER_USERNAME and interaction.user.id != OWNER_ID and interaction.user.id != interaction.guild.owner_id:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية لاستخدام هذا الأمر!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            activity_text = activity.strip()
            
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
            
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=activity_type,
                    name=activity_name
                )
            )
            
            self.bot.current_status = activity_text
            
            embed = discord.Embed(
                title="✅ تم تغيير الستاتيوس",
                description=f"**الستاتيوس الجديد:** {activity_text}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"غُير بواسطة {interaction.user.name}")
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="guilds", description="عرض قائمة السيرفرات التي البوت موجود فيها")
    async def guilds_slash(self, interaction: discord.Interaction):
        """عرض جميع السيرفرات التي البوت موجود فيها"""
        if interaction.user.name != OWNER_USERNAME and interaction.user.id != OWNER_ID:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية لاستخدام هذا الأمر!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guilds = self.bot.guilds
        
        if not guilds:
            embed = discord.Embed(
                title="❌ لا توجد سيرفرات",
                description="البوت غير موجود في أي سيرفر",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guilds_list = []
        for i, guild in enumerate(guilds, 1):
            guild_info = f"{i}. **{guild.name}** (ID: `{guild.id}`)\n   - 👥 الأعضاء: {guild.member_count}\n   - 📅 تاريخ الإنشاء: <t:{int(guild.created_at.timestamp())}:d>"
            guilds_list.append(guild_info)
        
        embeds = []
        current_text = ""
        
        for guild_info in guilds_list:
            if len(current_text) + len(guild_info) > 4000:
                embed = discord.Embed(
                    title="📊 السيرفرات",
                    description=current_text,
                    color=discord.Color.blue()
                )
                embeds.append(embed)
                current_text = guild_info
            else:
                current_text += guild_info + "\n"
        
        if current_text:
            embed = discord.Embed(
                title="📊 السيرفرات",
                description=current_text,
                color=discord.Color.blue()
            )
            embeds.append(embed)
        
        embeds[0].set_footer(text=f"إجمالي السيرفرات: {len(guilds)} | إجمالي الأعضاء: {sum(g.member_count for g in guilds)}")
        
        await interaction.response.send_message(embeds=embeds, ephemeral=True)
    
    @commands.command(name='guilds')
    @commands.check(lambda ctx: OwnerCommands(ctx.bot).is_owner(ctx))
    async def guilds_cmd(self, ctx):
        """عرض جميع السيرفرات التي البوت موجود فيها (أمر عادي)"""
        guilds = self.bot.guilds
        
        if not guilds:
            embed = discord.Embed(
                title="❌ لا توجد سيرفرات",
                description="البوت غير موجود في أي سيرفر",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        guilds_list = []
        for i, guild in enumerate(guilds, 1):
            guild_info = f"{i}. **{guild.name}** (ID: `{guild.id}`)\n   - 👥 الأعضاء: {guild.member_count}\n   - 📅 تاريخ الإنشاء: <t:{int(guild.created_at.timestamp())}:d>"
            guilds_list.append(guild_info)
        
        embeds = []
        current_text = ""
        
        for guild_info in guilds_list:
            if len(current_text) + len(guild_info) > 4000:
                embed = discord.Embed(
                    title="📊 السيرفرات",
                    description=current_text,
                    color=discord.Color.blue()
                )
                embeds.append(embed)
                current_text = guild_info
            else:
                current_text += guild_info + "\n"
        
        if current_text:
            embed = discord.Embed(
                title="📊 السيرفرات",
                description=current_text,
                color=discord.Color.blue()
            )
            embeds.append(embed)
        
        embeds[0].set_footer(text=f"إجمالي السيرفرات: {len(guilds)} | إجمالي الأعضاء: {sum(g.member_count for g in guilds)}")
        
        await ctx.send(embeds=embeds)
    
    @app_commands.command(name="leave", description="خروج البوت من سيرفر معين")
    @app_commands.describe(guild_id="معرّف السيرفر (ID)")
    async def leave_guild(self, interaction: discord.Interaction, guild_id: str):
        """خروج البوت من سيرفر معين"""
        if interaction.user.name != OWNER_USERNAME and interaction.user.id != OWNER_ID:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية لاستخدام هذا الأمر!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            guild_id = int(guild_id)
            guild = self.bot.get_guild(guild_id)
            
            if not guild:
                embed = discord.Embed(
                    title="❌ خطأ",
                    description=f"لم أجد السيرفر برقم: `{guild_id}`",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            guild_name = guild.name
            await guild.leave()
            
            embed = discord.Embed(
                title="✅ تم الخروج من السيرفر",
                description=f"**السيرفر:** {guild_name}\n**المعرّف:** {guild_id}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب أن يكون معرّف السيرفر رقماً صحيحاً!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @commands.command(name='leave')
    @commands.check(lambda ctx: OwnerCommands(ctx.bot).is_owner(ctx))
    async def leave_cmd(self, ctx, guild_id: int = None):
        """خروج البوت من سيرفر معين (أمر عادي)
        الاستخدام: !leave [guild_id]
        إذا لم تحدد ID، سيخرج من السيرفر الحالي
        """
        try:
            if guild_id is None:
                guild = ctx.guild
            else:
                guild = self.bot.get_guild(guild_id)
            
            if not guild:
                embed = discord.Embed(
                    title="❌ خطأ",
                    description=f"لم أجد السيرفر برقم: `{guild_id}`",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
            
            guild_name = guild.name
            await guild.leave()
            
            embed = discord.Embed(
                title="✅ تم الخروج من السيرفر",
                description=f"**السيرفر:** {guild_name}\n**المعرّف:** {guild.id}",
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
    
    @app_commands.command(name="botinfo", description="معلومات عن البوت")
    async def botinfo_slash(self, interaction: discord.Interaction):
        """عرض معلومات عن البوت"""
        embed = discord.Embed(
            title="🤖 معلومات البوت",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="📛 اسم البوت", value=self.bot.user.name, inline=False)
        embed.add_field(name="🆔 ID", value=self.bot.user.id, inline=False)
        embed.add_field(name="👑 صاحب البوت", value=OWNER_USERNAME, inline=False)
        embed.add_field(name="🌐 عدد السيرفرات", value=len(self.bot.guilds), inline=False)
        embed.add_field(name="👥 عدد المستخدمين", value=sum(g.member_count for g in self.bot.guilds), inline=False)
        embed.add_field(name="⏱️ البينج", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text="Vortex Bot | Made with ❤️")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="getstatus", description="الحصول على الستاتيوس الحالي للبوت")
    async def getstatus_slash(self, interaction: discord.Interaction):
        """الحصول على الستاتيوس الحالي للبوت"""
        current = self.bot.current_status if hasattr(self.bot, 'current_status') else "لا يوجد"
        
        embed = discord.Embed(
            title="📊 الستاتيوس الحالي",
            description=f"**الستاتيوس:** {current}",
            color=discord.Color.blue()
        )
        embed.add_field(name="⏱️ البينج", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ping", description="اختبار استجابة البوت")
    async def ping_slash(self, interaction: discord.Interaction):
        """اختبار استجابة البوت"""
        embed = discord.Embed(
            title="🏓 بينج البوت",
            description=f"⏱️ البينج: **{round(self.bot.latency * 1000)}ms**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    
    @commands.command(name='ping')
    async def ping_cmd(self, ctx):
        """اختبار استجابة البوت (أمر عادي)"""
        embed = discord.Embed(
            title="🏓 بينج البوت",
            description=f"⏱️ البينج: **{round(self.bot.latency * 1000)}ms**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))
