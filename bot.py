import discord
from discord.ext import commands
from discord import app_commands
import os

# ─────────────────────────────────────────
#  CONFIGURATION — modifie ces valeurs
# ─────────────────────────────────────────
GUILD_ID            = 671313137550753830   # ID de ton serveur
ANNOUNCE_CHANNEL_ID = 890677502169735179  # ID du salon principal (annonces votes)
ALLOWED_ROLES       = ["Modérateur", "Crieur"]  # Rôles autorisés à utiliser les commandes
# ─────────────────────────────────────────

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)
guild_obj = discord.Object(id=GUILD_ID)


def has_permission(interaction: discord.Interaction) -> bool:
    if interaction.user.guild_permissions.administrator:
        return True
    user_roles = [role.name for role in interaction.user.roles]
    return any(role in user_roles for role in ALLOWED_ROLES)


@bot.event
async def on_ready():
    await bot.tree.sync(guild=guild_obj)
    print(f"✅ LogoBattle Bot connecté en tant que {bot.user}")


# COMMANDE 1 : Supprimer toutes les réactions d'un fil
@bot.tree.command(
    guild=guild_obj,
    name="clear-reactions",
    description="Supprime toutes les réactions de tous les messages du fil actuel."
)
async def clear_reactions(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
        return
    if not isinstance(interaction.channel, discord.Thread):
        await interaction.response.send_message("❌ Cette commande doit être utilisée **dans un fil (thread)**.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True, thinking=True)
    thread = interaction.channel
    count = 0
    async for message in thread.history(limit=None):
        if message.reactions:
            for reaction in message.reactions:
                await message.clear_reaction(reaction.emoji)
            count += 1
    await interaction.followup.send(f"✅ Réactions supprimées sur **{count} message(s)** dans le fil **{thread.name}**.", ephemeral=True)


# COMMANDE 2 : Ajouter ✅ à tous les messages d'un fil
@bot.tree.command(
    guild=guild_obj,
    name="add-checkmark",
    description="Ajoute la réaction ✅ à tous les messages du fil actuel."
)
async def add_checkmark(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
        return
    if not isinstance(interaction.channel, discord.Thread):
        await interaction.response.send_message("❌ Cette commande doit être utilisée **dans un fil (thread)**.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True, thinking=True)
    thread = interaction.channel
    count = 0
    async for message in thread.history(limit=None):
        await message.add_reaction("✅")
        count += 1
    await interaction.followup.send(f"✅ Réaction ajoutée sur **{count} message(s)** dans le fil **{thread.name}**.", ephemeral=True)


# COMMANDE 3 : Annoncer le lancement des votes
@bot.tree.command(
    guild=guild_obj,
    name="announce-vote",
    description="Envoie l'annonce de lancement des votes dans le salon principal."
)
@app_commands.describe(
    lien_fil="Le lien du fil de vote de la semaine"
)
async def announce_vote(interaction: discord.Interaction, lien_fil: str):
    if not has_permission(interaction):
        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
        return
    channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
    if channel is None:
        await interaction.response.send_message("❌ Impossible de trouver le salon d'annonce.", ephemeral=True)
        return
    message = (
        "Hello  , J'espère que vous allez bien. 🤠\n\n"
        "Vous pouvez voter pour vos logos favoris en cliquant sur l'emoji ✅.\n\n"
        "**PS : On vous invite à lire le détail de chaque brief avant de faire votre choix.**\n\n"
        f"{lien_fil}\n\n"
        "*Fin des votes demain à 20h00.*\n\n"
        "Bonne chance et bon weekend à tous ! 🌞"
    )
    await channel.send(message)
    await interaction.response.send_message("✅ Annonce envoyée dans le salon principal !", ephemeral=True)


# Lancement du bot
token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise ValueError("❌ La variable d'environnement DISCORD_TOKEN est manquante !")

bot.run(token)
