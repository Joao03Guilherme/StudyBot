import discord


EMBED_COLOR = 0x04caff

def initial_question_embed_template():
    emb = discord.Embed(title=f"Dúvida", color=EMBED_COLOR)
    emb.add_field(name="Status", value="Não resolvida")
    emb.set_footer(text="Se uma mensagem esclarecer a tua dúvida, reage a essa mensagem com ✅  para que outros "
                        "membros a possam localizar mais facilmente.")

    return emb

def solved_question_embed_template(message):
    emb = discord.Embed(title=f"Dúvida", color=EMBED_COLOR)
    emb.add_field(name="**Status**", value="Resolvida")
    emb.add_field(name="**Resolução**", value=f"Resolvido por {message.author.mention} nesta [mensagem]({message.jump_url})")

    return emb

