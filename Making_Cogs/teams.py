import asyncio
import random

from discord import app_commands, Embed, Interaction, ButtonStyle, Embed, Color
from discord.ext import commands
from discord.ui import Button, View, TextInput, Modal

class TeamAssignment:
    def __init__(self):
        self.required_people = 0
        self.team_count = 0
        self.team_sizes = []
        self.participants = set()
        self.command_issuer_id = None
        self.assignment_done = False

    async def split_teams(self):
        participant_list = list(self.participants)
        random.shuffle(participant_list)
        
        teams = []
        start_index = 0
        for size in self.team_sizes:
            teams.append(participant_list[start_index:start_index + size])
            start_index += size
        
        return teams

team_assignment = TeamAssignment()

team = app_commands.Group(name="team", description="チーム関連のコマンドなのだ")

@app_commands.command(name="join_list", description="ゲームのチーム分けを行います。")
@app_commands.describe(list_size="List of team sizes (comma separated)")
async def join_list(interaction: Interaction, list_size: str):
    button = Button(label="参加", style=ButtonStyle.primary, custom_id="join_button")
    execute_button = Button(label="実行", style=ButtonStyle.danger, custom_id="execute_button")
    cancel_button = Button(label="取消", style=ButtonStyle.secondary, custom_id="cancel_button")
    edit_button = Button(label="変更", style=ButtonStyle.primary, custom_id="edit_button")
    view = View()
    view.add_item(button)
    view.add_item(execute_button)
    view.add_item(cancel_button)
    view.add_item(edit_button)
    
    team_assignment.team_sizes = [int(size) for size in list_size.split(',')]
    team_assignment.team_count = len(team_assignment.team_sizes)
    team_assignment.required_people = sum(team_assignment.team_sizes)
    team_assignment.command_issuer_id = interaction.user.id
    
    message_content = f"ゲームのチーム分けを行います。\nチームは「{list_size.replace(',', '対')}」となります。\n"
    message_content += "参加の場合は「参加」ボタンを押してください！"

    await interaction.response.send_message(message_content, view=view)

@commands.Cog.listener()
async def on_interaction(inter: Interaction):
    try:
        if inter.data['component_type'] == 2:
            await on_button_click(inter)
    except KeyError:
        pass

async def on_button_click(inter: Interaction):
    if inter.data['custom_id'] == "execute_button":
        if inter.user.id != team_assignment.command_issuer_id:
            await inter.response.send_message("この操作はコマンドを使用したユーザーのみが実行できます。", ephemeral=True)
            return
        
        if len(team_assignment.participants) < team_assignment.required_people:
            await inter.response.defer(ephemeral=False)
            not_participants = await inter.followup.send("人数が不足しています。チーム分けをキャンセルしました。")
            await asyncio.sleep(5)
            await not_participants.delete()
        else:
            teams = await team_assignment.split_teams()
            embed = Embed(title="チーム分け結果", color=Color.green())
            for idx, team in enumerate(teams, start=1):
                team_members = "\n".join([participant.display_name for participant in team])
                embed.add_field(name=f"チーム {idx}", value=team_members, inline=False)
            await inter.response.send_message(embed=embed)
    elif inter.data['custom_id'] == "join_button":
        if team_assignment.assignment_done:
            await inter.response.send_message("チーム分けは既に終了しました。", ephemeral=True)
        else:
            user_id = inter.user
            if user_id not in team_assignment.participants:
                team_assignment.participants.add(user_id)
                embed = await update_participants_embed()
                await inter.message.edit(embed=embed)
                await inter.response.send_message("リストに追加しました。", ephemeral=True)
            else:
                await inter.response.send_message("すでにリストに含まれています。", ephemeral=True)
    elif inter.data['custom_id'] == "cancel_button":
        if inter.user.id == team_assignment.command_issuer_id:
            await inter.message.delete()
            team_assignment.participants.clear()
            team_assignment.assignment_done = False
            await inter.response.defer(ephemeral=False)
            cancel_message = await inter.followup.send("チーム分けがキャンセルされました。")
            await asyncio.sleep(5)
            await cancel_message.delete()
        else:
            await inter.response.send_message("この操作はコマンドを使用したユーザーのみが実行できます。", ephemeral=True)
    elif inter.data['custom_id'] == "edit_button":
        if inter.user.id != team_assignment.command_issuer_id:
            await inter.response.send_message("この操作はコマンドを使用したユーザーのみが実行できます。", ephemeral=True)
            return
        edit_modal = EditTeamSizesModal()
        await inter.response.send_modal(edit_modal)
        
class EditTeamSizesModal(Modal):
    def __init__(self):
        super().__init__(title="チームサイズの編集")
        self.team_sizes_input = TextInput(label="チーム各人数",placeholder='チームサイズをカンマで区切って入力してください', custom_id='team_sizes_input')
        self.add_item(self.team_sizes_input)
        
    async def on_submit(self, interaction: Interaction):
        team_sizes_str = self.team_sizes_input.value
        team_assignment.team_sizes = [int(size) for size in team_sizes_str.split(',')]
        team_assignment.team_count = len(team_assignment.team_sizes)
        team_assignment.required_people = sum(team_assignment.team_sizes)
        await interaction.response.send_message(f"チーム編成が更新されました。新しいチーム編成は\n「{team_sizes_str.replace(',', '対')}」です。", ephemeral=False)

async def update_participants_embed():
    participant_names = "\n".join(["・" + participant.display_name for participant in team_assignment.participants])
    embed = Embed(title=f"参加している人 (チーム数:{team_assignment.team_count})", description=f"{participant_names}", color=Color.blue())
    return embed