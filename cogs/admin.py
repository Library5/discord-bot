import discord
from discord.ext import commands
from config import ADMIN_ROLE

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def is_admin(self, ctx):
        """التحقق من صلاحيات الإدارة"""
        return any(role.name == ADMIN_ROLE for role in ctx.author.roles) or ctx.author.guild_permissions.administrator
    
    @commands.command(name='kick')
    @commands.check(lambda ctx: AdminCommands(ctx.bot).is_admin(ctx))
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """كوماند كيك العضو
        الاستخدام: !kick @user سبب
        """
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك طرد نفسك!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if member == ctx.guild.owner:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك طرد مالك السيرفر!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="✅ تم طرد العضو",
                description=f"**العضو:** {member.mention}\n**السبب:** {reason or 'لم يتم تحديد سبب'}",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='ban')
    @commands.check(lambda ctx: AdminCommands(ctx.bot).is_admin(ctx))
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """كوماند بان العضو
        الاستخدام: !ban @user سبب
        """
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك بان نفسك!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if member == ctx.guild.owner:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك بان مالك السيرفر!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="✅ تم حظر العضو",
                description=f"**العضو:** {member.mention}\n**السبب:** {reason or 'لم يتم تحديد سبب'}",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='clear')
    @commands.check(lambda ctx: AdminCommands(ctx.bot).is_admin(ctx))
    async def clear(self, ctx, amount: int = 5):
        """حذف عدد معين من الرسائل
        الاستخدام: !clear [العدد]
        """
        if amount > 100:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا يمكنك حذف أكثر من 100 رسالة دفعة واحدة!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        if amount < 1:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب تحديد عدد موجب!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount)
            embed = discord.Embed(
                title="✅ تم حذف الرسائل",
                description=f"تم حذف {len(deleted)} رسالة",
                color=discord.Color.green()
            )
            msg = await ctx.send(embed=embed)
            await msg.delete(delay=3)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='mute')
    @commands.check(lambda ctx: AdminCommands(ctx.bot).is_admin(ctx))
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        """إسكات عضو
        الاستخدام: !mute @user سبب
        """
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not mute_role:
            try:
                mute_role = await ctx.guild.create_role(
                    name="Muted",
                    color=discord.Color.greyple(),
                    reason="دور الإسكات"
                )
            except Exception as e:
                embed = discord.Embed(
                    title="❌ خطأ",
                    description=f"خطأ في إنشاء رول الإسكات: {str(e)}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
        
        try:
            await member.add_roles(mute_role, reason=reason)
            embed = discord.Embed(
                title="🔇 تم إسكات العضو",
                description=f"**العضو:** {member.mention}\n**السبب:** {reason or 'لم يتم تحديد سبب'}",
                color=discord.Color.greyple()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='unmute')
    @commands.check(lambda ctx: AdminCommands(ctx.bot).is_admin(ctx))
    async def unmute(self, ctx, member: discord.Member):
        """إلغاء إسكات عضو
        الاستخدام: !unmute @user
        """
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not mute_role:
            embed = discord.Embed(
                title="❌ خطأ",
                description="لا توجد رول إسكات!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.remove_roles(mute_role)
            embed = discord.Embed(
                title="🔊 تم إلغاء إسكات العضو",
                description=f"**العضو:** {member.mention}",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ خطأ",
                description=f"حدث خطأ: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
