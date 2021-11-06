from discord.ext import commands
from .questions_messages import initial_question_embed_template, solved_question_embed_template, \
    close_question_embed_template
import config
import discord
import json
import os

here = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(here, 'stored_values.json')

try:
    with open(filename) as file:
        stored_questions = json.load(file)

except FileNotFoundError:
    stored_questions = {}

disciplines = ["Matemática", "Física", "Biologia", "Química", "Português", "Outras", "Geologia", "testes-do-bot"]


class question():
    def __init__(self, guild, member_id, channel_id, discipline_role_id, solved, sent_message_id):
        self.member = guild.get_member(member_id)
        self.channel = guild.get_channel(channel_id)
        self.discipline_role = guild.get_role(discipline_role_id)
        self.solved = solved
        self.sent_message_id = sent_message_id

    async def initial_question_message(self):
        emb = initial_question_embed_template()
        await self.channel.send(f"{self.discipline_role.mention}")
        self.sent_message_id = await self.channel.send(embed=emb) # Returns a message object
        self.sent_message_id = self.sent_message_id.id # Get the id of the object

    async def update_question_message(self, reacted_message_id):
        sent_message = await self.channel.fetch_message(self.sent_message_id)

        if self.solved:
            # Update the embed with new info
            reacted_message = await self.channel.fetch_message(reacted_message_id)
            emb = solved_question_embed_template(reacted_message)
            await sent_message.edit(embed=emb)

        else:
            # Reset the embed
            emb = initial_question_embed_template()
            await sent_message.edit(embed=emb)

    async def close_question_message(self):
        sent_message = await self.channel.fetch_message(self.sent_message_id)
        emb = close_question_embed_template()
        await sent_message.edit(embed=emb)

    def to_dict(self):
        return {
            "member": self.member.id,
            "channel": self.channel.id,
            "discipline_role": self.discipline_role.id,
            "solved": self.solved,
            "sent_message": self.sent_message_id
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

        # Member hasn't got active questions
        if member.id not in stored_questions or len(stored_questions[member.id]) == 0:
            return

        # Check if emoji is to close question
        if str(payload.emoji) == "✅":
            for member_id, stored_question in stored_questions.items():
                if stored_question is not None and stored_question["channel"] == payload.channel_id:
                    solved_question = question(
                        self.guild,
                        stored_question["member"],
                        stored_question["channel"],
                        stored_question["discipline_role"],
                        True,
                        stored_question["sent_message"]
                    )

                    await solved_question.update_question_message(payload.message_id)
                    stored_questions[member_id] = None

    @commands.command(name="ajuda", aliases=["pergunta", "dúvida", "questão"])
    async def open_question(self, ctx):
        member = ctx.message.author
        channel = ctx.message.channel
        discipline_name = None

        # Search in the disciplines list
        for discipline in disciplines:
            if discipline.lower() in channel.name:
                discipline_name = discipline

        # Return if no discipline was found
        if discipline_name is None:
            await channel.send("Este canal não é apropriado para iniciar questões.")
            return

        # Check if user has unanswered question
        if member.id in stored_questions:
            stored_question = stored_questions[member.id]

            if stored_question is not None:
                # Convert dict to question object
                closed_question = question(
                    self.guild,
                    stored_question["member"],
                    stored_question["channel"],
                    stored_question["discipline_role"],
                    True,
                    stored_question["sent_message"]
                )

                # Close question
                await closed_question.close_question_message()
                await member.send("⚠️ Foi criada uma nova questão. ⚠️\nA questão que já estava ativa foi fechada")
                stored_questions[member.id] = None

        # Create new message and add to dict
        discipline_role = discord.utils.get(member.guild.roles, name=discipline_name)
        new_question = question(self.guild, member.id, channel.id, discipline_role.id, False, None)
        await new_question.initial_question_message()
        stored_questions[member.id] = new_question.to_dict()

        # Store values in json file
        with open(filename, "w") as file:
            json.dump(stored_questions, file)


def setup(client):
    client.add_cog(questions(client))