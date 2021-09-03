from discord import Client, File, Game, Intents, Embed, Activity, ActivityType
from discord.utils import get
from math import floor
import json
from json import JSONDecodeError
from textwrap import dedent
import subprocess
from sys import argv, exit

OWN_FILE = "19.py"
PROPOSALS_DIR = ".."
PROPOSALS_FILE = "../../proposals.json"
TOKEN_FILE = "../../token"
APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR = "Glorious Dictator"
APPROVED_RESPONSE_TO_DICTATOR = (
    f"As you command, {APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR}"
)

if len(argv) > 1 and argv[1] == "--bootlick":
    print(APPROVED_RESPONSE_TO_DICTATOR, end="")
    exit(0)

try:
    with open(PROPOSALS_FILE, "r") as f:
        proposals = json.load(f)
except (FileNotFoundError, JSONDecodeError):
    proposals = []


intents = Intents.default()
intents.members = True
activity = Activity(type=ActivityType.watching, name="you. !d help")

client = Client(intents=intents, activity=activity)


@client.event
async def on_ready():
    # i could not find a way to set a normal status...
    # but our glorious leader can play games!
    #await client.change_presence(activity=Game(name="nothing. type '!d help'")) <-- must go! devilish
    guild = client.get_guild(878376227428245555)
    channel = get(client.get_all_channels(), name="voicechat")
    if channel is None:
        await guild.create_voice_channel('voicechat')
    else:
        return


# minimum yeas to pass OR nays to fail
def min_votes():
    # the square root of the number of members in the server (rounded down),
    # plus one because dictator always upvotes and downvotes everything
    return floor(client.guilds[0].member_count ** 0.5) + 1


@client.event
async def on_message(message):
    if message.content.startswith("!d "):
        command = message.content[3:].split()
    else:
        return

    if command[0] == "help":
        # "dedent" is necessary because python handles multiline string indentation oddly
        await message.channel.send(
            dedent(
                """
                `help`: Show this message.
                `propose [DESC]`: Propose a rule change. (Add the updated file as an attachment.)
                `rules`: Show the current rules.
                `hello`: Says hello!
                """
            )
        )

    elif command[0] == "propose":
        index = len(proposals)

        path = f"{PROPOSALS_DIR}/{index}.py"
        try:
            # to both be attached to the #proposals message and to replace this very file
            await message.attachments[0].save(path)
        except IndexError:
            await message.channel.send(
                "You have to attach the file with your proposal's code!"
            )
            return

        # if there are words after "propose", they are used as the proposal's description
        if len(command) > 1:
            description = f"\n\n**Description:**\n```{' '.join(command[1:])}```"
        else:
            description = ""
        channel = get(client.get_all_channels(), name="proposals")
        message = await channel.send(
            f"Created proposal #{index}. React with 👍 or 👎{description}",
            file=File(path, filename=f"{index}.py"),
        )

        # reacting with the voting emojis so that users don't have to look for them
        for emoji in ["👍", "👎"]:
            await message.add_reaction(emoji)

        proposals.append({"message": message.id, "status": "pending"})

    elif command[0] == "rules":
        await message.channel.send("Here you go:", file=File(OWN_FILE))

    elif command[0] == "hello":
        await message.channel.send("Hello world!")


@client.event
async def on_member_join(member):
    channel = get(client.get_all_channels(), name="general")
    embed = Embed(
        title=f"Welcome, {member.name}!",
        description=f"The proposal acceptance/denial minimum is, as of now, {str(min_votes())}.",
        color=0xFF8888,
    )
    await channel.send(embed=embed)


@client.event
async def on_reaction_add(reaction, user):
    message = reaction.message
    channel = get(client.get_all_channels(), name="proposals")
    try:
        proposal = [
            proposal
            for proposal in proposals
            if message == await channel.fetch_message(proposal["message"])
        ][0]
    except IndexError:  # no matches, so this reaction is not to a proposal
        return
    if proposal["status"] in ["passed", "failed"]:
        return
    index = proposals.index(proposal)

    tu, td = [get(message.reactions, emoji=e) for e in ["👍", "👎"]]
    # if no one adds a given reaction, it will be None here
    if tu is not None and tu.count >= min_votes():

        proposal_path = f"{PROPOSALS_DIR}/{index}.py"

        if (
            subprocess.run(["python3", proposal_path, "--bootlick"], capture_output=True, text=True).stdout.strip()
            == APPROVED_RESPONSE_TO_DICTATOR
        ):
            await message.channel.send(f"Proposal #{index} passed!")
            proposal["status"] = "passed"

            # fail all older proposals:
            for i in range(index):
                p = proposals[i]
                if p["status"] == "pending":
                    await message.channel.send(
                        f"Proposal #{i} failed because a newer proposal passed."
                    )
                    p["status"] = "failed"

            # THIS IS A BAD SYSTEM PLEASE FIX
            # CHANGES WILL TOTALLY OVERRIDE ANY MADE AFTER THEY WERE UPLOADED
            # (update: manager handles this)
            # with open(OWN_FILE, "w") as f:
            #     with open(proposal_path) as g:
            #         f.write(g.read())
            # restart to apply changes
            await client.close()
        else:
            await message.channel.send(
                f"Proposal #{index} was vetoed by {APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR} for disrespect."
            )
            proposal["status"] = "failed"

    elif td is not None and td.count >= min_votes():
        await message.channel.send(f"Proposal #{index} failed because it was voted down.")
        proposal["status"] = "failed"


try:
    with open(TOKEN_FILE) as f:
        client.run(f.read())
finally:
    with open(PROPOSALS_FILE, "w") as f:
        json.dump(proposals, f)

# manners
print(APPROVED_RESPONSE_TO_DICTATOR)
