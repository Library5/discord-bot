import discord
from discord.ext import commands
from discord import app_commands
from config import ADMIN_ROLE
from datetime import datetime
import io

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets = {}  # {ticket_channel_id: {"creator": user_id, "claimed_by": user_id or None}}
        self.transcript_log_channel = None
    
    @app_commands.command(name="setup-tickets", description="إعداد نظام التكتات")
    async def setup_tickets(self, interaction: discord.Interaction):
        """إعداد نظام التكتات مع زر الإنشاء"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # إنشاء embed للتكتات
        embed = discord.Embed(
            title="🎫 نظام التكتات",
            description="اضغط على الزر أدناه لفتح تكت جديد",
            color=discord.Color.blue()
        )
        embed.add_field(name="ℹ️ معلومات", value="سيتم إنشاء قناة خاصة بك", inline=False)
        
        # إنشاء زر
        view = TicketView(self)
        await interaction.channel.send(embed=embed, view=view)
        
        await interaction.response.send_message("✅ تم إعداد نظام التكتات!", ephemeral=True)
    
    @app_commands.command(name="transcript-log", description="تحديد قناة السجل للترانسكريبت")
    @app_commands.describe(channel="القناة المراد حفظ الترانسكريبت فيها")
    async def set_transcript_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """تحديد قناة لحفظ الترانسكريبت"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ خطأ",
                description="ليس لديك الصلاحية!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.transcript_log_channel = channel
        
        embed = discord.Embed(
            title="✅ تم تحديد قناة الترانسكريبت",
            description=f"**القناة:** {channel.mention}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    async def create_ticket(self, interaction: discord.Interaction):
        """إنشاء تكت جديد"""
        guild = interaction.guild
        user = interaction.user
        
        # إنشاء قناة التكت
        overwrites = {\n            guild.default_role: discord.PermissionOverwrite(view_channel=False),\n            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),\n            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)\n        }\n        \n        ticket_channel = await guild.create_text_channel(\n            name=f\"ticket-{user.name}\",\n            overwrites=overwrites,\n            reason=f\"تكت من {user}\"\n        )\n        \n        self.tickets[ticket_channel.id] = {\"creator\": user.id, \"claimed_by\": None}\n        \n        # إنشاء رسالة التكت\n        embed = discord.Embed(\n            title=\"🎫 تكت جديد\",\n            description=f\"مرحباً {user.mention}، كيف يمكننا مساعدتك؟\",\n            color=discord.Color.blue()\n        )\n        embed.add_field(name=\"👤 المنشئ\", value=user.mention, inline=False)\n        embed.add_field(name=\"📅 التاريخ\", value=f\"<t:{int(datetime.utcnow().timestamp())}:F>\", inline=False)\n        \n        view = TicketActionView(self, ticket_channel.id)\n        await ticket_channel.send(embed=embed, view=view)\n        \n        embed_reply = discord.Embed(\n            title=\"✅ تم إنشاء التكت\",\n            description=f\"**التكت:** {ticket_channel.mention}\",\n            color=discord.Color.green()\n        )\n        \n        await interaction.response.send_message(embed=embed_reply, ephemeral=True)\n    \n    async def close_ticket(self, interaction: discord.Interaction, ticket_channel_id: int):\n        \"\"\"إغلاق التكت وإرسال الترانسكريبت\"\"\"\n        ticket_channel = self.bot.get_channel(ticket_channel_id)\n        if not ticket_channel:\n            return\n        \n        ticket_info = self.tickets.get(ticket_channel_id, {})\n        creator_id = ticket_info.get(\"creator\")\n        claimed_by_id = ticket_info.get(\"claimed_by\")\n        \n        # جمع الرسائل\n        messages = []\n        async for message in ticket_channel.history(limit=None, oldest_first=True):\n            messages.append(message)\n        \n        # إنشاء ترانسكريبت\n        transcript = self._generate_transcript(messages, ticket_channel.name)\n        \n        # إرسال الترانسكريبت للمنشئ\n        if creator_id:\n            try:\n                creator = await self.bot.fetch_user(creator_id)\n                embed = discord.Embed(\n                    title=\"📄 ترانسكريبت التكت\",\n                    description=f\"**التكت:** {ticket_channel.name}\",\n                    color=discord.Color.blue()\n                )\n                await creator.send(embed=embed, file=discord.File(io.BytesIO(transcript.encode()), filename=\"transcript.txt\"))\n            except:\n                pass\n        \n        # إرسال الترانسكريبت لمن ادعى التكت\n        if claimed_by_id and claimed_by_id != creator_id:\n            try:\n                claimer = await self.bot.fetch_user(claimed_by_id)\n                embed = discord.Embed(\n                    title=\"📄 ترانسكريبت التكت\",\n                    description=f\"**التكت:** {ticket_channel.name}\",\n                    color=discord.Color.blue()\n                )\n                await claimer.send(embed=embed, file=discord.File(io.BytesIO(transcript.encode()), filename=\"transcript.txt\"))\n            except:\n                pass\n        \n        # إرسال الترانسكريبت لقناة السجل\n        if self.transcript_log_channel:\n            try:\n                embed = discord.Embed(\n                    title=\"📄 ترانسكريبت التكت\",\n                    description=f\"**التكت:** {ticket_channel.name}\\n**المنشئ:** <@{creator_id}>\\n**الادعي:** <@{claimed_by_id}>\",\n                    color=discord.Color.blue()\n                )\n                embed.set_footer(text=f\"تم الإغلاق في {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\")\n                await self.transcript_log_channel.send(embed=embed, file=discord.File(io.BytesIO(transcript.encode()), filename=\"transcript.txt\"))\n            except:\n                pass\n        \n        # حذف القناة\n        try:\n            await ticket_channel.delete(reason=\"تم إغلاق التكت\")\n        except:\n            pass\n        \n        del self.tickets[ticket_channel_id]\n    \n    def _generate_transcript(self, messages, channel_name):\n        \"\"\"إنشاء ترانسكريبت نصي\"\"\"\n        transcript = f\"=== ترانسكريبت التكت: {channel_name} ===\\n\"\n        transcript += f\"التاريخ: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n\"\n        \n        for message in messages:\n            transcript += f\"[{message.created_at.strftime('%H:%M:%S')}] {message.author}: {message.content}\\n\"\n            if message.attachments:\n                for attachment in message.attachments:\n                    transcript += f\"  [ملف: {attachment.filename}]\\n\"\n        \n        return transcript\n\nclass TicketView(discord.ui.View):\n    def __init__(self, cog):\n        super().__init__(timeout=None)\n        self.cog = cog\n    \n    @discord.ui.button(label=\"فتح تكت\", style=discord.ButtonStyle.green, emoji=\"🎫\")\n    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):\n        await self.cog.create_ticket(interaction)\n\nclass TicketActionView(discord.ui.View):\n    def __init__(self, cog, ticket_channel_id):\n        super().__init__(timeout=None)\n        self.cog = cog\n        self.ticket_channel_id = ticket_channel_id\n    \n    @discord.ui.button(label=\"إغلاق\", style=discord.ButtonStyle.red, emoji=\"❌\")\n    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):\n        if not interaction.user.guild_permissions.administrator and interaction.user.id != self.cog.tickets[self.ticket_channel_id][\"creator\"]:\n            await interaction.response.send_message(\"ليس لديك الصلاحية!\", ephemeral=True)\n            return\n        \n        embed = discord.Embed(\n            title=\"⏳ جاري إغلاق التكت...\",\n            description=\"سيتم إرسال الترانسكريبت...\",\n            color=discord.Color.yellow()\n        )\n        await interaction.response.send_message(embed=embed)\n        await self.cog.close_ticket(interaction, self.ticket_channel_id)\n    \n    @discord.ui.button(label=\"ادعي\", style=discord.ButtonStyle.blue, emoji=\"👤\")\n    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):\n        ticket_info = self.cog.tickets.get(self.ticket_channel_id)\n        if not ticket_info:\n            return\n        \n        if ticket_info[\"claimed_by\"]:\n            embed = discord.Embed(\n                title=\"❌ التكت بالفعل مدعي\",\n                description=f\"**المدعي:** <@{ticket_info['claimed_by']}>\",\n                color=discord.Color.red()\n            )\n            await interaction.response.send_message(embed=embed, ephemeral=True)\n            return\n        \n        ticket_info[\"claimed_by\"] = interaction.user.id\n        \n        embed = discord.Embed(\n            title=\"✅ تم ادعاء التكت\",\n            description=f\"**المدعي:** {interaction.user.mention}\",\n            color=discord.Color.green()\n        )\n        await interaction.response.send_message(embed=embed)\n    \n    @discord.ui.button(label=\"قفل\", style=discord.ButtonStyle.gray, emoji=\"🔒\")\n    async def lock_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):\n        if not interaction.user.guild_permissions.administrator:\n            await interaction.response.send_message(\"ليس لديك الصلاحية!\", ephemeral=True)\n            return\n        \n        channel = self.cog.bot.get_channel(self.ticket_channel_id)\n        if channel:\n            await channel.set_permissions(channel.guild.default_role, send_messages=False)\n            embed = discord.Embed(\n                title=\"🔒 تم قفل التكت\",\n                color=discord.Color.orange()\n            )\n            await interaction.response.send_message(embed=embed)\n    \n    @discord.ui.button(label=\"ترانسكريبت\", style=discord.ButtonStyle.blurple, emoji=\"📄\")\n    async def transcript(self, interaction: discord.Interaction, button: discord.ui.Button):\n        channel = self.cog.bot.get_channel(self.ticket_channel_id)\n        if not channel:\n            return\n        \n        # جمع الرسائل\n        messages = []\n        async for message in channel.history(limit=None, oldest_first=True):\n            messages.append(message)\n        \n        transcript = self.cog._generate_transcript(messages, channel.name)\n        \n        embed = discord.Embed(\n            title=\"📄 ترانسكريبت التكت\",\n            description=\"جاري إرسال الترانسكريبت...\",\n            color=discord.Color.blue()\n        )\n        await interaction.response.send_message(embed=embed, file=discord.File(io.BytesIO(transcript.encode()), filename=\"transcript.txt\"), ephemeral=True)\n\nasync def setup(bot):\n    await bot.add_cog(TicketSystem(bot))
