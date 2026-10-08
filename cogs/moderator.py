import discord
from discord.ext import commands
from discord import app_commands
from config import ADMIN_ROLE

class ModeratorCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def is_admin(self, interaction: discord.Interaction):
        """التحقق من الصلاحيات الإدارية"""
        return any(role.name == ADMIN_ROLE for role in interaction.user.roles) or interaction.user.guild_permissions.administrator
    
    @app_commands.command(name="slowmode", description="تفعيل أو تعطيل الوضع البطيء في القناة")
    @app_commands.describe(seconds="عدد الثواني (0 = تعطيل)")
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        """تفعيل أو تعطيل الوضع البطيء"""
        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية لاستخدام هذا الأمر!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if seconds < 0 or seconds > 21600:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب أن تكون القيمة بين 0 و 21600 ثانية (6 ساعات)!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await interaction.channel.edit(slowmode_delay=seconds)
            
            if seconds == 0:
                embed = discord.Embed(
                    title="✅ تم تعطيل الوضع البطيء",
                    description=f"**القناة:** {interaction.channel.mention}",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="✅ تم تفعيل الوضع البطيء",
                    description=f"**القناة:** {interaction.channel.mention}\n**المدة:** {seconds} ثانية",
                    color=discord.Color.green()
                )
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="lock", description="قفل القناة الحالية")
    async def lock_channel(self, interaction: discord.Interaction):
        """قفل القناة الحالية"""
        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية لاستخدام هذا الأمر!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await interaction.channel.set_permissions(
                interaction.guild.default_role,
                send_messages=False
            )
            
            embed = discord.Embed(
                title="🔒 تم قفل القناة",
                description=f"**القناة:** {interaction.channel.mention}",
                color=discord.Color.red()
            )
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="unlock", description="فتح القناة الحالية")
    async def unlock_channel(self, interaction: discord.Interaction):
        """فتح القناة الحالية"""
        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية لاستخدام هذا الأمر!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await interaction.channel.set_permissions(
                interaction.guild.default_role,
                send_messages=True
            )
            
            embed = discord.Embed(
                title="🔓 تم فتح القناة",
                description=f"**القناة:** {interaction.channel.mention}",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="announce", description="نشر إعلان في القناة")
    @app_commands.describe(title="عنوان الإعلان", content="محتوى الإعلان")
    async def announce(self, interaction: discord.Interaction, title: str, content: str):
        """نشر إعلان في القناة"""
        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية لاستخدام هذا الأمر!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            embed = discord.Embed(
                title=f"📢 {title}",
                description=content,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"تم النشر بواسطة {interaction.user.name}")
            
            await interaction.channel.send(embed=embed)
            
            embed_confirm = discord.Embed(
                title="✅ تم نشر الإعلان",
                description=f"**القناة:** {interaction.channel.mention}",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed_confirm, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="role", description="إضافة أو إزالة دور من عضو")
    @app_commands.describe(member="العضو", role="الدور", action="إضافة أو إزالة")
    async def role_command(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role, action: str):
        """إضافة أو إزالة دور من عضو"""
        if not self.is_admin(interaction):
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية لاستخدام هذا الأمر!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if action.lower() not in ["add", "remove", "إضافة", "إزالة"]:
            embed = discord.Embed(
                title="❌ خطأ",
                description="استخدم 'add'/'إضافة' أو 'remove'/'إزالة'",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            if action.lower() in ["add", "إضافة"]:
                await member.add_roles(role)
                embed = discord.Embed(
                    title="✅ تم إضافة الدور",
                    description=f"**العضو:** {member.mention}\n**الدور:** {role.mention}",
                    color=discord.Color.green()
                )
            else:
                await member.remove_roles(role)
                embed = discord.Embed(
                    title="✅ تم إزالة الدور",
                    description=f"**العضو:** {member.mention}\n**الدور:** {role.mention}",
                    color=discord.Color.green()
                )
            
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="channelinfo", description="معلومات عن القناة الحالية")
    async def channel_info(self, interaction: discord.Interaction):
        """عرض معلومات عن القناة الحالية"""
        channel = interaction.channel
        
        embed = discord.Embed(
            title=f"📊 معلومات القناة",
            description=f"**{channel.name}**",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="🆔 ID", value=channel.id, inline=False)
        embed.add_field(name="📝 الوصف", value=channel.topic or "لا يوجد وصف", inline=False)
        embed.add_field(name="📅 تاريخ الإنشاء", value=f"<t:{int(channel.created_at.timestamp())}:d>", inline=False)
        embed.add_field(name="🔢 الموضع", value=channel.position, inline=False)
        
        if isinstance(channel, discord.TextChannel):
            embed.add_field(name="⏱️ الوضع البطيء", value=f"{channel.slowmode_delay}s" if channel.slowmode_delay > 0 else "معطل", inline=False)
            try:
                pins = await channel.pins()
                embed.add_field(name="📌 الرسائل المثبتة", value=len(pins), inline=False)
            except:
                embed.add_field(name="📌 الرسائل المثبتة", value="لا يمكن الوصول", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ModeratorCommands(bot))
