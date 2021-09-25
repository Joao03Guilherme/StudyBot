from discord.ext import commands
from .questions_messages import initial_question_embed_template, solved_question_embed_template
import config
import discord
import json
import os


# TODO: Remove redundancies in the file
# TODO: Work with question objects or keep the dictionary, where is the bridge between both?

here = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(here, 'stored_values.json')

try:
    with open(filename) as file:
            stored_questions = json.load(file)

except FileNotFoundError:
    stored_questions = {}

disciplines = ["Matemática", "Física", "Biologia", "Química"]

class question():
    def __init__(self, member, channel, discipline_role, solved, sent_message):
        self.member = member
        self.channel = channel
        self.discipline_role = discipline_role
        self.solved = solved
        self.sent_message = sent_message

    async def send_question_message(self):
        emb = initial_question_embed_template()
        await self.channel.send(f"{self.discipline_role.mention}")
        self.sent_message = await self.channel.send(embed=emb)


    async def update_question_message(self, reacted_message):
        if self.solved:
            # Update the embed with new info
            emb = solved_question_embed_template(reacted_message)
            await self.sent_message.edit(embed=emb)

        else:
            # Reset the embed
            emb = initial_question_embed_template()
            await self.sent_message.edit(embed=emb)

    def to_dict(self):
        return {
            "member": self.member.id,
            "channel": self.channel.id,
            "discipline_role": self.discipline_role.id,
            "solved": self.solved,
            "sent_message": self.sent_message.id
        }


class questions(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.guild = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.client.get_guild(config.ID_GUILD)

    # Update questions status
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        member = payload.member

        if member.id not in stored_questions:
            return

        for stored_question in stored_questions[member.id]:
            if stored_question["channel"] == payload.channel_id and not stored_question["solved"]:
                current_question = question(
                    self.guild.get_member(stored_question["member"]),
                    self.guild.get_channel(stored_question["channel"]),
                    self.guild.get_role(stored_question["discipline_role"]),
                    True,
                    await self.guild.get_channel(stored_question["channel"]).fetch_message(stored_question["sent_message"])
                )

                await current_question.update_question_message(await self.guild.get_channel(stored_question["channel"]).fetch_message(payload.message_id))
                stored_question["solved"] = True


    @commands.command(name="ajuda")
    async def open_question(self, ctx):
        member = ctx.message.author
        channel = ctx.message.channel
        discipline_name = None

        # Search in the disciplines list
        for discipline in disciplines:
            if channel.name == discipline.lower():
                discipline_name = discipline

        discipline_role = discord.utils.get(member.guild.roles, name=discipline_name)
        new_question = question(member, channel, discipline_role, False, None)
        await new_question.send_question_message()

        if member.id in stored_questions:
            stored_questions[member.id].append(new_question.to_dict())
        else:
            stored_questions[member.id] = [new_question.to_dict()]

        # Store values in json file
        with open(filename, "w") as file:
            json.dump(stored_questions, file)

def setup(client):
    client.add_cog(questions(client))
