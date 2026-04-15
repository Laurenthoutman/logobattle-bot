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


# ─────────────────────────────────────────
#  COMMANDE 1 : Supprimer toutes les réactions d'un fil
# ─────────────────────────────────────────
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
 

# ─────────────────────────────────────────
#  COMMANDE 2 : Ajouter ✅ à tous les messages d'un fil
# ─────────────────────────────────────────
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


# ─────────────────────────────────────────
#  COMMANDE 3 : Annoncer le lancement des votes
# ─────────────────────────────────────────
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
        "Hello <@&776417520503750748> , J'espère que vous allez bien. 🤠\n\n"
        "Vous pouvez voter pour vos logos favoris en cliquant sur l'emoji ✅.\n\n"
        "**PS : On vous invite à lire le détail de chaque brief avant de faire votre choix.**\n\n"
        f"{lien_fil}\n\n"
        "*Fin des votes demain à 20h00.*\n\n"
        "Bonne chance et bon weekend à tous ! 🌞"
    )
    await channel.send(message)
    await interaction.response.send_message("✅ Annonce des votes envoyée !", ephemeral=True)


# ─────────────────────────────────────────
#  COMMANDE 4 : Annoncer la nouvelle bataille
# ─────────────────────────────────────────
@bot.tree.command(
    guild=guild_obj,
    name="announce-bataille",
    description="Annonce le gagnant et la nouvelle bataille dans le salon principal."
)
@app_commands.describe(
    numero_bataille="Numéro de la bataille qui vient de se terminer (ex: 216)",
    mention_gagnant="Mention du gagnant (ex: @pseudo)",
    nombre_votes="Nombre de votes obtenus (ex: 12)",
    nom_gagnant="Nom affiché du gagnant (ex: Jean)",
    lien_nouvelle_bataille="Lien du fil de la nouvelle bataille",
    lien_logo_gagnant="Lien direct vers le logo gagnant"
)
async def announce_bataille(
    interaction: discord.Interaction,
    numero_bataille: int,
    mention_gagnant: str,
    nombre_votes: int,
    nom_gagnant: str,
    lien_nouvelle_bataille: str,
    lien_logo_gagnant: str
):
    if not has_permission(interaction):
        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
        return
    channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
    if channel is None:
        await interaction.response.send_message("❌ Impossible de trouver le salon d'annonce.", ephemeral=True)
        return
    message = (
        f"Hello <@&776417520503750748> , Bravo à tous les participants de la bataille **#{numero_bataille}**. 👏\n\n"
        f"Cette semaine c'est {mention_gagnant} qui a gagné la guerre avec **{nombre_votes} votes**. 🥳\n"
        f"**{nom_gagnant}** a donc pu choisir le thème de la nouvelle bataille. {lien_nouvelle_bataille}\n\n"
        f"Lien du logo gagnant :\n\n"
        f"{lien_logo_gagnant}\n\n"
        "Bonne semaine et bon travail à tous. 🌞\n"
        "*Pour accéder aux précédentes batailles, il vous suffit de cliquer en haut sur le bouton fil ( **#** )*\n\n"
        "🚧 En 2026, la Bataille débarque sur Instagram… et aura même son propre site web. "
        "Chaque lundi, vous y retrouverez les nouveaux thèmes, les gagnants auront droit à un post dédié, "
        "et nouveauté, il y aura des récompenses pour les participants. 🎁\n\n"
        "Je prépare aussi une grosse vidéo YouTube pour dévoiler la nouvelle identité de la Bataille et tout ce qui "
        "accompagne le projet (oui, il y aura bien plus que de simples concours de logos). "
        "Le tout est encore en construction, mais vous pouvez déjà vous abonner si ça vous tente. ☀️\n\n"
        "https://www.instagram.com/batailledelogos/"
    )
    await channel.send(message)
    await interaction.response.send_message("✅ Annonce de la nouvelle bataille envoyée !", ephemeral=True)


# ─────────────────────────────────────────
#  COMMANDE 5 : Nettoyer le salon des gagnants
# ─────────────────────────────────────────
@bot.tree.command(
    guild=guild_obj,
    name="clean-salon",
    description="Supprime tous les messages du salon des gagnants."
)
async def clean_salon(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True, thinking=True)

    channel = bot.get_channel(1482999485536800949)
    if channel is None:
        await interaction.followup.send("❌ Salon introuvable.", ephemeral=True)
        return

    deleted = 0
    async for message in channel.history(limit=None):
        try:
            await message.delete()
            deleted += 1
        except discord.Forbidden:
            await interaction.followup.send("❌ Le bot n'a pas la permission de supprimer des messages dans ce salon.", ephemeral=True)
            return
        except discord.HTTPException:
            pass

    await interaction.followup.send(f"✅ **{deleted} message(s)** supprimé(s) dans le salon des gagnants.", ephemeral=True)


# ─────────────────────────────────────────
#  Lancement du bot
# ─────────────────────────────────────────
token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise ValueError("❌ La variable d'environnement DISCORD_TOKEN est manquante !")

bot.run(token)
