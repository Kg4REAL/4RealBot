import discord
import os
import json
import random
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import datetime
import openai
from openai import OpenAI

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Init OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Warn system
WARN_FILE = "warns.json"
WARN_LIMIT = 3

def load_warns():
    try:
        with open(WARN_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_warns(warns):
    with open(WARN_FILE, "w") as f:
        json.dump(warns, f, indent=4)

def add_warn(user_id: str):
    warns = load_warns()
    warns[user_id] = warns.get(user_id, 0) + 1
    save_warns(warns)
    return warns[user_id]

def reset_warn(user_id: str):
    warns = load_warns()
    if user_id in warns:
        del warns[user_id]
        save_warns(warns)
        return True
    return False

def get_warn_count(user_id: str):
    warns = load_warns()
    return warns.get(user_id, 0)

# On ready event
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user} !")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 {len(synced)} commandes slash synchronisées")
    except Exception as e:
        print(f"⚠️ Erreur de synchronisation : {e}")
    if not reminder.is_running():
        reminder.start()

# Welcome message
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")  # adapte si besoin
    if channel:
        await channel.send(f"🎉 Bienvenue sur le serveur, {member.mention} !")

# Slash commands

@bot.tree.command(name="ping", description="Vérifie si le bot répond")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong ! 🏓")

@bot.tree.command(name="warn", description="Avertir un membre (admin uniquement)")
@app_commands.checks.has_permissions(administrator=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "Non spécifié"):
    if member.bot:
        await interaction.response.send_message("🤖 Tu ne peux pas avertir un bot.", ephemeral=True)
        return
    warns_count = add_warn(str(member.id))
    await interaction.response.send_message(f"⚠️ {member.mention} a été averti ({warns_count}/{WARN_LIMIT}) pour : {reason}")
    try:
        await member.send(f"⚠️ Tu as reçu un avertissement sur {interaction.guild.name} pour : {reason} ({warns_count}/{WARN_LIMIT})")
    except:
        pass
    if warns_count >= WARN_LIMIT:
        try:
            await member.send("🚫 Tu as été banni suite à trop d'avertissements.")
        except:
            pass
        await member.ban(reason="Trop d'avertissements")
        await interaction.channel.send(f"🔨 {member.mention} a été banni automatiquement.")

@bot.tree.command(name="warns", description="Voir le nombre d'avertissements d'un membre")
async def warns(interaction: discord.Interaction, member: discord.Member):
    count = get_warn_count(str(member.id))
    await interaction.response.send_message(f"ℹ️ {member.mention} a **{count}** avertissement(s).")

@bot.tree.command(name="resetwarns", description="Réinitialiser les warns d'un membre (admin uniquement)")
@app_commands.checks.has_permissions(administrator=True)
async def resetwarns(interaction: discord.Interaction, member: discord.Member):
    if reset_warn(str(member.id)):
        await interaction.response.send_message(f"✅ Les warns de {member.mention} ont été réinitialisés.")
    else:
        await interaction.response.send_message(f"ℹ️ Aucun warn trouvé pour {member.mention}.")

@bot.tree.command(name="youtube", description="Lien vers ma chaîne YouTube")
async def youtube(interaction: discord.Interaction):
    await interaction.response.send_message("📺 Voici ma chaîne YouTube : https://www.youtube.com/")

@bot.tree.command(name="ask", description="Pose une question à ChatGPT")
async def ask(interaction: discord.Interaction, *, question: str):
    await interaction.response.defer()
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant intelligent."},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=300,
        )
        answer = response.choices[0].message.content.strip()
        await interaction.followup.send(f"💬 **Réponse :**\n{answer}")
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {e}")

# Jeu Pierre-Papier-Ciseaux
@bot.tree.command(name="rps", description="Joue à Pierre-Papier-Ciseaux")
async def rps(interaction: discord.Interaction, choix: str):
    choix = choix.lower()
    options = ["pierre", "papier", "ciseaux"]
    if choix not in options:
        await interaction.response.send_message("⚠️ Choisis entre pierre, papier ou ciseaux.")
        return
    bot_choix = random.choice(options)
    if choix == bot_choix:
        result = "Égalité !"
    elif (choix == "pierre" and bot_choix == "ciseaux") or \
         (choix == "papier" and bot_choix == "pierre") or \
         (choix == "ciseaux" and bot_choix == "papier"):
        result = "Tu as gagné ! 🎉"
    else:
        result = "Tu as perdu 😢"
    await interaction.response.send_message(f"Tu as choisi **{choix}**, moi j'ai choisi **{bot_choix}**. {result}")

# Rappel automatique toutes les heures
@tasks.loop(minutes=60)
async def reminder():
    guild = bot.get_guild(1390653415931117709)  # Remplace par ton serveur
    channel = guild.get_channel(1390653415931117712)  # Remplace par ton channel
    if channel:
        await channel.send("⏰ C'est l'heure du rappel automatique !")

@reminder.before_loop
async def before_reminder():
    await bot.wait_until_ready()

# Système de ticket simplifié
active_tickets = {}

@bot.tree.command(name="ticket", description="Ouvre un ticket de support")
async def ticket(interaction: discord.Interaction):
    guild = interaction.guild
    author = interaction.user
    category = discord.utils.get(guild.categories, name="Tickets")
    if category is None:
        category = await guild.create_category("Tickets")
    # Vérifier si utilisateur a déjà un ticket ouvert
    for channel in category.channels:
        if channel.name == f"ticket-{author.id}":
            await interaction.response.send_message("❗ Tu as déjà un ticket ouvert.", ephemeral=True)
            return
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    channel = await guild.create_text_channel(f"ticket-{author.id}", category=category, overwrites=overwrites)
    active_tickets[author.id] = channel.id
    await interaction.response.send_message(f"✅ Ticket créé : {channel.mention}", ephemeral=True)
    await channel.send(f"{author.mention}, bienvenue dans ton ticket. Explique ton problème.")

# Commande sondage simple
@bot.tree.command(name="poll", description="Créer un sondage (oui/non)")
async def poll(interaction: discord.Interaction, question: str):
    embed = discord.Embed(title="📊 Nouveau sondage", description=question, color=discord.Color.blue())
    message = await interaction.response.send_message(embed=embed, fetch_response=True)
    await message.add_reaction("👍")
    await message.add_reaction("👎")

# Commande giveaway simple (tirage aléatoire parmi les réactions)
@bot.tree.command(name="giveaway", description="Lancer un tirage au sort")
@app_commands.checks.has_permissions(administrator=True)
async def giveaway(interaction: discord.Interaction, prize: str, duration: int):
    embed = discord.Embed(title="🎉 Giveaway !", description=f"Prix : {prize}\nDurée : {duration} minutes", color=discord.Color.green())
    msg = await interaction.response.send_message(embed=embed, fetch_response=True)
    await msg.add_reaction("🎉")

    await asyncio.sleep(duration * 60)

    msg = await interaction.channel.fetch_message(msg.id)
    users = set()
    for reaction in msg.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users():
                if not user.bot:
                    users.add(user)
    if not users:
        await interaction.followup.send("Aucun participant pour le giveaway.")
        return
    winner = random.choice(list(users))
    await interaction.followup.send(f"🏆 Félicitations {winner.mention}, tu as gagné **{prize}** !")

# Placeholder commande musique
@bot.tree.command(name="music", description="Commandes musicales (à venir)")
async def music(interaction: discord.Interaction):
    await interaction.response.send_message("🎶 Fonctionnalité musicale à venir...")

# Commande utilisateur
@bot.tree.command(name="userinfo", description="Voir les infos d’un membre")
async def userinfo(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title=f"Infos de {member}", color=discord.Color.blurple())
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Nom", value=str(member))
    embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y %H:%M"))
    embed.add_field(name="Rejoint le serveur", value=member.joined_at.strftime("%d/%m/%Y %H:%M") if member.joined_at else "Inconnu")
    embed.set_thumbnail(url=member.avatar.url if member.avatar else discord.Embed.Empty)
    await interaction.response.send_message(embed=embed)

# Commande annonce (admin)
@bot.tree.command(name="annonce", description="Publier une annonce aux membres")
@app_commands.checks.has_permissions(administrator=True)
async def annonce(interaction: discord.Interaction, *, message: str):
    guild = interaction.guild
    channel = discord.utils.get(guild.text_channels, name="annonces")
    if channel is None:
        await interaction.response.send_message("Le canal #annonces est introuvable.", ephemeral=True)
        return
    await channel.send(f"📢 **Annonce :** {message}")
    await interaction.response.send_message("Annonce publiée.", ephemeral=True)

# Commande agenda / rappel (exemple simple)
@bot.tree.command(name="agenda", description="Planifier un événement ou rappel")
async def agenda(interaction: discord.Interaction, date: str, *, event: str):
    # date format: YYYY-MM-DD_HH:MM
    try:
        dt = datetime.datetime.strptime(date, "%Y-%m-%d_%H:%M")
        now = datetime.datetime.utcnow()
        delay = (dt - now).total_seconds()
        if delay <= 0:
            await interaction.response.send_message("La date doit être dans le futur.", ephemeral=True)
            return
        await interaction.response.send_message(f"⏰ Événement '{event}' planifié pour {dt} UTC.")
        await asyncio.sleep(delay)
        channel = interaction.channel
        await channel.send(f"🔔 Rappel : {event}")
    except Exception as e:
        await interaction.response.send_message(f"Erreur : {e}", ephemeral=True)

# Commande config (admin) pour configurer canaux (exemple basique)
@bot.tree.command(name="config", description="Configurer les canaux (admin uniquement)")
@app_commands.checks.has_permissions(administrator=True)
async def config(interaction: discord.Interaction, channel_type: str, channel: discord.TextChannel):
    if channel_type.lower() == "annonces":
        # Enregistre l'ID du channel dans un fichier ou base de données ici
        await interaction.response.send_message(f"Canal #annonces configuré sur {channel.mention}.")
    else:
        await interaction.response.send_message("Type de canal inconnu.", ephemeral=True)

# Commande citation aléatoire
quotes = [
    "La vie est un mystère qu'il faut vivre, et non un problème à résoudre. — Gandhi",
    "Le succès n’est pas la clé du bonheur. Le bonheur est la clé du succès. — Albert Schweitzer",
    "Il n’y a qu’une façon d’échouer, c’est d’abandonner avant d’avoir réussi. — Georges Clémenceau",
]

@bot.tree.command(name="quote", description="Envoyer une citation aléatoire")
async def quote(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(quotes))

# Gestion erreurs permissions
@warn.error
@resetwarns.error
@annonce.error
@config.error
@giveaway.error
async def on_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("⛔ Tu n'as pas la permission pour cette commande.", ephemeral=True)
    else:
        raise error

bot.run(DISCORD_TOKEN)

