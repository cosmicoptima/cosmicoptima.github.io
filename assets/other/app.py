from __future__ import annotations
from abc import ABC, abstractmethod
from asyncio import create_task, sleep as async_sleep
from asyncio.tasks import gather
from copy import deepcopy
from datetime import datetime, time
from discord import (
    Activity,
    ActivityType,
    ChannelType,
    Client,
    Embed,
    File,
    Intents,
    Member,
    Message,
    PermissionOverwrite,
    TextChannel,
    Colour,
    Permissions,
    Role,
    Guild,
)
from discord.abc import GuildChannel
from discord.ext import tasks, commands
from discord.utils import get
import emoji_list
from enum import IntEnum, unique
import json
from json import JSONDecodeError
from math import ceil, floor, isnan
from numpy import median, linalg as la, random as rand
import numpy as np
from pickle import dumps, loads
import random
import randomcolor
import re
import requests
import sqlite3
from sqlite3 import Error
import string
import subprocess
from sys import argv, exit, exc_info
from textwrap import dedent
from traceback import format_exception, format_tb
from typing import Dict, Iterator, List, Optional, Set, Tuple, TypeVar, Union
import urllib.request


# file names
OWN_FILE = "app.py"
PROPOSALS_DIR = "data/proposals"
DATABASE_FILE = "data/base.sqlite3"
PROPOSALS_FILE = "data/proposals.json"
AGENTS_FILE = "data/agents.json"
DEALS_FILE = "data/deals.json"
PLACES_FILE = "data/channels.json"
RESTART_DATA_FILE = "data/restart.json"
TOKEN_FILE = "data/token"

# channel names
GENERAL_CHANNEL_NAME = "general"
PROPOSALS_CHANNEL_NAME = "proposals"
PROFILES_CHANNEL_NAME = "profiles"
VOICE_CHANNEL_NAME = "voicechat"
LOG_CHANNEL_NAME = "debug"
EVENTS_CHANNEL_NAME = "events"
MOODS_CHANNEL_NAME = "moods"


COMMAND_PREFIX = random.choices(
    population=[
        "!d ",
        random.choice("-.,?$%/*+:¿"),
        random.choice(string.ascii_lowercase),
    ],
    weights=[0.0, 0.1, 0.9],
    k=1,
)[0]
APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR = "Glorious Dictator"
APPROVED_RESPONSE_TO_DICTATOR = (
    f"As you command, {APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR}"
)
# Limit to characters in profile command self-description

MAX_CHARACTERS_IN_SELFDESCRIPTION = 500

MOODS = (
    "happiness sadness anger fear relief jealousy hope frustration pride nervousness awe courage bliss curiousity enthusiasm joy degrence humber nage dorcelessness andric varination ponnish harfam kyne trantiveness teluge onlent loric"
).split()

MOOD_EMOJI = {
    "happiness": "🙂",
    "sadness": "😔",
    "anger": "😠",
    "fear": "😨",
    "relief": "😌",
    "jealousy": "🙄",
    "hope": "🤤",
    "frustration": "😖",
    "pride": "😎",
    "nervousness": "😓",
    "awe": "🤯",
    "courage": "😉",
    "bliss": "☺",
    "curiousity": "🧐",
    "enthusiasm": "😃",
    "joy": "😂",
    "degrence": "🥴",  # TODO: replace with the good one
}

INITIAL_ROLE_PRICE = 10
BASE_IN_ROLE_PRICE_CALCULATION = 1.1
ROLE_TAX = 1.1

# P_DICTATOR_REACTS = 0.01
def p_dictator_reacts():
    # return 0.1 * get_mood("varination") ** 2
    return mood(0.05, varination=2, enthusiasm=1, courage=1)


# The probability of a random event FROM A MESSAGE. This is independent to the chance from the timer.
# This is to allow a form of weighting; triggering more random events when the server is more active
# P_RANDOM_EVENT = 0.06
def p_random_event():
    # return 0.4 * get_mood("varination") ** 2
    return mood(0.2, varination=1)


# Number of expected seconds between events caused by timers
# TARGET_SECONDS_BETWEEN_TIMER_EVENTS = 60 * 60 * 4
def target_seconds_between_timer_event():
    # return 900 / get_mood("enthusiasm") ** 2
    return mood(900, enthusiasm=-1, harfam=0.5, hope=0.2)


# Ensure these weights add up to 1, maybe? Or it might not be an issue... just in case.
WEIGHT_RANDOM_EVENT_IS_TRADE = 0.75
WEIGHT_RANDOM_EVENT_IS_PAST = 0.15
WEIGHT_RANDOM_EVENT_IS_PRAISE = 0.10
PAST_EVENT_MIN_REWARD = 1
PAST_EVENT_MAX_REWARD = 5
# Ensure this remains less than 0.50 or some breakage may occur
# P_PAST_EVENT_IS_NEUTRAL = 0.20
def p_past_event_is_neutral():
    return mood(0.2, pride=-1)


CREDIT_FOR_AUTHORING_SUCCESSFUL_PROPOSAL = 5  # TODO: not in use yet
CREDIT_FOR_VOTING_PROPOSAL_SUCCESSFULLY = 1  # TODO: not in use yet

WHIM_SECONDS = 5.0

# The amount to additionally downscale the worth of goods given to the recombobulate command.
# RECOMBOB_RATIO = 1
def recombob_ratio():
    # return 0.4 / (1.2 - get_mood("harfam"))
    return mood(0.4, harfam=1)


def inc_amount():
    # return 0.5 / (1.1 - get_mood("harfam"))
    return mood(1, harfam=1, joy=0.5, enthusiasm=0.2, dorcelessness=-1.5)


WEBHOOK_NAME = "impersonate"

WORDS = "understandings|understanding|conversations|disappearing|informations|grandmothers|grandfathers|questionings|conversation|information|approaching|understands|immediately|positioning|questioning|grandmother|travellings|questioners|recognizing|recognizers|televisions|remembering|rememberers|expressions|discovering|disappeared|interesting|grandfather|straightest|controllers|controlling|considering|remembered|cigarettes|companying|completely|spreadings|considered|continuing|controlled|stationing|controller|straighter|stretching|businesses|somebodies|soldiering|countering|darknesses|situations|directions|disappears|younglings|suggesting|afternoons|breathings|distancing|screenings|schoolings|especially|everything|everywhere|explaining|explainers|expression|branchings|revealings|repeatings|surprising|rememberer|somewheres|television|themselves|recognizer|recognizes|recognized|belongings|finishings|travelling|questioner|beginnings|travelings|questioned|followings|pretending|forgetting|forgetters|forwarding|positioned|travellers|gatherings|perfecting|understand|understood|weightings|approaches|officering|numberings|happenings|mentioning|letterings|husbanding|imaginings|approached|apartments|whispering|interested|discovered|spinnings|clearings|climbings|spendings|clothings|colorings|soundings|truckings|somewhere|troubling|companies|companied|beautiful|computers|confusing|considers|travelers|youngling|continues|continued|traveller|traveling|yellowing|apartment|beginning|wheelings|travelled|sometimes|something|appearing|cornering|believing|countered|believers|countries|soldiered|coverings|creatures|crossings|accepting|daughters|belonging|situation|silvering|different|silencing|touchings|bettering|tomorrows|disappear|thinkings|boardings|discovers|admitting|wrappings|distances|distanced|sightings|shrugging|doctoring|showering|shoulders|shoppings|shootings|dressings|sheetings|shadowing|settlings|servicing|seriously|seconding|searching|weighting|screening|screaming|schooling|teachings|bothering|everybody|botherers|bottoming|excepting|expecting|explained|direction|explainer|surprised|surprises|waterings|branching|revealing|returning|surfacing|familiars|repeating|fathering|reminding|supposing|breasting|attacking|remembers|breathing|remaining|breathers|brightest|brownings|suggested|recognize|fightings|attention|figurings|receiving|reasoning|realizing|fingering|buildings|finishing|stupidest|stuffings|questions|watchings|flashings|strongest|strikings|flighting|flowering|promisers|promising|following|bathrooms|prettiest|pretended|stretched|foreheads|foresting|stretches|forgotten|pressings|forgetter|strangest|preparing|forwarded|strangers|possibles|positions|afternoon|straights|pocketing|gardening|pleasings|wondering|gathering|picturing|personals|perfected|stomaches|stomached|carefully|stationed|catchings|parenting|paintings|orderings|groupings|wintering|officered|offerings|centering|numbering|neighbors|certainly|happening|narrowing|narrowest|mountains|mothering|mirroring|middlings|messaging|standings|mentioned|mattering|marriages|histories|machining|hospitals|listening|lightings|springing|lettering|husbanded|spreaders|whispered|imagining|imaginers|spreading|important|languages|answering|cigarette|interests|spiriting|cleanings|knockings|soundest|coatings|sounders|sounding|colleges|coloring|colorful|wouldn't|training|colorers|sorriest|worrying|belonged|approach|tracking|touchers|touching|computer|whatever|toppings|confused|confuses|workings|consider|bettered|teething|tonights|tonguers|tonguing|continue|arriving|tomorrow|controls|together|blacking|blackest|throwers|blocking|throwing|coolings|someones|blockers|somebody|thirties|soldiers|cornered|weighted|counting|thoughts|counters|thinking|thinners|thinning|coursing|covering|thinnest|craziest|snapping|creating|creature|thickest|boarding|crossing|smokings|crowding|smelling|smallest|cuttings|slipping|slightly|dancings|sleepers|sleeping|slamming|wordings|darkness|daughter|boatings|skinning|weddings|thanking|sittings|deciding|deciders|singling|singings|despites|simplest|terrible|silvered|tellings|wearings|youngest|watering|silences|teachers|bookings|agreeing|teaching|discover|attacked|bothered|botherer|watching|swingers|bottling|distance|silenced|signings|bottomed|sighting|shutting|shrugged|wondered|swinging|doctored|sweetest|showered|showings|doorways|shouting|shoulder|wronging|shortest|surprise|dragging|shopping|shooters|drawings|actually|shooting|dreaming|dressing|avoiding|shitting|shirting|shipping|drinking|drinkers|braining|sheeting|sharpest|drivings|sharpers|dropping|droppers|shadowed|surfaced|settling|washings|settings|services|serviced|earliest|backings|earthing|servings|branches|branched|seconded|seatings|surfaces|searched|searches|walkings|screened|waitings|screamed|supposed|emptiest|emptying|breaking|breakers|schooled|enjoying|enjoyers|entering|runnings|breasted|rounders|rounding|supposes|everyone|visitors|visiting|breathed|excepted|roofings|exciting|breathes|expected|rollings|bankings|breather|explains|villages|bridging|viewings|brighter|ringings|righting|suitings|bringing|revealed|bringers|returned|failings|repliers|replying|repeated|brothers|familiar|wintered|families|suggests|farthest|furthest|browning|fathered|removing|building|reminded|bathroom|allowing|suddenly|remember|allowers|feedings|builders|burnings|feelings|remained|refusing|stupider|windings|although|stuffing|studying|business|angriest|fighting|fighters|students|figuring|received|twenties|receives|fillings|reasoned|findings|stronger|turnings|realizes|realized|readiest|fingered|readying|striking|trusters|finishes|trusting|finished|readings|reachers|reaching|quieters|quietest|quieting|fittings|quickest|writings|beaching|question|trucking|callings|stranger|flashing|beatings|answered|flattest|flatting|flighted|straight|troubled|flowered|pullings|storming|promiser|couldn't|promised|promises|couldn’t|followed|stoppers|problems|probably|prettier|stopping|pretends|stomachs|troubles|pressers|tripping|forehead|stickers|forested|pressing|whispers|carrying|sticking|carriers|stepping|stealers|forwards|stealing|becoming|prepares|prepared|powering|freeings|stations|possible|position|freshest|beddings|wrapping|fronting|catching|fuckings|policing|funniest|pointers|pointing|catchers|pocketed|gardened|starters|ceilings|pleasing|gathered|starting|centered|platings|plastics|planning|pictured|pictures|traveler|pickings|personal|glancing|yourself|chancing|perfects|changing|peopling|partying|partings|parented|grabbing|grabbers|changers|checking|starring|bedrooms|checkers|pairings|standing|painting|outsides|greatest|cheeking|greening|greenest|grouping|ordering|anything|openings|guarding|wheeling|officers|guessing|spreader|offering|children|anywhere|numbered|choicest|noticers|noticing|hallways|nothings|hangings|nobodies|admitted|neighbor|choosing|choosers|happened|neckings|happiest|narrowed|narrower|spotting|churches|mouthing|traveled|mountain|mothered|accepted|mornings|mirrored|headings|spirited|hearings|heatings|circling|middling|messaged|messages|heaviest|wouldn’t|spinners|mentions|helpings|cleanest|memories|meetings|meanings|appeared|mattered|marrieds|marrying|marriage|yellowed|markings|cleaning|managing|cleaners|holdings|machined|machines|lunching|luckiest|lowering|longings|clearest|hospital|lockings|littlest|clearing|listened|housings|lightest|lighting|lighters|spinning|hundreds|hurrying|believes|spenders|believed|climbing|husbands|lettered|lettings|learning|leadings|ignoring|laughing|ignorers|imagines|yellower|imagined|climbers|imaginer|spending|closings|specials|speakers|language|believer|clothing|clouding|speaking|interest|spacings|landings|knowings|southest|jacketed|knocking|kitchens|kissings|killings|keepings|dresses|biggest|sticker|careful|shirted|warmers|shipped|birding|drinker|carries|sheeted|warming|carried|carrier|driving|sharper|tonight|drivers|casings|sharers|sharing|stepped|dropped|dropper|whisper|shapers|shaping|shakers|shaking|tonguer|shadows|stealer|several|tongued|staying|settles|settled|dusting|setting|tongues|catting|backing|catches|earlier|warmest|earthed|service|serving|warring|wanters|catcher|serious|eastest|sensing|senders|easiest|sending|sellers|selling|seeming|seeings|tiniest|seconds|station|causing|seating|edgings|stating|timings|efforts|starter|causers|screens|blacker|ceiling|screams|centers|wanting|walling|walkers|certain|emptied|empties|emptier|thrower|endings|started|schools|scarers|scaring|sayings|engines|savings|sanding|enjoyed|starers|saddest|enjoyer|staring|enoughs|rushing|bagging|runners|entered|running|chances|entires|chancer|rubbing|rowings|rounder|chanced|rounded|starred|rooming|changed|changes|blocked|angrier|exactly|changer|blocker|excepts|checked|excited|walking|excites|roofing|through|expects|blooded|checker|cheeked|throats|explain|wakings|springs|thought|waiting|blowing|rolling|rocking|risings|ringing|baggers|animals|righter|righted|ridings|richest|facings|reveals|blowers|choicer|choices|returns|voicing|worries|resting|chooses|failing|spreads|replier|failers|falling|spotted|replies|replied|chooser|thinned|fallers|thinner|balling|boarded|repeats|visitor|farther|further|circles|another|removed|fastest|removes|fathers|thicker|circled|visited|reminds|fearing|spirits|classes|answers|banking|boating|cleaned|feeding|spinner|thanked|village|worried|feeling|cleaner|remains|cleared|refuses|refused|workers|reddest|telling|yellows|spender|working|clearer|clearly|climbed|tearing|fighter|teaming|figured|figures|booking|viewing|climber|usually|closest|receive|filling|teacher|reasons|closing|finally|closers|anybody|finding|anymore|realize|special|finders|booting|realest|clothed|readier|readies|readied|fingers|teaches|tallest|clothes|speaker|readers|talkers|clouded|talking|reading|firings|spacing|takings|reacher|reached|coating|reaches|raising|raining|fishing|quietly|fittest|fitting|systems|whether|bothers|wrapped|fitters|quieted|quieter|quickly|coffees|quicker|fixings|coldest|sounded|sounder|actings|anyways|college|flashed|flashes|bottles|flatter|flatted|colored|bottled|wording|turning|sorting|flights|colorer|putting|pushers|pushing|flowers|pullers|swinger|wonders|sorrier|pulling|proving|comings|bottoms|promise|truster|boxings|company|follows|younger|trusted|sweeter|yelling|problem|without|beached|footing|confuse|beaches|brained|bearing|pretend|trucked|forcing|presser|wishing|trouble|forests|appears|beating|airings|forever|surface|control|forgets|accepts|pressed|wronged|winters|forming|presses|prepare|beaters|breaker|wheeled|because|forward|coolers|cooling|allowed|powered|pourers|freeing|pouring|tripped|coolest|breasts|someone|fresher|suppose|somehow|friends|breaths|copping|fronted|becomes|porches|poppers|popping|poorest|treeing|fucking|fullest|pooling|breathe|polices|funnier|funnies|policed|bedding|corners|futures|pointer|pointed|gamings|counted|soldier|pockets|wetting|pleased|gardens|wetters|wettest|pleases|counter|sunning|players|westest|country|gathers|bridges|playing|plating|bridged|plastic|couples|softest|getting|planned|getters|placing|gifting|pinking|pilings|piecing|picture|coursed|courses|summers|picking|snowing|phoning|bedroom|glances|glanced|winging|snapped|glassed|glasses|perhaps|covered|crazies|crazier|perfect|peopled|persons|peoples|suiting|pausing|passing|goldest|partied|windows|parties|parting|creates|grabbed|smokers|created|grabber|brought|weights|bringer|arrives|crosser|crosses|grasses|parents|palming|graying|pairing|crossed|painted|arrived|greying|smoking|paining|outside|brother|greater|smilers|outings|greened|greener|crowded|travels|smiling|ordered|grounds|offings|smelled|openers|browner|grouped|opening|smaller|growing|okaying|officer|guarded|slowest|slowing|cupping|slipped|guessed|guesses|cutting|offices|gunning|offered|browned|allower|nursing|numbing|suggest|cutters|numbers|sliders|halving|sliding|noticer|wedding|notices|noticed|nothing|writers|hallway|handing|sleeper|normals|noising|hanging|nodding|dancing|wearing|writing|slammed|hangers|darkest|skinned|happens|trained|needing|builder|beliefs|happier|necking|nearest|hardest|nearing|burning|believe|winding|hatting|narrows|stupids|sitting|mouthed|deadest|watered|sisters|mothers|singled|winning|morning|mooning|moments|heading|missing|decides|decided|decider|mirrors|minutes|hearing|minings|already|minding|middled|heating|burners|singles|middles|deepest|stuffed|heaters|singing|simpler|heavier|heavies|belongs|message|despite|mention|simples|studies|studied|silvers|helping|helpers|members|meeting|willing|meanest|attacks|herself|meaning|dinners|student|hidings|matters|marries|married|busying|busiest|silence|against|highest|wildest|hilling|marking|mapping|manages|managed|himself|history|tracked|strikes|manning|hitting|makings|hitters|whiting|towards|watched|holding|toucher|machine|holders|lunches|lunched|watches|luckier|stretch|streets|lowered|loudest|lookers|looking|longing|calling|longest|locking|bending|washing|signing|hottest|littler|benders|strange|sighted|listens|linings|likings|housing|beneath|sighing|sicking|however|lighted|sickest|lighter|calming|lifters|hundred|calmest|hurried|hurries|lifting|touched|doesn't|doesn’t|hurting|touches|showers|husband|doctors|letters|cameras|letting|tossing|leaving|learned|dogging|leaning|leafing|leaders|leading|whitest|layered|ignored|showing|ignores|stories|ignorer|shoving|laughed|lasting|largest|imaging|doorway|besting|imagine|shouted|stormed|downing|storing|topping|avoided|dragged|shorter|betters|stopper|landers|insides|instead|written|drawing|shopped|stopped|between|landing|shooter|knowing|jackets|dreamed|carding|toothed|knocked|knifing|kitchen|joining|teethed|stomach|joiners|kissing|kindest|killers|killing|shoeing|kidding|jumping|kickers|kicking|jumpers|keepers|dressed|keeping|enough|checks|kicked|jumper|kicker|kidded|jumped|killed|joking|killer|kinder|joiner|kisses|kissed|joined|knives|knifes|knifed|jacket|knocks|itself|ladies|landed|lander|inside|larger|images|lasted|imaged|laughs|ignore|aboves|laying|accept|layers|across|yellow|leaded|leader|leaved|leaned|learns|leaves|yelled|lesser|letter|living|lifted|lifter|humans|hugest|lights|wrongs|houses|liking|likers|lining|housed|acting|listen|hotels|little|hotter|locals|locked|horses|longer|longed|looked|hoping|looker|losing|adding|louder|loving|lovers|lowing|lowest|writer|lowers|homing|holing|holder|making|hitter|makers|manned|manage|writes|admits|mapped|marked|hilled|higher|afraid|hiding|hidden|matter|ageing|helper|member|helped|memory|hellos|heater|metals|middle|heated|mights|minded|hearts|mining|minute|headed|mirror|misses|missed|moment|moneys|monies|months|mooned|mostly|having|mother|worlds|hating|mouths|moving|movers|movies|musics|worker|myself|naming|namers|narrow|hatted|hardly|nearer|neared|nearly|harder|necked|needed|happen|hanger|newest|nicest|nights|worked|nobody|nodded|handed|noises|noised|worded|normal|norths|nosing|agrees|noting|notice|halves|halved|number|guying|numbed|nurses|nursed|agreed|wooden|offing|gunned|offers|office|guards|wonder|okayed|okay'd|okay’d|ok'ing|ok’ing|oldest|womens|opened|opener|groups|womans|within|ground|orders|others|outing|wished|greens|greats|owning|wishes|owners|paging|pained|paints|greyed|greyer|paired|palest|grayed|palmed|papers|grayer|parent|parted|passed|golder|passes|pauses|paused|paying|person|people|wipers|goings|glance|phones|phoned|photos|picked|giving|givens|pieces|pieced|piling|gifted|pinked|pinker|places|placed|getter|gotten|plated|plates|gently|played|gather|player|please|gating|garden|pocket|gamers|points|pointy|gaming|future|wiping|fuller|police|pooled|poorer|fucked|popped|popper|fronts|friend|freers|poured|pourer|freest|powers|formed|forget|forgot|forest|forces|forced|footed|pretty|follow|fliers|flyers|proven|airing|proves|proved|prover|pulled|flying|puller|flower|pushes|pushed|floors|pusher|flight|fixers|fixing|quicks|winter|fitted|quiets|fitter|winged|radios|rained|raises|raised|fishes|rather|fished|firsts|firing|reader|finish|finger|fining|finest|realer|finder|really|finals|reason|filled|figure|fought|fights|fields|fewest|redder|refuse|remain|feeing|remind|feared|father|faster|remove|repeat|family|faller|fallen|failer|failed|rested|fading|return|reveal|riches|richer|riding|ridden|window|riders|rights|facing|allows|ringed|rising|rivers|extras|rocked|rolled|expect|roofed|excite|except|rooves|roomed|events|rounds|rowing|evened|rubbed|almost|entire|runner|enters|keying|rushed|rushes|sadder|safest|sanded|enjoys|saving|engine|savers|winded|saying|enders|scared|scares|scarer|scenes|ending|school|scream|either|eights|screen|egging|effort|search|edging|seated|second|eaters|seeing|seemed|eating|seller|sender|senses|sensed|easier|easily|earths|serves|served|willed|dusted|settle|during|driers|sevens|sexing|shadow|shakes|shaken|dryers|shaker|always|shaped|driest|shapes|shaper|drying|shares|shared|sharer|sharps|driver|drives|driven|sheets|droves|drinks|shirts|drunks|shoots|dreams|shorts|dozens|should|downed|shouts|shoved|shoves|showed|wilder|shower|dogged|doctor|shrugs|didn’t|sicker|sicked|didn't|siding|sighed|doings|sights|signed|dinner|silent|silver|dyings|widest|simple|simply|deeper|single|decide|deaths|sister|deader|sizing|darker|wholes|sleeps|dances|danced|slides|slider|cutter|slower|slowed|slowly|smalls|cupped|smells|smelly|crying|smiles|smiled|smiler|crowds|smokes|smoked|smoker|create|covers|snowed|whited|softer|course|softly|couple|counts|corner|whiter|copped|cooled|cooler|coming|whites|sorted|colors|colder|sounds|coffee|coated|spaces|clouds|spaced|spoken|speaks|clothe|closed|closes|closer|spends|climbs|clears|cleans|spirit|cities|circle|church|choose|spread|chosen|choice|chests|sprung|spring|sprang|stages|stairs|cheeks|stands|keeper|change|chance|stared|stares|starer|chairs|starts|center|causer|caused|states|stated|causes|caught|catted|stayed|steals|stolen|casing|sticks|caring|carded|stones|animal|cannot|stored|stores|storms|answer|camera|calmer|calmed|called|street|buyers|bought|strike|struck|buying|anyone|strong|busier|busied|busing|burner|stuffs|burned|stupid|builds|browns|suites|suited|brings|summer|bright|sunned|bridge|breath|breast|breaks|broken|surest|branch|brains|anyway|boxing|wheels|sweets|swings|bottom|bottle|system|bother|tables|taking|takers|talked|talker|boring|taller|booted|taught|booked|teamed|teared|boning|appear|bodies|thanks|boated|thicks|boards|bluest|things|thinks|blower|thirds|thirty|though|threes|throat|bloods|thrown|throws|blocks|timing|blacks|timers|tinier|biters|tiring|todays|biting|toning|tongue|arming|birded|bigger|wetter|toothy|beyond|better|topped|tossed|bested|tosses|beside|bender|toward|bended|tracks|belong|trains|belief|travel|behind|begins|before|bedded|became|become|beater|beaten|trucks|truest|aren’t|aren't|trusts|truths|trying|turned|twenty|around|uncles|weight|wasn’t|wasn't|arrive|unless|upping|wedded|viewed|barely|visits|banked|balled|voices|voiced|waited|bagger|waking|walked|bagged|walker|walled|asking|wanted|wanter|warred|waring|backed|warmed|warmer|babies|washed|washes|avoids|attack|waters|asleep|watery|waving|wavers|seems|party|minds|eaten|sells|sends|known|sense|hours|pasts|paths|easts|pause|mined|layer|payed|serve|earth|early|wills|aired|heard|hears|dusts|kills|goers|hotel|seven|dried|ideas|sexed|sexes|going|drier|dries|dryer|glass|heads|shake|leads|shook|aging|gives|phone|local|photo|shape|picks|above|locks|money|drops|share|given|wrong|girls|month|sharp|piece|wilds|sheet|drove|drive|moons|lands|piles|ships|drink|piled|drank|drunk|shirt|pinks|shits|dress|shoes|mores|shoot|longs|shots|dream|drawn|draws|drags|shops|haves|horse|short|gifts|dozen|place|downs|shout|hopes|shove|hoped|plans|wiper|doors|shown|shows|wiped|plate|world|mouth|doers|joins|shrug|shuts|leafs|moved|plays|moves|sicks|don’t|pleas|sided|sides|sighs|don't|gated|sight|looks|gates|wives|mover|signs|doing|dirts|knees|movie|learn|gamer|games|gamed|dying|music|since|desks|sings|singe|deeps|point|acted|musts|yells|funny|death|wider|loses|sixes|whose|names|sizes|sized|skins|keyed|skies|pools|slams|darks|named|slept|namer|sleep|leave|dance|slide|hated|young|whole|fucks|who’s|slips|who's|slows|front|porch|loved|hates|small|fresh|cries|cried|smell|white|nears|loves|smile|freer|pours|lover|freed|power|smoke|frees|yeses|crowd|cross|jokes|fours|snaps|crazy|forms|cover|homed|snows|among|necks|happy|least|press|force|homes|count|needs|wipes|years|cools|foots|joked|foods|never|songs|comes|sorry|flier|color|sorts|souls|lower|newer|flyer|colds|sound|flown|south|works|coats|space|nicer|prove|lucky|spoke|night|speak|cloud|hurts|yards|pulls|holed|flies|close|climb|spent|spend|words|holes|hangs|clear|lunch|spins|clean|class|liars|floor|holds|spots|alive|noise|flats|chose|flash|nones|child|fixer|fixed|fixes|chest|cheek|mains|stage|hands|makes|stair|quick|stood|check|fiver|stand|stars|fives|north|wrote|stare|lying|quiet|noses|quite|start|chair|nosed|radio|lived|rains|notes|state|large|cause|raise|catch|noted|maker|stays|halls|angry|stole|steal|reach|first|cased|cases|steps|lives|fires|stuck|carry|stick|cares|still|cared|fired|cards|added|stone|reads|halve|stops|write|can’t|ready|hairy|store|hairs|can't|storm|numbs|story|could|finer|knife|fines|calms|fined|calls|hurry|while|buyer|finds|nurse|found|which|lifts|admit|final|fills|lasts|keeps|where|buses|bused|study|offed|stuff|fight|woods|burnt|burns|field|human|build|built|wings|offer|brown|allow|guyed|suite|suits|bring|marks|fewer|feels|hills|wines|later|feeds|agree|guess|surer|fears|broke|break|guard|brain|highs|often|marry|ahead|knock|boxes|sweet|boxed|okays|swing|swung|falls|reply|hides|fails|huger|table|takes|taken|laugh|taker|rests|house|talks|bored|women|faded|fades|wheel|facts|wraps|boots|teach|faces|teams|older|books|tears|bones|maybe|woman|faced|areas|boned|opens|tells|rides|grows|thank|their|boats|thens|there|these|thick|rider|after|board|right|bluer|thins|blues|blued|grown|thing|again|rings|think|blows|blown|third|would|means|those|risen|three|rises|blood|eying|heres|throw|block|threw|roses|group|river|black|tying|times|timed|roads|rocks|order|timer|meant|green|tired|tires|extra|meets|today|rolls|biter|bitey|other|toned|tones|light|bites|worry|birds|roofs|armed|outer|rooms|outed|every|tooth|teeth|round|image|bests|event|liked|evens|rowed|likes|touch|bends|windy|bents|towns|winds|great|below|track|overs|owned|liker|train|enter|wound|begun|helps|began|begin|owner|beers|kinds|wests|paged|trees|treed|tripe|trips|pages|alone|hello|beats|enjoy|bears|truck|beach|safer|trues|truer|trued|safes|hells|sames|trust|truth|pains|wells|sands|tried|tries|greys|turns|isn’t|isn't|heavy|twice|saves|uncle|saved|under|kicks|saver|paint|lines|grays|until|weeks|upped|pairs|using|asked|usual|scare|being|ender|metal|views|paled|banks|visit|pales|paler|voice|scene|heats|waits|balls|ended|empty|woken|palms|wakes|waked|walks|lined|knows|pants|worse|paper|walls|worst|wants|eight|heart|along|backs|egged|jumps|warms|grass|might|edges|grabs|seats|avoid|parts|edged|aunts|watch|about|eater|won’t|water|won't|waved|waves|goods|waver|golds|wears|ears|grab|fits|each|sets|knee|lots|part|dust|noes|fish|stay|good|rain|cats|work|wild|laid|hang|gold|pass|step|loud|case|help|your|past|nods|home|care|path|hell|read|love|fire|gods|lift|card|stop|pays|keys|cars|paid|idea|fine|none|real|into|drop|heat|wish|cans|kids|find|goer|goes|went|calm|just|lead|gone|call|fill|nose|ship|huge|acts|lows|buys|some|note|kind|shit|shat|mind|ices|busy|pick|hand|shod|shoe|gave|reds|shot|hall|fews|ours|feel|burn|drew|such|draw|shop|give|felt|wing|suit|drag|hear|feed|mine|girl|feds|iced|down|when|fees|half|suns|able|word|fear|nows|door|fast|sure|leaf|pile|jobs|show|wine|boys|dogs|yell|hair|guys|kept|doer|fall|fell|head|shut|gift|hole|rest|numb|kick|lean|take|both|sick|fail|fade|took|miss|side|sigh|held|talk|last|plan|bore|hold|done|tall|teas|fact|boot|like|wife|rich|sign|book|wood|team|does|main|offs|tear|tore|torn|rode|dirt|gets|bone|joke|ride|make|told|play|died|tell|dies|tens|area|body|than|boat|line|guns|desk|that|what|kiss|them|they|gate|sang|then|plea|kill|face|sing|sung|eyes|thin|blue|deep|made|rung|ring|sirs|wide|he’s|rang|moon|blow|eyed|sits|more|whys|dead|blew|days|this|left|grew|he's|size|rise|rose|whom|have|skin|most|late|grow|slam|road|game|tied|ties|arms|time|dark|rock|okay|ages|mens|roll|mans|tiny|slid|dads|airs|ok'd|tire|wets|ok’d|i’ll|roof|slip|full|cuts|pool|slow|tone|bite|lips|cups|bits|room|olds|poor|bird|adds|ever|knew|hate|fuck|pops|even|tops|wipe|hits|once|west|hour|rows|rubs|toss|best|ones|only|from|runs|bend|bent|onto|open|move|town|free|pour|legs|rush|jump|snap|many|hill|less|maps|snow|keep|safe|much|soft|join|beer|i'll|beds|four|tree|same|sand|form|cops|must|year|cool|trip|lets|beat|mark|born|bear|with|come|save|know|true|sons|lock|song|soon|laws|came|outs|name|well|been|says|said|sort|feet|soul|high|yeah|were|hide|foot|turn|cold|wind|yard|twos|coat|food|over|hats|owns|ends|lady|aged|arts|else|long|flew|hurt|page|week|upon|lays|used|uses|hard|eggs|wins|very|mays|seas|pain|near|view|bars|weds|pull|edge|wrap|lies|bank|spin|ball|grey|seat|spun|lied|neck|push|wait|hope|bags|city|look|wake|spot|saws|woke|wear|pink|liar|eats|walk|need|sees|seen|puts|seem|wall|want|pair|gray|sell|will|flat|back|pale|sold|asks|wars|land|send|mean|warm|baby|sent|also|wash|away|here|easy|hung|sens|star|hers|aunt|palm|worn|life|meet|wore|east|live|news|five|wave|next|lost|lose|nice|ways|far|few|war|bad|bag|bar|wed|use|ups|art|was|two|try|are|bed|top|arm|wet|big|too|bit|tie|the|ten|tvs|tea|box|boy|sun|bus|but|buy|any|can|car|cat|and|son|cop|sos|cry|cup|cut|who|dad|sky|day|six|why|sit|sat|sir|die|did|dog|she|dry|sex|set|ear|ate|eat|see|saw|win|won|sea|egg|end|say|sad|ran|run|rub|row|eye|rid|ask|fed|fee|red|way|fit|fix|all|put|fly|for|pop|fun|get|got|god|pay|own|out|our|air|ors|one|old|ohs|gun|key|off|guy|now|not|nor|nod|nos|ago|new|hat|age|had|has|her|met|hey|may|hid|map|him|add|his|man|men|hit|mad|low|lot|hot|lip|how|lit|lie|kid|i'm|let|i’m|leg|i'd|i’d|ice|led|act|lay|law|ins|yes|yet|you|its|job|no|at|by|my|on|ha|do|ok|he|oh|is|tv|me|us|as|hi|go|if|of|am|up|to|we|so|in|or|it|be|an|i|a".split(
    "|"
)

STOPWORDS = "a|all|am|an|and|any|are|as|at|be|because|been|but|by|can|did|do|does|each|every|few|for|from|get|give|go|got|had|has|have|he|her|him|his|how|i|if|in|into|is|it|its|let|many|may|me|more|most|must|my|next|no|not|of|on|or|other|our|out|over|same|she|should|so|some|something|such|than|that|the|their|them|then|there|these|they|this|those|to|too|under|until|up|us|use|want|was|we|were|what|when|which|while|who|with|without|would|you|your".split(
    "|"
)

unicode_categories = {
    "Pi": r"\u00ab\u2018\u201b\u201c\u201f\u2039\u2e02\u2e04\u2e09\u2e0c\u2e1c",
    "Sk": r"\u005e\u0060\u00a8\u00af\u00b4\u00b8\u02c2-\u02c5\u02d2-\u02df\u02e5-\u02ed\u02ef-\u02ff\u0374\u0375\u0384\u0385\u1fbd\u1fbf-\u1fc1\u1fcd-\u1fcf\u1fdd-\u1fdf\u1fed-\u1fef\u1ffd\u1ffe\u309b\u309c\ua700-\ua716\ua720\ua721\uff3e\uff40\uffe3",
    "Sm": r"\u002b\u003c-\u003e\u007c\u007e\u00ac\u00b1\u00d7\u00f7\u03f6\u2044\u2052\u207a-\u207c\u208a-\u208c\u2140-\u2144\u214b\u2190-\u2194\u219a\u219b\u21a0\u21a3\u21a6\u21ae\u21ce\u21cf\u21d2\u21d4\u21f4-\u22ff\u2308-\u230b\u2320\u2321\u237c\u239b-\u23b3\u23dc-\u23e1\u25b7\u25c1\u25f8-\u25ff\u266f\u27c0-\u27c4\u27c7-\u27ca\u27d0-\u27e5\u27f0-\u27ff\u2900-\u2982\u2999-\u29d7\u29dc-\u29fb\u29fe-\u2aff\ufb29\ufe62\ufe64-\ufe66\uff0b\uff1c-\uff1e\uff5c\uff5e\uffe2\uffe9-\uffec",
    "So": r"\u00a6\u00a7\u00a9\u00ae\u00b0\u00b6\u0482\u060e\u060f\u06e9\u06fd\u06fe\u07f6\u09fa\u0b70\u0bf3-\u0bf8\u0bfa\u0cf1\u0cf2\u0f01-\u0f03\u0f13-\u0f17\u0f1a-\u0f1f\u0f34\u0f36\u0f38\u0fbe-\u0fc5\u0fc7-\u0fcc\u0fcf\u1360\u1390-\u1399\u1940\u19e0-\u19ff\u1b61-\u1b6a\u1b74-\u1b7c\u2100\u2101\u2103-\u2106\u2108\u2109\u2114\u2116-\u2118\u211e-\u2123\u2125\u2127\u2129\u212e\u213a\u213b\u214a\u214c\u214d\u2195-\u2199\u219c-\u219f\u21a1\u21a2\u21a4\u21a5\u21a7-\u21ad\u21af-\u21cd\u21d0\u21d1\u21d3\u21d5-\u21f3\u2300-\u2307\u230c-\u231f\u2322-\u2328\u232b-\u237b\u237d-\u239a\u23b4-\u23db\u23e2-\u23e7\u2400-\u2426\u2440-\u244a\u249c-\u24e9\u2500-\u25b6\u25b8-\u25c0\u25c2-\u25f7\u2600-\u266e\u2670-\u269c\u26a0-\u26b2\u2701-\u2704\u2706-\u2709\u270c-\u2727\u2729-\u274b\u274d\u274f-\u2752\u2756\u2758-\u275e\u2761-\u2767\u2794\u2798-\u27af\u27b1-\u27be\u2800-\u28ff\u2b00-\u2b1a\u2b20-\u2b23\u2ce5-\u2cea\u2e80-\u2e99\u2e9b-\u2ef3\u2f00-\u2fd5\u2ff0-\u2ffb\u3004\u3012\u3013\u3020\u3036\u3037\u303e\u303f\u3190\u3191\u3196-\u319f\u31c0-\u31cf\u3200-\u321e\u322a-\u3243\u3250\u3260-\u327f\u328a-\u32b0\u32c0-\u32fe\u3300-\u33ff\u4dc0-\u4dff\ua490-\ua4c6\ua828-\ua82b\ufdfd\uffe4\uffe8\uffed\uffee\ufffc\ufffd",
    "Po": r"\u0021-\u0023\u0025-\u0027\u002a\u002c\u002e\u002f\u003a\u003b\u003f\u0040\u005c\u00a1\u00b7\u00bf\u037e\u0387\u055a-\u055f\u0589\u05be\u05c0\u05c3\u05c6\u05f3\u05f4\u060c\u060d\u061b\u061e\u061f\u066a-\u066d\u06d4\u0700-\u070d\u07f7-\u07f9\u0964\u0965\u0970\u0df4\u0e4f\u0e5a\u0e5b\u0f04-\u0f12\u0f85\u0fd0\u0fd1\u104a-\u104f\u10fb\u1361-\u1368\u166d\u166e\u16eb-\u16ed\u1735\u1736\u17d4-\u17d6\u17d8-\u17da\u1800-\u1805\u1807-\u180a\u1944\u1945\u19de\u19df\u1a1e\u1a1f\u1b5a-\u1b60\u2016\u2017\u2020-\u2027\u2030-\u2038\u203b-\u203e\u2041-\u2043\u2047-\u2051\u2053\u2055-\u205e\u2cf9-\u2cfc\u2cfe\u2cff\u2e00\u2e01\u2e06-\u2e08\u2e0b\u2e0e-\u2e16\u3001-\u3003\u303d\u30fb\ua874-\ua877\ufe10-\ufe16\ufe19\ufe30\ufe45\ufe46\ufe49-\ufe4c\ufe50-\ufe52\ufe54-\ufe57\ufe5f-\ufe61\ufe68\ufe6a\ufe6b\uff01-\uff03\uff05-\uff07\uff0a\uff0c\uff0e\uff0f\uff1a\uff1b\uff1f\uff20\uff3c\uff61\uff64\uff65",
    "Mn": r"\u0300-\u036f\u0483-\u0486\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7\u0610-\u0615\u064b-\u065e\u0670\u06d6-\u06dc\u06df-\u06e4\u06e7\u06e8\u06ea-\u06ed\u0711\u0730-\u074a\u07a6-\u07b0\u07eb-\u07f3\u0901\u0902\u093c\u0941-\u0948\u094d\u0951-\u0954\u0962\u0963\u0981\u09bc\u09c1-\u09c4\u09cd\u09e2\u09e3\u0a01\u0a02\u0a3c\u0a41\u0a42\u0a47\u0a48\u0a4b-\u0a4d\u0a70\u0a71\u0a81\u0a82\u0abc\u0ac1-\u0ac5\u0ac7\u0ac8\u0acd\u0ae2\u0ae3\u0b01\u0b3c\u0b3f\u0b41-\u0b43\u0b4d\u0b56\u0b82\u0bc0\u0bcd\u0c3e-\u0c40\u0c46-\u0c48\u0c4a-\u0c4d\u0c55\u0c56\u0cbc\u0cbf\u0cc6\u0ccc\u0ccd\u0ce2\u0ce3\u0d41-\u0d43\u0d4d\u0dca\u0dd2-\u0dd4\u0dd6\u0e31\u0e34-\u0e3a\u0e47-\u0e4e\u0eb1\u0eb4-\u0eb9\u0ebb\u0ebc\u0ec8-\u0ecd\u0f18\u0f19\u0f35\u0f37\u0f39\u0f71-\u0f7e\u0f80-\u0f84\u0f86\u0f87\u0f90-\u0f97\u0f99-\u0fbc\u0fc6\u102d-\u1030\u1032\u1036\u1037\u1039\u1058\u1059\u135f\u1712-\u1714\u1732-\u1734\u1752\u1753\u1772\u1773\u17b7-\u17bd\u17c6\u17c9-\u17d3\u17dd\u180b-\u180d\u18a9\u1920-\u1922\u1927\u1928\u1932\u1939-\u193b\u1a17\u1a18\u1b00-\u1b03\u1b34\u1b36-\u1b3a\u1b3c\u1b42\u1b6b-\u1b73\u1dc0-\u1dca\u1dfe\u1dff\u20d0-\u20dc\u20e1\u20e5-\u20ef\u302a-\u302f\u3099\u309a\ua806\ua80b\ua825\ua826\ufb1e\ufe00-\ufe0f\ufe20-\ufe23",
    "Ps": r"\u0028\u005b\u007b\u0f3a\u0f3c\u169b\u201a\u201e\u2045\u207d\u208d\u2329\u2768\u276a\u276c\u276e\u2770\u2772\u2774\u27c5\u27e6\u27e8\u27ea\u2983\u2985\u2987\u2989\u298b\u298d\u298f\u2991\u2993\u2995\u2997\u29d8\u29da\u29fc\u3008\u300a\u300c\u300e\u3010\u3014\u3016\u3018\u301a\u301d\ufd3e\ufe17\ufe35\ufe37\ufe39\ufe3b\ufe3d\ufe3f\ufe41\ufe43\ufe47\ufe59\ufe5b\ufe5d\uff08\uff3b\uff5b\uff5f\uff62",
    "Cc": r"\u0000-\u001f\u007f-\u009f",
    "Cf": r"\u00ad\u0600-\u0603\u06dd\u070f\u17b4\u17b5\u200b-\u200f\u202a-\u202e\u2060-\u2063\u206a-\u206f\ufeff\ufff9-\ufffb",
    "Ll": r"\u0061-\u007a\u00aa\u00b5\u00ba\u00df-\u00f6\u00f8-\u00ff\u0101\u0103\u0105\u0107\u0109\u010b\u010d\u010f\u0111\u0113\u0115\u0117\u0119\u011b\u011d\u011f\u0121\u0123\u0125\u0127\u0129\u012b\u012d\u012f\u0131\u0133\u0135\u0137\u0138\u013a\u013c\u013e\u0140\u0142\u0144\u0146\u0148\u0149\u014b\u014d\u014f\u0151\u0153\u0155\u0157\u0159\u015b\u015d\u015f\u0161\u0163\u0165\u0167\u0169\u016b\u016d\u016f\u0171\u0173\u0175\u0177\u017a\u017c\u017e-\u0180\u0183\u0185\u0188\u018c\u018d\u0192\u0195\u0199-\u019b\u019e\u01a1\u01a3\u01a5\u01a8\u01aa\u01ab\u01ad\u01b0\u01b4\u01b6\u01b9\u01ba\u01bd-\u01bf\u01c6\u01c9\u01cc\u01ce\u01d0\u01d2\u01d4\u01d6\u01d8\u01da\u01dc\u01dd\u01df\u01e1\u01e3\u01e5\u01e7\u01e9\u01eb\u01ed\u01ef\u01f0\u01f3\u01f5\u01f9\u01fb\u01fd\u01ff\u0201\u0203\u0205\u0207\u0209\u020b\u020d\u020f\u0211\u0213\u0215\u0217\u0219\u021b\u021d\u021f\u0221\u0223\u0225\u0227\u0229\u022b\u022d\u022f\u0231\u0233-\u0239\u023c\u023f\u0240\u0242\u0247\u0249\u024b\u024d\u024f-\u0293\u0295-\u02af\u037b-\u037d\u0390\u03ac-\u03ce\u03d0\u03d1\u03d5-\u03d7\u03d9\u03db\u03dd\u03df\u03e1\u03e3\u03e5\u03e7\u03e9\u03eb\u03ed\u03ef-\u03f3\u03f5\u03f8\u03fb\u03fc\u0430-\u045f\u0461\u0463\u0465\u0467\u0469\u046b\u046d\u046f\u0471\u0473\u0475\u0477\u0479\u047b\u047d\u047f\u0481\u048b\u048d\u048f\u0491\u0493\u0495\u0497\u0499\u049b\u049d\u049f\u04a1\u04a3\u04a5\u04a7\u04a9\u04ab\u04ad\u04af\u04b1\u04b3\u04b5\u04b7\u04b9\u04bb\u04bd\u04bf\u04c2\u04c4\u04c6\u04c8\u04ca\u04cc\u04ce\u04cf\u04d1\u04d3\u04d5\u04d7\u04d9\u04db\u04dd\u04df\u04e1\u04e3\u04e5\u04e7\u04e9\u04eb\u04ed\u04ef\u04f1\u04f3\u04f5\u04f7\u04f9\u04fb\u04fd\u04ff\u0501\u0503\u0505\u0507\u0509\u050b\u050d\u050f\u0511\u0513\u0561-\u0587\u1d00-\u1d2b\u1d62-\u1d77\u1d79-\u1d9a\u1e01\u1e03\u1e05\u1e07\u1e09\u1e0b\u1e0d\u1e0f\u1e11\u1e13\u1e15\u1e17\u1e19\u1e1b\u1e1d\u1e1f\u1e21\u1e23\u1e25\u1e27\u1e29\u1e2b\u1e2d\u1e2f\u1e31\u1e33\u1e35\u1e37\u1e39\u1e3b\u1e3d\u1e3f\u1e41\u1e43\u1e45\u1e47\u1e49\u1e4b\u1e4d\u1e4f\u1e51\u1e53\u1e55\u1e57\u1e59\u1e5b\u1e5d\u1e5f\u1e61\u1e63\u1e65\u1e67\u1e69\u1e6b\u1e6d\u1e6f\u1e71\u1e73\u1e75\u1e77\u1e79\u1e7b\u1e7d\u1e7f\u1e81\u1e83\u1e85\u1e87\u1e89\u1e8b\u1e8d\u1e8f\u1e91\u1e93\u1e95-\u1e9b\u1ea1\u1ea3\u1ea5\u1ea7\u1ea9\u1eab\u1ead\u1eaf\u1eb1\u1eb3\u1eb5\u1eb7\u1eb9\u1ebb\u1ebd\u1ebf\u1ec1\u1ec3\u1ec5\u1ec7\u1ec9\u1ecb\u1ecd\u1ecf\u1ed1\u1ed3\u1ed5\u1ed7\u1ed9\u1edb\u1edd\u1edf\u1ee1\u1ee3\u1ee5\u1ee7\u1ee9\u1eeb\u1eed\u1eef\u1ef1\u1ef3\u1ef5\u1ef7\u1ef9\u1f00-\u1f07\u1f10-\u1f15\u1f20-\u1f27\u1f30-\u1f37\u1f40-\u1f45\u1f50-\u1f57\u1f60-\u1f67\u1f70-\u1f7d\u1f80-\u1f87\u1f90-\u1f97\u1fa0-\u1fa7\u1fb0-\u1fb4\u1fb6\u1fb7\u1fbe\u1fc2-\u1fc4\u1fc6\u1fc7\u1fd0-\u1fd3\u1fd6\u1fd7\u1fe0-\u1fe7\u1ff2-\u1ff4\u1ff6\u1ff7\u2071\u207f\u210a\u210e\u210f\u2113\u212f\u2134\u2139\u213c\u213d\u2146-\u2149\u214e\u2184\u2c30-\u2c5e\u2c61\u2c65\u2c66\u2c68\u2c6a\u2c6c\u2c74\u2c76\u2c77\u2c81\u2c83\u2c85\u2c87\u2c89\u2c8b\u2c8d\u2c8f\u2c91\u2c93\u2c95\u2c97\u2c99\u2c9b\u2c9d\u2c9f\u2ca1\u2ca3\u2ca5\u2ca7\u2ca9\u2cab\u2cad\u2caf\u2cb1\u2cb3\u2cb5\u2cb7\u2cb9\u2cbb\u2cbd\u2cbf\u2cc1\u2cc3\u2cc5\u2cc7\u2cc9\u2ccb\u2ccd\u2ccf\u2cd1\u2cd3\u2cd5\u2cd7\u2cd9\u2cdb\u2cdd\u2cdf\u2ce1\u2ce3\u2ce4\u2d00-\u2d25\ufb00-\ufb06\ufb13-\ufb17\uff41-\uff5a",
    "Lm": r"\u02b0-\u02c1\u02c6-\u02d1\u02e0-\u02e4\u02ee\u037a\u0559\u0640\u06e5\u06e6\u07f4\u07f5\u07fa\u0e46\u0ec6\u10fc\u17d7\u1843\u1d2c-\u1d61\u1d78\u1d9b-\u1dbf\u2090-\u2094\u2d6f\u3005\u3031-\u3035\u303b\u309d\u309e\u30fc-\u30fe\ua015\ua717-\ua71a\uff70\uff9e\uff9f",
    "Lo": r"\u01bb\u01c0-\u01c3\u0294\u05d0-\u05ea\u05f0-\u05f2\u0621-\u063a\u0641-\u064a\u066e\u066f\u0671-\u06d3\u06d5\u06ee\u06ef\u06fa-\u06fc\u06ff\u0710\u0712-\u072f\u074d-\u076d\u0780-\u07a5\u07b1\u07ca-\u07ea\u0904-\u0939\u093d\u0950\u0958-\u0961\u097b-\u097f\u0985-\u098c\u098f\u0990\u0993-\u09a8\u09aa-\u09b0\u09b2\u09b6-\u09b9\u09bd\u09ce\u09dc\u09dd\u09df-\u09e1\u09f0\u09f1\u0a05-\u0a0a\u0a0f\u0a10\u0a13-\u0a28\u0a2a-\u0a30\u0a32\u0a33\u0a35\u0a36\u0a38\u0a39\u0a59-\u0a5c\u0a5e\u0a72-\u0a74\u0a85-\u0a8d\u0a8f-\u0a91\u0a93-\u0aa8\u0aaa-\u0ab0\u0ab2\u0ab3\u0ab5-\u0ab9\u0abd\u0ad0\u0ae0\u0ae1\u0b05-\u0b0c\u0b0f\u0b10\u0b13-\u0b28\u0b2a-\u0b30\u0b32\u0b33\u0b35-\u0b39\u0b3d\u0b5c\u0b5d\u0b5f-\u0b61\u0b71\u0b83\u0b85-\u0b8a\u0b8e-\u0b90\u0b92-\u0b95\u0b99\u0b9a\u0b9c\u0b9e\u0b9f\u0ba3\u0ba4\u0ba8-\u0baa\u0bae-\u0bb9\u0c05-\u0c0c\u0c0e-\u0c10\u0c12-\u0c28\u0c2a-\u0c33\u0c35-\u0c39\u0c60\u0c61\u0c85-\u0c8c\u0c8e-\u0c90\u0c92-\u0ca8\u0caa-\u0cb3\u0cb5-\u0cb9\u0cbd\u0cde\u0ce0\u0ce1\u0d05-\u0d0c\u0d0e-\u0d10\u0d12-\u0d28\u0d2a-\u0d39\u0d60\u0d61\u0d85-\u0d96\u0d9a-\u0db1\u0db3-\u0dbb\u0dbd\u0dc0-\u0dc6\u0e01-\u0e30\u0e32\u0e33\u0e40-\u0e45\u0e81\u0e82\u0e84\u0e87\u0e88\u0e8a\u0e8d\u0e94-\u0e97\u0e99-\u0e9f\u0ea1-\u0ea3\u0ea5\u0ea7\u0eaa\u0eab\u0ead-\u0eb0\u0eb2\u0eb3\u0ebd\u0ec0-\u0ec4\u0edc\u0edd\u0f00\u0f40-\u0f47\u0f49-\u0f6a\u0f88-\u0f8b\u1000-\u1021\u1023-\u1027\u1029\u102a\u1050-\u1055\u10d0-\u10fa\u1100-\u1159\u115f-\u11a2\u11a8-\u11f9\u1200-\u1248\u124a-\u124d\u1250-\u1256\u1258\u125a-\u125d\u1260-\u1288\u128a-\u128d\u1290-\u12b0\u12b2-\u12b5\u12b8-\u12be\u12c0\u12c2-\u12c5\u12c8-\u12d6\u12d8-\u1310\u1312-\u1315\u1318-\u135a\u1380-\u138f\u13a0-\u13f4\u1401-\u166c\u166f-\u1676\u1681-\u169a\u16a0-\u16ea\u1700-\u170c\u170e-\u1711\u1720-\u1731\u1740-\u1751\u1760-\u176c\u176e-\u1770\u1780-\u17b3\u17dc\u1820-\u1842\u1844-\u1877\u1880-\u18a8\u1900-\u191c\u1950-\u196d\u1970-\u1974\u1980-\u19a9\u19c1-\u19c7\u1a00-\u1a16\u1b05-\u1b33\u1b45-\u1b4b\u2135-\u2138\u2d30-\u2d65\u2d80-\u2d96\u2da0-\u2da6\u2da8-\u2dae\u2db0-\u2db6\u2db8-\u2dbe\u2dc0-\u2dc6\u2dc8-\u2dce\u2dd0-\u2dd6\u2dd8-\u2dde\u3006\u303c\u3041-\u3096\u309f\u30a1-\u30fa\u30ff\u3105-\u312c\u3131-\u318e\u31a0-\u31b7\u31f0-\u31ff\u3400\u4db5\u4e00\u9fbb\ua000-\ua014\ua016-\ua48c\ua800\ua801\ua803-\ua805\ua807-\ua80a\ua80c-\ua822\ua840-\ua873\uac00\ud7a3\uf900-\ufa2d\ufa30-\ufa6a\ufa70-\ufad9\ufb1d\ufb1f-\ufb28\ufb2a-\ufb36\ufb38-\ufb3c\ufb3e\ufb40\ufb41\ufb43\ufb44\ufb46-\ufbb1\ufbd3-\ufd3d\ufd50-\ufd8f\ufd92-\ufdc7\ufdf0-\ufdfb\ufe70-\ufe74\ufe76-\ufefc\uff66-\uff6f\uff71-\uff9d\uffa0-\uffbe\uffc2-\uffc7\uffca-\uffcf\uffd2-\uffd7\uffda-\uffdc",
    "Co": r"\ue000\uf8ff",
    "Nd": r"\u0030-\u0039\u0660-\u0669\u06f0-\u06f9\u07c0-\u07c9\u0966-\u096f\u09e6-\u09ef\u0a66-\u0a6f\u0ae6-\u0aef\u0b66-\u0b6f\u0be6-\u0bef\u0c66-\u0c6f\u0ce6-\u0cef\u0d66-\u0d6f\u0e50-\u0e59\u0ed0-\u0ed9\u0f20-\u0f29\u1040-\u1049\u17e0-\u17e9\u1810-\u1819\u1946-\u194f\u19d0-\u19d9\u1b50-\u1b59\uff10-\uff19",
    "Lt": r"\u01c5\u01c8\u01cb\u01f2\u1f88-\u1f8f\u1f98-\u1f9f\u1fa8-\u1faf\u1fbc\u1fcc\u1ffc",
    "Lu": r"\u0041-\u005a\u00c0-\u00d6\u00d8-\u00de\u0100\u0102\u0104\u0106\u0108\u010a\u010c\u010e\u0110\u0112\u0114\u0116\u0118\u011a\u011c\u011e\u0120\u0122\u0124\u0126\u0128\u012a\u012c\u012e\u0130\u0132\u0134\u0136\u0139\u013b\u013d\u013f\u0141\u0143\u0145\u0147\u014a\u014c\u014e\u0150\u0152\u0154\u0156\u0158\u015a\u015c\u015e\u0160\u0162\u0164\u0166\u0168\u016a\u016c\u016e\u0170\u0172\u0174\u0176\u0178\u0179\u017b\u017d\u0181\u0182\u0184\u0186\u0187\u0189-\u018b\u018e-\u0191\u0193\u0194\u0196-\u0198\u019c\u019d\u019f\u01a0\u01a2\u01a4\u01a6\u01a7\u01a9\u01ac\u01ae\u01af\u01b1-\u01b3\u01b5\u01b7\u01b8\u01bc\u01c4\u01c7\u01ca\u01cd\u01cf\u01d1\u01d3\u01d5\u01d7\u01d9\u01db\u01de\u01e0\u01e2\u01e4\u01e6\u01e8\u01ea\u01ec\u01ee\u01f1\u01f4\u01f6-\u01f8\u01fa\u01fc\u01fe\u0200\u0202\u0204\u0206\u0208\u020a\u020c\u020e\u0210\u0212\u0214\u0216\u0218\u021a\u021c\u021e\u0220\u0222\u0224\u0226\u0228\u022a\u022c\u022e\u0230\u0232\u023a\u023b\u023d\u023e\u0241\u0243-\u0246\u0248\u024a\u024c\u024e\u0386\u0388-\u038a\u038c\u038e\u038f\u0391-\u03a1\u03a3-\u03ab\u03d2-\u03d4\u03d8\u03da\u03dc\u03de\u03e0\u03e2\u03e4\u03e6\u03e8\u03ea\u03ec\u03ee\u03f4\u03f7\u03f9\u03fa\u03fd-\u042f\u0460\u0462\u0464\u0466\u0468\u046a\u046c\u046e\u0470\u0472\u0474\u0476\u0478\u047a\u047c\u047e\u0480\u048a\u048c\u048e\u0490\u0492\u0494\u0496\u0498\u049a\u049c\u049e\u04a0\u04a2\u04a4\u04a6\u04a8\u04aa\u04ac\u04ae\u04b0\u04b2\u04b4\u04b6\u04b8\u04ba\u04bc\u04be\u04c0\u04c1\u04c3\u04c5\u04c7\u04c9\u04cb\u04cd\u04d0\u04d2\u04d4\u04d6\u04d8\u04da\u04dc\u04de\u04e0\u04e2\u04e4\u04e6\u04e8\u04ea\u04ec\u04ee\u04f0\u04f2\u04f4\u04f6\u04f8\u04fa\u04fc\u04fe\u0500\u0502\u0504\u0506\u0508\u050a\u050c\u050e\u0510\u0512\u0531-\u0556\u10a0-\u10c5\u1e00\u1e02\u1e04\u1e06\u1e08\u1e0a\u1e0c\u1e0e\u1e10\u1e12\u1e14\u1e16\u1e18\u1e1a\u1e1c\u1e1e\u1e20\u1e22\u1e24\u1e26\u1e28\u1e2a\u1e2c\u1e2e\u1e30\u1e32\u1e34\u1e36\u1e38\u1e3a\u1e3c\u1e3e\u1e40\u1e42\u1e44\u1e46\u1e48\u1e4a\u1e4c\u1e4e\u1e50\u1e52\u1e54\u1e56\u1e58\u1e5a\u1e5c\u1e5e\u1e60\u1e62\u1e64\u1e66\u1e68\u1e6a\u1e6c\u1e6e\u1e70\u1e72\u1e74\u1e76\u1e78\u1e7a\u1e7c\u1e7e\u1e80\u1e82\u1e84\u1e86\u1e88\u1e8a\u1e8c\u1e8e\u1e90\u1e92\u1e94\u1ea0\u1ea2\u1ea4\u1ea6\u1ea8\u1eaa\u1eac\u1eae\u1eb0\u1eb2\u1eb4\u1eb6\u1eb8\u1eba\u1ebc\u1ebe\u1ec0\u1ec2\u1ec4\u1ec6\u1ec8\u1eca\u1ecc\u1ece\u1ed0\u1ed2\u1ed4\u1ed6\u1ed8\u1eda\u1edc\u1ede\u1ee0\u1ee2\u1ee4\u1ee6\u1ee8\u1eea\u1eec\u1eee\u1ef0\u1ef2\u1ef4\u1ef6\u1ef8\u1f08-\u1f0f\u1f18-\u1f1d\u1f28-\u1f2f\u1f38-\u1f3f\u1f48-\u1f4d\u1f59\u1f5b\u1f5d\u1f5f\u1f68-\u1f6f\u1fb8-\u1fbb\u1fc8-\u1fcb\u1fd8-\u1fdb\u1fe8-\u1fec\u1ff8-\u1ffb\u2102\u2107\u210b-\u210d\u2110-\u2112\u2115\u2119-\u211d\u2124\u2126\u2128\u212a-\u212d\u2130-\u2133\u213e\u213f\u2145\u2183\u2c00-\u2c2e\u2c60\u2c62-\u2c64\u2c67\u2c69\u2c6b\u2c75\u2c80\u2c82\u2c84\u2c86\u2c88\u2c8a\u2c8c\u2c8e\u2c90\u2c92\u2c94\u2c96\u2c98\u2c9a\u2c9c\u2c9e\u2ca0\u2ca2\u2ca4\u2ca6\u2ca8\u2caa\u2cac\u2cae\u2cb0\u2cb2\u2cb4\u2cb6\u2cb8\u2cba\u2cbc\u2cbe\u2cc0\u2cc2\u2cc4\u2cc6\u2cc8\u2cca\u2ccc\u2cce\u2cd0\u2cd2\u2cd4\u2cd6\u2cd8\u2cda\u2cdc\u2cde\u2ce0\u2ce2\uff21-\uff3a",
    "Cs": r"\ud800\udb7f\udb80\udbff\udc00\udfff",
    "Zl": r"\u2028",
    "Nl": r"\u16ee-\u16f0\u2160-\u2182\u3007\u3021-\u3029\u3038-\u303a",
    "Zp": r"\u2029",
    "No": r"\u00b2\u00b3\u00b9\u00bc-\u00be\u09f4-\u09f9\u0bf0-\u0bf2\u0f2a-\u0f33\u1369-\u137c\u17f0-\u17f9\u2070\u2074-\u2079\u2080-\u2089\u2153-\u215f\u2460-\u249b\u24ea-\u24ff\u2776-\u2793\u2cfd\u3192-\u3195\u3220-\u3229\u3251-\u325f\u3280-\u3289\u32b1-\u32bf",
    "Zs": r"\u0020\u00a0\u1680\u180e\u2000-\u200a\u202f\u205f\u3000",
    "Sc": r"\u0024\u00a2-\u00a5\u060b\u09f2\u09f3\u0af1\u0bf9\u0e3f\u17db\u20a0-\u20b5\ufdfc\ufe69\uff04\uffe0\uffe1\uffe5\uffe6",
    "Pc": r"\u005f\u203f\u2040\u2054\ufe33\ufe34\ufe4d-\ufe4f\uff3f",
    "Pd": r"\u002d\u058a\u1806\u2010-\u2015\u2e17\u301c\u3030\u30a0\ufe31\ufe32\ufe58\ufe63\uff0d",
    "Pe": r"\u0029\u005d\u007d\u0f3b\u0f3d\u169c\u2046\u207e\u208e\u232a\u2769\u276b\u276d\u276f\u2771\u2773\u2775\u27c6\u27e7\u27e9\u27eb\u2984\u2986\u2988\u298a\u298c\u298e\u2990\u2992\u2994\u2996\u2998\u29d9\u29db\u29fd\u3009\u300b\u300d\u300f\u3011\u3015\u3017\u3019\u301b\u301e\u301f\ufd3f\ufe18\ufe36\ufe38\ufe3a\ufe3c\ufe3e\ufe40\ufe42\ufe44\ufe48\ufe5a\ufe5c\ufe5e\uff09\uff3d\uff5d\uff60\uff63",
    "Pf": r"\u00bb\u2019\u201d\u203a\u2e03\u2e05\u2e0a\u2e0d\u2e1d",
    "Me": r"\u0488\u0489\u06de\u20dd-\u20e0\u20e2-\u20e4",
    "Mc": r"\u0903\u093e-\u0940\u0949-\u094c\u0982\u0983\u09be-\u09c0\u09c7\u09c8\u09cb\u09cc\u09d7\u0a03\u0a3e-\u0a40\u0a83\u0abe-\u0ac0\u0ac9\u0acb\u0acc\u0b02\u0b03\u0b3e\u0b40\u0b47\u0b48\u0b4b\u0b4c\u0b57\u0bbe\u0bbf\u0bc1\u0bc2\u0bc6-\u0bc8\u0bca-\u0bcc\u0bd7\u0c01-\u0c03\u0c41-\u0c44\u0c82\u0c83\u0cbe\u0cc0-\u0cc4\u0cc7\u0cc8\u0cca\u0ccb\u0cd5\u0cd6\u0d02\u0d03\u0d3e-\u0d40\u0d46-\u0d48\u0d4a-\u0d4c\u0d57\u0d82\u0d83\u0dcf-\u0dd1\u0dd8-\u0ddf\u0df2\u0df3\u0f3e\u0f3f\u0f7f\u102c\u1031\u1038\u1056\u1057\u17b6\u17be-\u17c5\u17c7\u17c8\u1923-\u1926\u1929-\u192b\u1930\u1931\u1933-\u1938\u19b0-\u19c0\u19c8\u19c9\u1a19-\u1a1b\u1b04\u1b35\u1b3b\u1b3d-\u1b41\u1b43\u1b44\ua802\ua823\ua824\ua827",
}

# VERY important function DO NOT TOUCH i have no idea why but nothing works without it
# fmt: off
def aa(s: str, l: list, d: dict) -> None:
    if (s == None or s == "@" or s.startswith("except this string, this string can be changed apparently")):
        d["a"] = l
# fmt: on


# Some class declarations:


@unique
class ProposalStatus(IntEnum):
    PENDING = 0
    PASSED = 1
    FAILED = 2


@unique
class DealStatus(IntEnum):
    OPEN = 0
    PROCESSING = 1
    CANCELLED = 2
    COMPLETE = 3


@unique
class ProposalType(IntEnum):
    LAW = 0
    ORDER = 1


@unique
class RoleOwnershipLevel(IntEnum):
    NONE = 0
    OWNED = 1
    SIMPLE_MAJORITY = 2
    ABSOLUTE_MAJORITY = 3
    TOTALITY = 4


class MeWhiningException(Exception):
    def __init__(self, message, bot_message):
        self.bot_message = bot_message
        super().__init__(message)


class DatabaseConnection:

    setup_statements = [
        """CREATE TABLE IF NOT EXISTS proposals (
        proposal_id    INTEGER PRIMARY KEY,
        message_id     INTEGER UNIQUE NOT NULL,
        status         INTEGER NOT NULL DEFAULT 0 CHECK(status IN (0, 1, 2)),
        type           INTEGER NOT NULL DEFAULT 0 CHECK(type IN (0, 1)),
        author_user_id INTEGER NOT NULL DEFAULT -1,
        description    TEXT,
        file_data      BLOB,
        file_path      TEXT
    );""",
        """CREATE TABLE IF NOT EXISTS agents (
        user_id            INTEGER UNIQUE NOT NULL,
        profile_message_id INTEGER NOT NULL DEFAULT -1,
        credit             REAL NOT NULL DEFAULT 0,
        loyalty            INTEGER NOT NULL DEFAULT 0,
        selfdescription    TEXT,
        to_refresh         BOOLEAN NOT NULL DEFAULT 1 CHECK(to_refresh IN (0, 1)),
        ascensions         INTEGER NOT NULL DEFAULT 0
    );""",
        """CREATE TABLE IF NOT EXISTS roles (
        role_id     INTEGER UNIQUE NOT NULL,
        name        TEXT    UNIQUE NOT NULL,
        color       INTEGER NOT NULL DEFAULT 0,
        equilibrium INTEGER NOT NULL DEFAULT 0,
        price       REAL NOT NULL,
        discount    REAL    NOT NULL DEFAULT 0,
        has_channel BOOLEAN NOT NULL DEFAULT 0 CHECK(has_channel IN (0, 1))
    );""",
        """CREATE TABLE IF NOT EXISTS owned_roles (
        user_id      INTEGER NOT NULL,
        role_id      INTEGER NOT NULL,
        amount       REAL NOT NULL DEFAULT 1,
        shield       REAL NOT NULL DEFAULT 0,
        PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id)
                REFERENCES agents (user_id)
                ON DELETE CASCADE,
            FOREIGN KEY (role_id)
                REFERENCES roles (role_id)
                ON DELETE CASCADE
    );""",
        """CREATE TABLE IF NOT EXISTS deals (
        message_id       INTEGER UNIQUE NOT NULL,
        author_user_id   INTEGER NOT NULL,
        channel_id       INTEGER NOT NULL,
        offers           TEXT NOT NULL,
        demands          TEXT,
        status           INTEGER NOT NULL DEFAULT 0 CHECK(status IN (0, 1, 2, 3)),
        resolution       TIMESTAMP,
        accepter_user_id INTEGER,
        comment          TEXT,
        expiration       TIMESTAMP,
        uses_left        INTEGER,
        cost_added_when_accepted REAL NOT NULL DEFAULT 0,
        cost_subtracted_per_minute REAL NOT NULL DEFAULT 0
    );""",
        """CREATE TABLE IF NOT EXISTS hiding_spots (
        channel_name TEXT NOT NULL,
        description  TEXT NOT NULL,
        contents     TEXT NOT NULL,
        UNIQUE (channel_name, description)
    );""",
        """CREATE TABLE IF NOT EXISTS secret_numbers (
        user_id INTEGER UNIQUE NOT NULL,
        number  REAL,
        FOREIGN KEY (user_id)
            REFERENCES agents (user_id)
            ON DELETE CASCADE
    );""",
        """CREATE TABLE IF NOT EXISTS secret_teams (
        user_id INTEGER UNIQUE NOT NULL,
        team    INTEGER NOT NULL,
        FOREIGN KEY (user_id)
            REFERENCES agents (user_id)
            ON DELETE CASCADE
    );""",
        """CREATE TABLE IF NOT EXISTS owned_items (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        item_type INTEGER NOT NULL,-- CHECK(item_type IN (1, 2, 3, 4)),
        string_representation TEXT NOT NULL,
        amount REAL NOT NULL,
        UNIQUE (user_id, item_type, string_representation)
    );""",
        """CREATE TABLE IF NOT EXISTS owned_agents (
        owner_user_id INTEGER NOT NULL,
        owned_user_id INTEGER NOT NULL,
        PRIMARY KEY (owner_user_id, owned_user_id),
        FOREIGN KEY (owner_user_id)
            REFERENCES agents (user_id)
                ON DELETE CASCADE,
        FOREIGN KEY (owned_user_id)
            REFERENCES agents (user_id)
                ON DELETE CASCADE
    );""",
        """CREATE TABLE IF NOT EXISTS suspicious_terms (
        user_id INTEGER NOT NULL,
        term    TEXT UNIQUE NOT NULL
    );""",
        """CREATE TABLE IF NOT EXISTS moods (
          name TEXT UNIQUE NOT NULL,
          value REAL NOT NULL
        );""",
        # profile refresh request system:
        "DROP TABLE IF EXISTS pending_profile_refreshes",
        # """CREATE TABLE IF NOT EXISTS pending_profile_refreshes (
        #     user_id INTEGER UNIQUE
        # );""",
        "DROP TRIGGER IF EXISTS request_pending_profile_refresh_on_agents_update",
        # """CREATE TRIGGER IF NOT EXISTS request_pending_profile_refresh_on_agents_update
        #     AFTER UPDATE OF profile_message_id, credit, loyalty, selfdescription
        #     ON agents
        # BEGIN
        #     INSERT OR IGNORE
        #     INTO pending_profile_refreshes (user_id)
        #     VALUES (NEW.user_id);
        # END;""",
        "DROP TRIGGER IF EXISTS request_pending_profile_refresh_on_agent_roles_insert",
        # """CREATE TRIGGER IF NOT EXISTS request_pending_profile_refresh_on_agent_roles_insert
        #     AFTER INSERT
        #     ON owned_roles
        # BEGIN
        #     INSERT OR IGNORE
        #     INTO pending_profile_refreshes (user_id)
        #     VALUES (NEW.user_id);
        # END;""",
        "DROP TRIGGER IF EXISTS request_pending_profile_refresh_on_agent_roles_update",
        # """CREATE TRIGGER IF NOT EXISTS request_pending_profile_refresh_on_agent_roles_update
        #     AFTER UPDATE
        #     ON owned_roles
        # BEGIN
        #     INSERT OR IGNORE
        #     INTO pending_profile_refreshes (user_id)
        #     VALUES (NEW.user_id);
        # END;""",
        "DROP TRIGGER IF EXISTS request_pending_profile_refresh_on_agent_roles_delete",
        # """CREATE TRIGGER IF NOT EXISTS request_pending_profile_refresh_on_agent_roles_delete
        #     AFTER DELETE
        #     ON owned_roles
        # BEGIN
        #     INSERT OR IGNORE
        #     INTO pending_profile_refreshes (user_id)
        #     VALUES (OLD.user_id);
        # END;""",
        # discord role addition and removal system:
        """CREATE TABLE IF NOT EXISTS pending_discord_role_operations (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        is_addition BOOLEAN NOT NULL CHECK(is_addition IN(0, 1)),
        UNIQUE (user_id, role_id)
    );""",
        "DROP TRIGGER IF EXISTS discord_role_review_on_update",
        """CREATE TRIGGER IF NOT EXISTS discord_role_review_on_update
        AFTER UPDATE OF amount
        ON owned_roles
        WHEN NEW.amount < 1 != OLD.amount < 1
    BEGIN
        INSERT INTO pending_discord_role_operations (user_id, role_id, is_addition)
            VALUES (NEW.user_id, NEW.role_id, NEW.amount > OLD.amount)
            ON CONFLICT (user_id, role_id)
            DO UPDATE SET is_addition = excluded.is_addition;
    END;""",
        "DROP TRIGGER IF EXISTS discord_role_review_on_insert",
        """CREATE TRIGGER IF NOT EXISTS discord_role_review_on_insert
        AFTER INSERT
        ON owned_roles
        WHEN NEW.amount >= 1
    BEGIN
        INSERT INTO pending_discord_role_operations (user_id, role_id, is_addition)
            VALUES (NEW.user_id, NEW.role_id, 1)
            ON CONFLICT (user_id, role_id)
            DO UPDATE SET is_addition = excluded.is_addition;
    END;""",
        "DROP TRIGGER IF EXISTS discord_role_review_on_delete",
        """CREATE TRIGGER IF NOT EXISTS discord_role_review_on_delete
        AFTER DELETE
        ON owned_roles
        WHEN OLD.amount >= 1
    BEGIN
        INSERT INTO pending_discord_role_operations (user_id, role_id, is_addition)
            VALUES (OLD.user_id, OLD.role_id, 0)
            ON CONFLICT (user_id, role_id)
            DO UPDATE SET is_addition = excluded.is_addition;
    END;""",
        # useless rows are deleted
        "DROP TRIGGER IF EXISTS empty_row_deleter_owned_items",
        # """CREATE TRIGGER IF NOT EXISTS empty_row_deleter_owned_items
        #     AFTER UPDATE OF amount
        #     ON owned_items
        #     WHEN NEW.amount == 0
        # BEGIN
        #     DELETE FROM owned_items
        #     WHERE id = OLD.id;
        # END;""",
        "DROP TRIGGER IF EXISTS empty_row_deleter_owned_roles",
        # TODO: this was causing trouble and it's just a small storage optimization
        # """CREATE TRIGGER IF NOT EXISTS empty_row_deleter_owned_roles
        #     AFTER UPDATE OF amount, shield, contribution
        #     ON owned_roles
        #     WHEN NEW.amount = 0 AND NEW.shield = 0 AND NEW.contribution = 0
        # BEGIN
        #     DELETE FROM owned_roles
        #     WHERE user_id = NEW.user_id AND role_id = NEW.role_id;
        # END;""",
    ]

    def __init__(self, path: str) -> None:

        self.con = sqlite3.connect(path)
        self.con.create_function("CALCULATE_ROLE_PRICE", 1, calculate_role_price)
        self.cur = self.con.cursor()

        for statement_string in self.setup_statements:
            try:
                self.cur.execute(statement_string)
            except Error as e:
                create_task(
                    debug_print(
                        statement_string
                        + "\n"
                        + ("".join(format_exception(None, e, e.__traceback__)))
                    )
                )

        self.con.commit()

    def exec(self, *args) -> None:
        self.cur.execute(*args)
        self.con.commit()

    def close(self) -> None:
        if self.con:
            self.con.close()


class Proposal:
    def __init__(self, values: tuple = None):
        
        if values:
            (
                self.proposal_id,
                self.message_id,
                status_int,
                type_int,
                self.author_user_id,
                self.description,
                self.file_data,
                self.file_path,
            ) = values
            self.status = ProposalStatus(status_int)
            self.type = ProposalType(type_int)
        else:
            self.proposal_id: int = -1
            self.message_id: int = -1
            self.status: ProposalStatus = ProposalStatus.PENDING
            self.type: ProposalType = ProposalType.LAW
            self.description: str = ""
            self.author_user_id: int = -1
            self.file_path = None
        self.index: int = self.proposal_id - 1

    def generate_message_content(self, approval):
        return (
            voice_filter(f"Proposed {self.type.name} #{self.index}. React with 👍 or 👎")
            + (
                voice_filter(f"\n\nDescription:") + f"```{self.description}```"
                if len(self.description) > 0
                else ""
            )
            + voice_filter(
                f"\nApproval: {approval}/{approval_threshold()} ({self.status.name})\n\n"
            )
        )

    async def generate_from_command(self, command_message: Message):
        command = command_message.content[3:].lower().split()
        if len(command) > 1 and command[1] in ["law", "order"]:
            self.type = (
                ProposalType.LAW
                if command[1] == "law"
                else ProposalType.ORDER
            )
            if self.type == ProposalType.LAW:
                self.description = " ".join(command[3:])
            else:
                self.description = " ".join(command[2:])
        else:
            return False

        if len(command_message.attachments) == 0:
            await command_message.channel.send(
                voice_filter("You have to attach the file with your proposal's code!")
            )
            return

        # Try to typecheck file
        attachment = command_message.attachments[0]

        attachment_content = await attachment.read()
        if command[1] == "law":
            content = attachment_content
        else:
            with open(OWN_FILE, "r") as f:
                main_content = f.read()

            order_code = attachment_content.decode("utf-8")
            order_code = f"async def _order(): " + "".join(
                f"\n {l}" for l in order_code.split("\n")
            )
            # Make a file that's the proposal but at the end of the main source code
            content = (
                main_content + "\n\n" + order_code + "\n"
            )  # input must end with \n for compile('eval')

        self.file_path = command[2]

        if self.file_path.endswith(".py"):
            try:
                compile(content, "proposal.py", "exec")
            except Exception as e:
                await command_message.channel.send(
                    voice_filter(f"Would-be {self.type.name} proposal misbehaved.")
                )

                await debug_print("".join(format_exception(None, e, e.__traceback__)))

                return

        # File has typechecked, continue

        self.author_user_id = command_message.author.id

        # if there are words after "order"/"law", they are used as the proposal's description
        # if len(command) > 2:
        #     self.description = " ".join(command[2:])

        db.cur.execute("SELECT Count(*) FROM proposals")
        self.index = db.cur.fetchone()[0]

        path = f"{PROPOSALS_DIR}/{self.index}.py"
        await attachment.save(path)

        message = await get_channel_named(PROPOSALS_CHANNEL_NAME).send(
            self.generate_message_content(0),
            file=File(path, filename=f"{self.index}.py"),
        )
        self.message_id = message.id

        db.exec(
            "INSERT INTO proposals(message_id,type,author_user_id,description,file_path) VALUES(?,?,?,?,?)",
            (self.message_id, self.type, self.author_user_id, self.description, self.file_path),
        )

        # reacting with the voting emojis so that users don't have to look for them
        for emoji in ["👍", "👎"]:
            await message.add_reaction(emoji)

        return True

    async def tally_votes(self, message: Message = None):
        if message is None or message.id != self.message_id:
            message = await get_channel_named(PROPOSALS_CHANNEL_NAME).fetch_message(
                self.message_id
            )

        approval = 0

        for reaction in message.reactions:
            if reaction.emoji in {"👍", "👎"}:
                direction = +1 if reaction.emoji == "👍" else -1
                async for user in reaction.users():
                    if user.id != get_guild().me.id:
                        loyalty = Agent(user.id).loyalty

                        # to prevent profiles not working from preventing all changes:
                        if loyalty == 0:
                            loyalty = 1

                        approval += direction * loyalty

        if approval >= approval_threshold():

            await self._try_to_pass(message, approval)

        elif approval <= -approval_threshold():

            self.set_status(ProposalStatus.FAILED)
            await message.channel.send(
                voice_filter(
                    f"{self.type.name} #{self.index} failed because it was voted down."
                )
            )

        await message.edit(content=self.generate_message_content(approval))

    async def _try_to_pass(self, message, approval):
        proposal_path = f"{PROPOSALS_DIR}/{self.index}.py"

        if self.type == ProposalType.LAW:

            if (
                subprocess.run(
                    ["python3", proposal_path, "--bootlick"],
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                == APPROVED_RESPONSE_TO_DICTATOR
            ) or not self.file_path.endswith(".py"):
                if self.status == ProposalStatus.PASSED:
                    return
                self.set_status(ProposalStatus.PASSED)
                pass_message_task = create_task(
                    message.channel.send(
                        voice_filter(
                            f"Proposal #{self.index} ({self.type.name}) passed!"
                        )
                    )
                )

                # fail all older proposals:
                for i in range(self.index - 1, 0, -1):
                    p = get_proposal(i)
                    if p.type == ProposalType.LAW and p.status == ProposalStatus.PASSED:
                        break
                    elif (
                        p.type == ProposalType.LAW
                        and p.status == ProposalStatus.PENDING
                    ):
                        await pass_message_task
                        await message.channel.send(
                            voice_filter(
                                f"Proposal #{i} ({p.type.name}) failed because a newer proposal passed."
                            )
                        )
                        p.set_status(ProposalStatus.FAILED)

                # THIS IS A BAD SYSTEM PLEASE FIX
                # CHANGES WILL TOTALLY OVERRIDE ANY MADE AFTER THEY WERE UPLOADED
                with open(self.file_path, "w") as f:
                    with open(proposal_path) as g:
                        f.write(g.read())

                await message.edit(content=self.generate_message_content(approval))

                # restart to apply changes
                create_task(restart("new law passed", PROPOSALS_CHANNEL_NAME))
                return

            else:
                self.set_status(ProposalStatus.FAILED)
                await message.channel.send(
                    voice_filter(
                        f"Proposal #{self.index} ({self.type.name}) was vetoed by {APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR} for disrespect."
                    )
                )

        else:  # proposal that just passed is of type "order"

            with open(proposal_path, "r") as f:

                code = f.read()

                if self.status == ProposalStatus.PENDING:

                    self.set_status(ProposalStatus.PASSED)
                    try:

                        await message.channel.send(
                            voice_filter(f"Execute order #{self.index}.")
                        )

                        # Make an async function with the code and `exec` it
                        exec(
                            f"async def _order(): "
                            + "".join(f"\n {l}" for l in code.split("\n")),
                            globals(),
                            locals(),  # TODO: remove this argument, probably
                        )

                        await locals()["_order"]()

                    except Exception as e:

                        await get_channel_named(GENERAL_CHANNEL_NAME).send(
                            voice_filter(
                                f"How dare you make this obviously fixable error: ",
                                f"```{''.join(format_exception(None, e, e.__traceback__))}```",
                            )
                        )

                        await message.channel.send(
                            voice_filter(
                                f"Proposal #{self.index} ({self.type.name}) misbehaved."
                            )
                        )

    def set_status(self, status: ProposalStatus):
        self.status = status
        db.exec(
            "UPDATE proposals SET status = ? WHERE proposal_id = ?",
            (self.status, self.proposal_id),
        )


class Agent:
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def exists(self) -> bool:
        db.cur.execute(
            "SELECT EXISTS(SELECT 1 FROM agents WHERE user_id = ?)", (self.user_id,)
        )
        return db.cur.fetchone()[0]

    def create(self) -> None:
        db.cur.execute(
            "INSERT OR IGNORE INTO agents (user_id) VALUES (?)", (self.user_id,)
        )

    def get_member(self) -> Member:
        return get_guild().get_member(self.user_id)

    def get_fields(self, *field_names) -> tuple:
        valid_field_names = {
            "user_id",
            "profile_message_id",
            "credit",
            "loyalty",
            "selfdescription",
            "ascensions",
        }
        for field_name in field_names:
            if field_name not in valid_field_names:
                raise MeWhiningException(
                    "invalid field name",
                    "You're requesting information on an agent that simply isn't available",
                )
        db.cur.execute(
            f"SELECT {','.join(field_names)} FROM agents WHERE user_id = ?",
            (self.user_id,),
        )
        return db.cur.fetchone()

    def get_field(self, field_name) -> any:
        if field_name not in {
            "user_id",
            "profile_message_id",
            "credit",
            "loyalty",
            "selfdescription",
            "ascensions",
        }:
            raise MeWhiningException(
                "invalid field name",
                "You're requesting information on an agent that simply isn't available.",
            )
        db.cur.execute(
            f"SELECT {field_name} FROM agents WHERE user_id = ?", (self.user_id,)
        )
        row = db.cur.fetchone()
        if row is not None:
            return row[0]

    def get_roles(self) -> Dict[Role, float]:
        db.cur.execute(
            """SELECT o.role_id, o.amount
               FROM owned_roles AS o JOIN roles as r ON o.role_id = r.role_id
               WHERE o.user_id = ? AND o.amount > 0
               ORDER BY o.amount * r.price DESC""",
            (self.user_id,),
        )
        role_collection = {}
        g = get_guild()
        for row in db.cur.fetchall():
            role_collection[g.get_role(row[0])] = row[1]
        return role_collection

    def get_agents(self) -> Dict[Agent, float]:
        db.cur.execute(
            """SELECT string_representation, amount
            FROM owned_items
            WHERE user_id = ? AND item_type = ?""",
            (self.user_id, ItemType.AGENT),
        )
        res = db.cur.fetchall()
        ids = {}
        for rep, amt in res:
            agent = AgentItem(0)
            agent.parse_name(rep)
            ids.update({agent.agent.user_id: amt})

        return ids

    def get_words(self) -> ItemGroup:
        db.cur.execute(
            """SELECT string_representation, amount
            FROM owned_items
            WHERE user_id = ? AND item_type = ? AND amount > 0""",
            (self.user_id, ItemType.WORD),
        )
        return ItemGroup(
            [WordItem(word=rep, amount=amount) for rep, amount in db.cur.fetchall()]
        )

    def get_profile_embed(self, is_profile_message=True) -> Embed:

        m = self.get_member()

        if m is not None:

            if m.avatar_url:
                thumbnail_url = m.avatar_url
            else:
                thumbnail_url = client.get_user(m.id).avatar_url

            res = Embed(
                title=f"Agent #{m.id}",
                description=f"Or as they're often known, {m.mention}.",
                color=m.color,
            ).set_thumbnail(url=thumbnail_url)

            res.add_field(name="Ascensions", value=str(self.get_field("ascensions")))

            role_collection = self.get_roles()
            role_strings = [
                f"{amount:g} {role.mention}"
                for role, amount in role_collection.items()
                if role is not None
            ]

            # Discord imposes a limit on the length of our fields
            # Split it up if a user has too many roles
            role_displays = None
            if len(role_strings) == 0:
                role_displays = ["This user is poor."]
            else:
                idx = 0
                role_displays = [role_strings[0]]
                for role_string in role_strings[1:]:
                    # Create another field if the first is going to be too long
                    if len(role_displays[idx]) + len(role_string) > 1000:
                        idx += 1
                        role_displays.append(role_string)
                    else:
                        role_displays[idx] += f", {role_string}"

            if len(role_displays) == 1:
                res.add_field(name="Roles", value=role_displays[0], inline=False)
            else:
                for num, embed_field in enumerate(role_displays):
                    res.add_field(name=f"Roles #{num}", value=embed_field, inline=False)

            agent_collection = self.get_agents()
            agent_strings = [
                f"{amount:g} <@{agent}>"
                for agent, amount in agent_collection.items()
                if agent is not None
            ]
            if len(agent_strings) == 0:
                agent_field = "This agent is owner to no one."
            else:
                agent_field = ", ".join(agent_strings)

            res.add_field(name="Agents", value=agent_field, inline=False)

            # res.add_field(
            #     name="Roles", value=, inline=False
            # )
            res.add_field(
                name="Joined",
                value=f"{datetime_to_discord_timestamp(m.joined_at, 'R')}",
                inline=False,
            )

            (selfdescription, loyalty, credit) = self.get_fields(
                "selfdescription", "loyalty", "credit"
            )
            if selfdescription is not None:
                res.add_field(
                    name="Self-describes As", value=f"{selfdescription}", inline=False
                )

            maybe_explain = (
                " (react with 👍 if they're loyal or 👎 if not)"
                if is_profile_message
                else ""
            )
            res.add_field(name="Loyalty", value=f"{loyalty}{maybe_explain}")

            res.add_field(name="Credit", value=f"{credit:g}", inline=False)
            return res

        else:
            return Embed(
                title="Agent missing",
                description="That agent has probably left the server.",
                color=0x888888,
            )

    def has_profile(self) -> bool:
        return self.get_field("profile_message_id") not in [-1, None]

    async def get_profile_message(self) -> Optional[Message]:
        try:
            channel = get_channel_named(PROFILES_CHANNEL_NAME)
            return await channel.fetch_message(self.get_field("profile_message_id"))
        except:
            return None

    def edit(self, commit: bool = True, **fields) -> None:
        """
        Updates credit, selfdescription, loyalty and/or profile_message_id in the database.
        """
        allowed_field_names = {
            "profile_message_id",
            "credit",
            "loyalty",
            "selfdescription",
            "ascensions",
        }
        sql = "UPDATE agents SET to_refresh = 1, "
        names = []
        variables = []
        for field_name in fields:
            if field_name not in allowed_field_names:
                raise MeWhiningException(
                    "invalid field name when trying to update agents",
                    "You're asking me to update a thing that should not be updated",
                )
            else:
                names.append(field_name)
                variables.append(fields[field_name])
        if variables:
            variables.append(self.user_id)
            db.exec(
                sql + " = ?, ".join(names) + " = ? WHERE user_id = ?", tuple(variables)
            )
            if commit:
                db.con.commit()

    def update_field(self, field_name: str, value: any, commit: bool = True) -> None:
        if field_name in ["profile_message_id", "credit", "loyalty", "selfdescription"]:
            db.cur.execute(
                f"UPDATE agents SET to_refresh = 1, {field_name} = ? WHERE user_id = ?",
                (
                    value,
                    self.user_id,
                ),
            )
        else:
            raise MeWhiningException(
                "invalid field name when trying to update agents",
                "You're asking me to update a thing that should not be updated",
            )
        if commit:
            db.con.commit()

    async def publish_profile(self) -> None:
        message: Message = await get_channel_named(PROFILES_CHANNEL_NAME).send(
            "\u200c",
            embed=self.get_profile_embed(),
        )
        self.update_field("profile_message_id", message.id)

        # reacting with the voting emojis so that users don't have to look for them
        # (except not always)
        voting_emoji = ["👍", "👎"]
        if random.random() < (0.4 * get_mood("degrence")):
            voting_emoji = random.choice(
                [
                    ["👊", "👎"],
                    ["👍", "🤙"],
                    ["👉", "👈"],
                    ["🤛", "🤜"],
                    ["👎", "👍"],
                    ["👆", "👇"],
                ]
            )
        for emoji in voting_emoji:
            await message.add_reaction(emoji)

    async def refresh_profile(self) -> None:
        if self.has_profile():
            message = await self.get_profile_message()
            if message is not None:
                await message.edit(
                    content="\u200c",
                    embed=self.get_profile_embed(),
                )
            else:
                await self.publish_profile()

    async def hide_profile(self) -> None:
        message = await self.get_profile_message()
        if message is not None:
            await message.delete()
        self.edit(loyalty=0, profile_message_id=-1)

    @property
    def loyalty(self):
        """"""
        db.cur.execute(f"SELECT loyalty FROM agents WHERE user_id = ?", (self.user_id,))
        row = db.cur.fetchone()
        if row is not None:
            return row[0]

    @loyalty.setter
    def loyalty(self, value):
        self.edit(loyalty=value)

    @property
    def selfdescription(self):
        """"""
        return self.get_field("selfdescription")

    @selfdescription.setter
    def selfdescription(self, value):
        self.edit(selfdescription=value)

    def give(self, item_or_items: Union[Item, ItemGroup]) -> None:
        item_or_items.give_to(self.user_id)

    def take(self, item_or_items: Union[Item, ItemGroup]) -> None:
        item_or_items.take_from(self.user_id)

    def ascend(self):
        ascensions = self.get_field("ascensions") + 1
        if (ascensions ** 0.5).is_integer():
            n = int(ascensions ** 0.5)
            create_task(
                get(get_guild().channels, name=f"ascension-{n}").set_permissions(
                    self.get_member(), view_channel=True
                )
            )
        self.edit(ascensions=ascensions)
        self.take(CreditItem(self.get_field("credit")))

        roles = self.get_roles()
        for role in roles:
            amount_to_take = roles[role]
            self.take(RoleItem(role, amount_to_take))

    def punish_wallet(self, factor: float = 1.0) -> float:
        credit = self.get_field("credit")
        amount_taken = max(1, ceil(mood(credit * 0.01 * factor), anger=2))
        self.take(CreditItem(amount_taken))
        return amount_taken


@unique
class ItemType(IntEnum):
    CREDIT = 0
    ROLE = 1
    FILE = 2
    WORD = 3
    COLOR = 4
    AGENT = 5


class BaseItem(ABC):

    amount: float = 1.0

    def __init__(
        self,
        amount: Union[float, int, str, None],
    ) -> None:
        if amount == str(amount):
            self.parse_amount(amount)
        elif amount is not None:
            self.amount = float(amount)
        if self.amount <= 0:
            if self.amount < 0:
                raise MeWhiningException(
                    "negative amount of item", "Negative items will *not* be tolerated"
                )
            else:
                raise MeWhiningException(
                    "empty item", "Do not waste my storage space with empty items"
                )

    @staticmethod
    @abstractmethod
    def can_parse(value_string: str) -> bool:
        return NotImplemented

    def parse_amount(self, amount_string: str) -> None:
        if not amount_string:
            self.amount = 1.0
        else:
            try:
                self.amount = float(amount_string)
            except ValueError:
                raise MeWhiningException(
                    f"item amount couldn't be parsed as float: '{amount_string}'",
                    f"What kind of number is '{amount_string}'?",
                )

    @abstractmethod
    def to_english(self) -> str:
        """"""  # TODO:

    @abstractmethod
    def get_type(self) -> ItemType:
        """"""  # TODO:

    @abstractmethod
    def give_to(self, user_id: int, commit=True, invert=False) -> None:
        """"""  # TODO:

    def take_from(self, user_id: int, commit=True, invert=False) -> None:
        """
        If not implemented, give_to(invert=True) is called.
        """
        self.give_to(user_id, commit, invert=not invert)

    @abstractmethod
    def is_owned_by(self, user_id: int) -> bool:
        """"""  # TODO:


Item = TypeVar("Item", bound=BaseItem)


class DistinctItem(BaseItem):
    """Item class with a value and not just an amount"""

    def to_english(self) -> str:
        if self.amount != 1:
            return f"{self.amount:g} {self.name_to_string()}"
        else:
            return self.name_to_string()

    @abstractmethod
    def parse_name(self, value_string: str) -> None:
        """"""  # TODO:

    @abstractmethod
    def name_to_string(self) -> str:
        """"""  # TODO:

    def give_to(self, user_id: int, commit=True, invert=False) -> None:
        amount = self.amount if not invert else -self.amount
        db.cur.execute(
            """
            INSERT INTO owned_items (user_id, item_type, string_representation, amount)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(user_id, item_type, string_representation)
                DO UPDATE SET amount = amount + excluded.amount;
            """,
            (
                user_id,
                self.get_type(),
                self.name_to_string(),
                amount,
            ),
        )
        if commit:
            db.con.commit()

    def is_owned_by(self, user_id: int) -> bool:
        db.cur.execute(
            """
            SELECT amount
                FROM owned_items
                WHERE user_id = ? AND item_type = ? AND string_representation = ? AND amount >= ?
            """,
            (
                user_id,
                self.get_type(),
                self.name_to_string(),
                self.amount,
            ),
        )
        return db.cur.fetchone() is not None


class CreditItem(BaseItem):
    @staticmethod
    def can_parse(value_string: str) -> bool:
        return bool(re.match(r"^c[\w\s]*$", value_string))

    def to_english(self) -> str:
        return f"{self.amount:g}c"

    def get_type(self) -> ItemType:
        return ItemType.CREDIT

    def give_to(self, user_id: int, commit=True, invert=False) -> None:
        amount = self.amount if not invert else -self.amount
        db.cur.execute(
            "UPDATE agents SET to_refresh = 1, credit = credit + ? WHERE user_id = ?",
            (
                amount,
                user_id,
            ),
        )
        if commit:
            db.con.commit()

    def is_owned_by(self, user_id: int) -> bool:
        db.cur.execute(
            "SELECT credit FROM agents WHERE user_id = ? AND credit >= ?",
            (
                user_id,
                self.amount,
            ),
        )
        return db.cur.fetchone() is not None


class RoleItem(DistinctItem):
    def __init__(
        self,
        role: Union[Role, int, str] = None,
        amount: Union[float, int, str, None] = None,
    ) -> None:
        if isinstance(role, int):
            self.role = get_role(role)
        elif isinstance(role, str):
            self.parse_name(role)
        else:
            self.role = role
        super().__init__(amount=amount)
        if self.role is None:
            raise MeWhiningException(
                "could not find role with that id",
                f"There is no such role under my domain",
            )

    @staticmethod
    def can_parse(value_string: str) -> bool:
        return bool(re.match(r"^@[^\s](.*[^\s])?|^<@&\d+>$", value_string))

    def parse_name(self, value_string: str) -> None:
        if value_string.startswith("<@&"):
            try:
                role_id = int(value_string[3:-1])
                self.role = get_role(role_id)
                if self.role is None:
                    raise MeWhiningException(
                        "invalid role id",
                        f"{role_id}? There's no role with that ID under my domain",
                    )
            except ValueError:
                raise MeWhiningException(
                    "invalid role expression",
                    f"What kind of role even is '{value_string}'",
                )
        elif value_string[0] == "@":
            self.role = get_role_named(value_string[1:])
            if self.role is None:
                raise MeWhiningException(
                    "invalid role name",
                    f"'{value_string}'? There's no role with that name under my domain",
                )
        else:
            raise MeWhiningException(
                "invalid role expression", f"What kind of role even is '{value_string}'"
            )

    def name_to_string(self) -> str:
        return self.role.mention

    def get_type(self) -> ItemType:
        return ItemType.ROLE

    def give_to(self, user_id: int, commit=True, invert=False) -> None:
        amount = self.amount if not invert else -self.amount
        # db.cur.execute(
        #     "UPDATE owned_roles SET amount = amount + ? WHERE agent_id = ? AND role_id = ?",
        #     (amount, user_id, self.value,)
        # )
        # db.cur.execute(
        #     "INSERT INTO owned_roles (user_id, role_id, amount) SELECT ?, ?, ? WHERE (SELECT CHANGES() = 0)",
        #     (user_id, self.value, amount,)
        # )
        db.cur.execute(
            """
            INSERT INTO owned_roles (user_id, role_id, amount)
                VALUES(?, ?, ?)
                ON CONFLICT(user_id, role_id)
                DO UPDATE SET amount = amount + excluded.amount;
            """,
            (
                user_id,
                self.role.id,
                amount,
            ),
        )
        db.cur.execute("UPDATE agents SET to_refresh = 1 WHERE user_id = ?", (user_id,))
        if commit:
            db.con.commit()

    def is_owned_by(self, user_id: int) -> bool:
        db.cur.execute(
            "SELECT amount FROM owned_roles WHERE user_id = ? AND role_id = ? AND amount >= ?",
            (
                user_id,
                self.role.id,
                self.amount,
            ),
        )
        return db.cur.fetchone() is not None


class FileItem(DistinctItem):
    def __init__(
        self,
        path: Optional[str] = None,
        amount: Union[float, int, str, None] = None,
    ) -> None:
        if path is not None:
            self.parse_name(path)
        super().__init__(amount=amount)
        if self.path is None:
            raise MeWhiningException("", "")  # TODO: fill this

    @staticmethod
    def can_parse(value_string: str) -> bool:
        return bool(re.match(r"(/\w+(\.\w+)*)+", value_string))

    def parse_name(self, value_string: str) -> None:
        self.path = value_string.strip("/")

    def name_to_string(self) -> str:
        return f"/{self.path}"

    def get_type(self) -> ItemType:
        return ItemType.FILE


class WordItem(DistinctItem):
    def __init__(
        self,
        word: Optional[str] = None,
        amount: Union[float, int, str, None] = None,
    ) -> None:
        if word is not None:
            self.parse_name(word)
        super().__init__(amount=amount)
        if self.word is None:
            raise MeWhiningException("", "")  # TODO: fill this

    @staticmethod
    def can_parse(value_string: str) -> bool:
        return bool(re.match(r'"[a-zA-Z]+"', value_string))

    def parse_name(self, value_string: str) -> None:
        self.word = value_string.strip('"_ ')
        if len(self.word) == 0:
            raise MeWhiningException("empty word", "")  # TODO: fill this

    def name_to_string(self) -> str:
        return f'"{self.word}"'

    def get_type(self) -> ItemType:
        return ItemType.WORD


class ColorItem(DistinctItem):
    def __init__(
        self,
        color: Union[Colour, int, str] = None,
        amount: Union[float, int, str, None] = None,
    ) -> None:
        if isinstance(color, int):
            self.color = Colour(color)
        elif isinstance(color, str):
            self.parse_name(color)
        else:
            self.color = color
        super().__init__(amount=amount)
        if self.color is None:
            raise MeWhiningException(
                "color does not exist", "Don't go around making up colors"
            )

    @staticmethod
    def can_parse(value_string: str) -> bool:
        return bool(re.match(r"0x\d+|Color\(\s*(0x)?\d+\s*\)", value_string))

    def parse_name(self, value_string: str) -> None:
        result = re.search(r"((0x)?\d+)", value_string)
        self.color = Colour(int(result.group(), 0))
        # TODO: catch possible exceptions

    def name_to_string(self) -> str:
        return f"Color({format(self.color.value, '#x')})"

    def get_type(self) -> ItemType:
        return ItemType.COLOR


class AgentItem(DistinctItem):
    def __init__(
        self,
        agent: Union[Agent, int, str] = None,
        amount: Union[float, int, str, None] = None,
    ) -> None:
        if isinstance(agent, int):
            self.agent = Agent(agent)
        elif isinstance(agent, str):
            self.parse_name(agent)
        else:
            self.agent = agent
        super().__init__(amount=amount)
        if self.agent is None:
            raise MeWhiningException(
                "agent does not exist", "I can tell when an agent doesn't exist"
            )

    @staticmethod
    def can_parse(value_string: str) -> bool:
        return bool(re.match(r"<@!?\d+>", value_string))

    def parse_name(self, value_string: str) -> None:
        result = re.search(r"<@!?(\d+)>", value_string)
        self.agent = Agent(int(result.group(1)))
        # TODO: catch possible exceptions

    def name_to_string(self) -> str:
        return mention_member(self.agent.user_id)

    def get_type(self) -> ItemType:
        return ItemType.AGENT

    def give_to(self, user_id: int, commit=True, invert=False) -> None:
        super().give_to(user_id, False, invert)
        db.cur.execute(
            "DELETE FROM owned_items WHERE user_id = ? AND item_type = ? AND string_representation = ?",
            (self.agent.user_id, self.get_type(), self.name_to_string()),
        )
        if commit:
            db.con.commit()


class ItemGroup:
    def __init__(self, item_list: Optional[List[Item]] = None) -> None:
        if item_list is None:
            self.item_list = []
        else:
            self.item_list = item_list

    def to_bytes(self) -> bytes:
        return dumps(self.to_english())

    def to_english(self) -> str:
        if len(self.item_list):
            l = []
            for item in self.item_list:
                l.append(item.to_english())
            return enumerate_in_english(l)
        else:
            return "nothing"

    def give_to(self, user_id: int, commit=True) -> None:
        for item in self.item_list:
            item.give_to(user_id, commit=False)
        if commit:
            db.con.commit()

    def take_from(self, user_id: int, commit=True) -> None:
        for item in self.item_list:
            item.take_from(user_id, commit=False)
        if commit:
            db.con.commit()

    def transfer_between(
        self, giver_user_id: int, taker_user_id: int, commit=True
    ) -> None:
        for item in self.item_list:
            item.take_from(giver_user_id, commit=False)
            item.give_to(taker_user_id, commit=False)
        if commit:
            db.con.commit()

    def is_owned_by(self, user_id: int) -> bool:

        # simplifying item list to prevent potential exploit
        item_dict: Dict[Union[ItemType, str], Item] = {}
        for item in self.item_list:
            if hasattr(item, "name_to_string"):
                key = item.name_to_string()
            else:
                key = item.get_type()
            if key in item_dict:
                item_dict[key].amount += item.amount
            else:
                item_dict[key] = item

        for item in item_dict.values():
            if not item.is_owned_by(user_id):
                return False
        return True

    def add(self, item: Item) -> None:
        self.item_list.append(item)

    def __add__(self, other: ItemGroup) -> None:
        self.item_list += other.item_list


class ItemGroupParser:

    # fmt: off
    next_item_pattern = re.compile(
        # ?P<name> names the group (syntax specific to python's re).
        r"^(?P<amount>\d*(\.\d+)?)"
        # the amount admits floats, but a lot of item classes don't
        + r"\s*" # *
        + r"(?P<item>.+?)"
        # this can match anything, but the last ? indicates laziness:
        # the group closes as soon as a valid separator is found. 
        + r"\s*" # *
        + r"(?P<separator>$|,|#|(?<=\s)(and|in|for)(?=\s))"
        # matches the end of the string, ",", "#" or, if surrounded by spaces, "and", "in" or "for".
        + r"\s*" # *
        + r"(?P<rest>.*)",
        # *: extra whitespace is ignored.
        flags = re.MULTILINE | re.IGNORECASE
    )
    # fmt: on

    item_group = None
    separator = None
    remaining_string = None

    def parse(self, string: str) -> ItemGroup:
        items: List[Item] = []
        self.remaining_string = string
        while self.remaining_string:
            result = self.next_item_pattern.search(self.remaining_string)
            self.separator = result.group("separator")
            self.remaining_string = result.group("rest")
            if result.group("item") != "nothing":
                items.append(
                    self.parse_item(result.group("item"), result.group("amount"))
                )
            if self.separator not in [",", "and"]:
                self.item_group = ItemGroup(items)
                return self.item_group

    def parse_item(self, name_string: str, amount_string: Optional[str] = None) -> Item:
        item_class_list_ordered: List[Item] = [
            CreditItem,
            RoleItem,
            FileItem,
            WordItem,
            ColorItem,
            AgentItem,
        ]
        for item_class in item_class_list_ordered:
            if item_class.can_parse(name_string):
                if item_class == CreditItem:  # TODO: >_<
                    return CreditItem(amount_string)
                else:
                    return item_class(name_string, amount=amount_string)


class Deal:
    def __init__(
        self,
        message_id: int = -1,
        author_user_id: int = -1,
        channel_id: int = -1,
        offers: Union[ItemGroup, bytes] = None,
        demands: Union[ItemGroup, bytes] = None,
        status: DealStatus = DealStatus.OPEN,
        # advanced options:
        comment: Optional[str] = None,
        expiration: Optional[datetime] = None,
        uses_left: Optional[int] = None,
        cost_added_when_accepted: int = 0,
        cost_subtracted_per_minute: int = 0,
    ) -> None:
        if isinstance(offers, bytes):
            parser = ItemGroupParser()
            offers = parser.parse(loads(offers))
            demands = parser.parse(loads(demands))
        self.message_id = message_id
        self.author_user_id = author_user_id
        self.channel_id = channel_id
        self.offers: ItemGroup = offers
        self.demands: ItemGroup = demands
        self.status = status
        self.comment = comment
        self.expiration = expiration
        self.uses_left = uses_left
        self.cost_added_when_accepted = cost_added_when_accepted
        self.cost_subtracted_per_minute = cost_subtracted_per_minute

    async def offer(self) -> None:
        my_message = await client.get_channel(self.channel_id).send(
            "\u200c",  # adding this so that 'edited' doesn't change message size.
            embed=self.generate_embed(),
        )
        self.message_id = my_message.id
        db.exec(
            f"""
            INSERT INTO deals(
                message_id,
                author_user_id,
                channel_id,
                offers,
                demands,
                comment,
                expiration,
                uses_left,
                cost_added_when_accepted,
                cost_subtracted_per_minute
            ) VALUES({",".join(["?"] * 10)})""",
            (
                self.message_id,
                self.author_user_id,
                self.channel_id,
                self.offers.to_bytes(),
                self.demands.to_bytes(),
                self.comment,
                self.expiration,
                self.uses_left,
                self.cost_added_when_accepted,
                self.cost_subtracted_per_minute,
            ),
        )

    async def accept(self, m2: Member, message=None):

        if message is None or message.id != self.message_id:
            message = await client.get_channel(self.channel_id).fetch_message(
                self.message_id
            )

        # check if the offer is available:
        if self.status != DealStatus.OPEN:
            if self.status != DealStatus.PROCESSING:
                await message.reply(
                    voice_filter(f"That offer is no longer on the table, {m2.mention}.")
                )
            return
        await self.set_status(DealStatus.PROCESSING)
        status_change_task = None

        m1 = get_guild().get_member(self.author_user_id)

        # check if the members are different:
        if m1.id != m2.id:

            # check if both parties can provide what they offer:
            # - dictator can always provide
            # - if none can, the offer taker is the one to be blame
            broke_member = None
            if (not self.demands.is_owned_by(m2.id)) and (m2.id != get_guild().me.id):
                broke_member = m2
            elif (not self.offers.is_owned_by(m1.id)) and (m1.id != get_guild().me.id):
                broke_member = m1

            if broke_member is None:

                # both agents can provide their side of the bargain.
                # complete trade:

                self.offers.transfer_between(m1.id, m2.id, commit=False)
                self.demands.transfer_between(m2.id, m1.id)

                status_change_task = create_task(self.set_status(DealStatus.COMPLETE))

                await message.reply(
                    voice_filter(
                        f"Transaction successful, {' and '.join([m.mention for m in [m1, m2] if m != get_guild().me])}."
                    )
                )

            else:
                subtracted = Agent(broke_member.id).punish_wallet()
                text = f"You don't have the goods, {broke_member.mention}. Your credit has decreased by {subtracted}"
                if broke_member == m1:
                    status_change_task = create_task(
                        self.set_status(DealStatus.CANCELLED)
                    )
                    text += " and your offer has been cancelled"
                await message.reply(voice_filter(f"{text}."))

        else:
            status_change_task = create_task(self.set_status(DealStatus.CANCELLED))
            await message.reply(
                voice_filter(
                    f"Do you believe I can't tell humans apart, {m2.mention}? You can't accept your own offer. It has been cancelled instead."
                )
            )

        if status_change_task is None:
            status_change_task = create_task(self.set_status(DealStatus.OPEN))

        await status_change_task

    def generate_embed(self) -> Embed:
        if self.status in [DealStatus.CANCELLED, DealStatus.COMPLETE]:
            title = f"Offer ({self.status.name})"
            color = 0x888888
        else:
            title = f"Offer ({self.status.name}: react with 🤝 to accept)"
            member = get_guild().get_member(self.author_user_id)
            if member is not None:
                color = member.color
            else:
                color = 0x888888

        res = Embed(
            title=title,
            description=f"Offered by {mention_member(self.author_user_id)}.",
            color=color,
        )

        # description = ""
        res.add_field(name="Offers", value=self.offers.to_english(), inline=False)
        res.add_field(name="Demands", value=self.demands.to_english(), inline=False)
        # if self.expiration is not None:
        #     res.add_field("Expiration", f"{datetime_to_discord_timestamp(self.expiration, 'R')}", inline=False)
        # if self.uses_left is not None:
        #     description += f"\nCan be taken {self.uses_left} more times"
        #     if self.cost_added_when_accepted != 0:
        #         description += f" (cost increases by {self.cost_added_when_accepted} every time it's taken)"
        # if self.cost_subtracted_per_minute != 0:
        #     # TODO: make this actually happen
        #     description += f"\nEvery minute, the cost goes down by {self.cost_subtracted_per_minute:g}c."
        if self.comment:
            res.description += f"*{self.comment}*"

        return res

    async def set_status(self, new_status: DealStatus) -> None:
        fetch_message_task = create_task(
            client.get_channel(self.channel_id).fetch_message(self.message_id)
        )
        if new_status == DealStatus.COMPLETE:
            db.exec(
                "UPDATE deals SET status = ?, resolution = CURRENT_TIMESTAMP WHERE message_id = ?",
                (new_status, self.message_id),
            )
        elif new_status == DealStatus.CANCELLED:
            db.exec(
                "UPDATE deals SET status = ?, resolution = CURRENT_TIMESTAMP WHERE message_id = ?",
                (new_status, self.message_id),
            )
        else:
            db.exec(
                "UPDATE deals SET status = ? WHERE message_id = ?",
                (new_status, self.message_id),
            )
        self.status = new_status
        embed = self.generate_embed()
        message = await fetch_message_task
        await message.edit(embed=embed)

    async def refresh_message(self):
        fetch_message_task = create_task(
            client.get_channel(self.channel_id).fetch_message(self.message_id)
        )
        embed = self.generate_embed()
        message = await fetch_message_task
        await message.edit(embed=embed)


class DealParser:
    item_group_parser = ItemGroupParser()
    deal = None
    remaining_string = None

    def parse(self, author_id: int, channel_id: int, string: str) -> Deal:

        self.remaining_string = string

        offers = self.item_group_parser.parse(self.remaining_string)
        separator = self.item_group_parser.separator

        if separator == "for":
            demands = self.item_group_parser.parse(
                self.item_group_parser.remaining_string
            )
            separator = self.item_group_parser.separator
        else:
            demands = ItemGroup()

        comment = None
        if separator == "#":
            comment = self.item_group_parser.remaining_string

        self.deal = Deal(
            author_user_id=author_id,
            channel_id=channel_id,
            offers=offers,
            demands=demands,
            status=DealStatus.OPEN,
            comment=comment,
        )
        return self.deal


# Some handy functions:


def get_new_client() -> Client:
    intents = Intents.default()
    intents.members = True
    intents.reactions = True
    activity = Activity(type=ActivityType.watching, name=f"you. {COMMAND_PREFIX}help")
    return commands.Bot(" ", intents=intents, activity=activity)


def get_guild() -> Guild:
    return client.guilds[0]


async def debug_print(text) -> None:
    channel = get_channel_named(LOG_CHANNEL_NAME)
    await channel.send(
        voice_filter("I have heard a message from the heavens above:")
        + f"```\n{text}```"
    )


def get_proposal(index: int) -> Optional[Proposal]:
    db.cur.execute(
        "SELECT proposal_id,message_id,status,type,author_user_id,description,file_data,file_path FROM proposals WHERE "
        "proposal_id = ?",
        (index + 1,),
    )
    values = db.cur.fetchone()
    if values:
        return Proposal(values=values)
    return None


def get_proposal_from_message_id(message_id: int) -> Optional[Proposal]:
    db.cur.execute(
        "SELECT proposal_id,message_id,status,type,author_user_id,description,file_data,file_path FROM proposals WHERE "
        "message_id = ?",
        (message_id,),
    )
    values = db.cur.fetchone()
    if values:
        return Proposal(values=values)
    return None


def get_agent(user_id: int) -> Agent:
    return Agent(user_id)


def get_agent_from_profile_message_id(id: int) -> Agent:
    db.cur.execute("SELECT user_id FROM agents WHERE profile_message_id = ?", (id,))
    row = db.cur.fetchone()
    if row is not None:
        return Agent(row[0])


def get_all_agents() -> Iterator[Agent]:
    db.cur.execute("SELECT user_id FROM agents")
    for row in db.cur.fetchall():
        yield Agent(row[0])


def get_deal(message_id: int) -> Optional[Deal]:
    db.cur.execute(
        f"""
            SELECT
                message_id,
                author_user_id,
                channel_id,
                offers,
                demands,
                status,
                comment,
                expiration,
                uses_left,
                cost_added_when_accepted,
                cost_subtracted_per_minute
            FROM deals
            WHERE
                message_id = ?
            """,
        (message_id,),
    )
    row = db.cur.fetchone()
    if row:
        return Deal(*row)


def get_channel_named(name) -> Optional[GuildChannel]:
    for channel in get_guild().channels:
        if channel.name == name:
            return channel
    # Version we would need if there were multiple Guilds:
    # return get(client.get_all_channels(), name=name)


def get_role(role_id: int) -> Optional[Role]:
    return get_guild().get_role(role_id)


def get_role_named(name) -> Optional[Role]:
    for role in get_guild().roles:
        if role.name == name:
            return role


def get_all_roles() -> Iterator[Role]:
    guild = get_guild()
    forbidden_roles = {guild.default_role, guild.self_role}
    for role in guild.roles:
        if role not in forbidden_roles:
            yield role


def get_random_role() -> Optional[Role]:
    """
    Returns a role that isn't @everyone or the bot's, or None if no such role exists.
    Every role has the same chance of being returned.
    """
    db.cur.execute(
        "SELECT role_id FROM roles WHERE role_id != ? ORDER BY Random() LIMIT 1",
        (get_guild().self_role.id,),
    )
    values = db.cur.fetchone()
    if values is not None:
        return get_guild().get_role(values[0])
    return None


def get_random_role_from_polya_urn() -> Optional[Role]:
    """
    Returns a role that isn't @everyone or the bot's, or None if no such role exists.
    The likelihood of this function returning a particular role is proportional to how many agents have it.
    """
    db.cur.execute(
        "SELECT role_id FROM owned_roles WHERE amount >= 1 AND role_id != ? ORDER BY Random() LIMIT 1",
        (get_guild().self_role.id,),
    )
    values = db.cur.fetchone()
    if values is not None:
        return get_guild().get_role(values[0])
    return None


def get_role_ownership_level(user_id: int, role_id: int) -> RoleOwnershipLevel:
    db.cur.execute(
        "SELECT amount FROM owned_roles WHERE user_id = ? AND role_id = ? AND amount > 0",
        (
            user_id,
            role_id,
        ),
    )
    row = db.cur.fetchone()
    if row is None:
        return RoleOwnershipLevel.NONE
    amount = row[0]
    db.cur.execute(
        "SELECT amount FROM owned_roles WHERE role_id = ? AND amount > 0 ORDER BY amount DESC LIMIT 2",
        (role_id,),
    )
    db.cur.fetchone()
    second_row = db.cur.fetchone()
    if second_row is None:
        return RoleOwnershipLevel.TOTALITY
    second_greatest_amount = second_row[0]
    if amount <= second_greatest_amount:
        return RoleOwnershipLevel.OWNED
    db.cur.execute(
        "SELECT Sum(amount) FROM owned_roles WHERE role_id = ? AND amount > 0",
        (role_id,),
    )
    total_amount = db.cur.fetchone()[0]
    if amount <= total_amount / 2:
        return RoleOwnershipLevel.SIMPLE_MAJORITY
    return RoleOwnershipLevel.ABSOLUTE_MAJORITY


def calculate_role_price(equilibrium: int):
    return INITIAL_ROLE_PRICE * BASE_IN_ROLE_PRICE_CALCULATION ** equilibrium


def role_price(role_id: int) -> Optional[float]:
    db.cur.execute(f"SELECT price FROM roles WHERE role_id = ?", (role_id,))
    row = db.cur.fetchone()
    if row is not None:
        return row[0]


def marginal_role_price_inc(role_id: int, n: int) -> Optional[float]:
    """Calculate the result of BUYING many roles such that their price increases"""

    db.cur.execute("SELECT equilibrium FROM roles WHERE role_id = ?", (role_id,))
    row = db.cur.fetchone()
    if row is None:
        return
    eq = row[0]

    return sum(calculate_role_price(eq + i) for i in range(n))


def marginal_role_price_dec(role_id: int, n: int) -> Optional[float]:
    """Calculate the result of SELLING many roles such that their price decreases"""

    db.cur.execute("SELECT equilibrium FROM roles WHERE role_id = ?", (role_id,))
    row = db.cur.fetchone()
    if row is None:
        return
    eq = row[0]

    return sum(calculate_role_price(eq - i) for i in range(n))


def marginal_sell_price(role_id: int, n: int) -> float:
    return marginal_role_price_dec(role_id, n) / ROLE_TAX


def marginal_buy_price(role_id: int, n: int) -> float:
    return marginal_role_price_inc(role_id, n) * ROLE_TAX


def role_price_or_zero(role_id: int) -> float:
    price = role_price(role_id)
    return price if price is not None else 0


def sell_price(role_id: int) -> float:
    return role_price_or_zero(role_id) / ROLE_TAX


def buy_price(role_id: int) -> float:
    return role_price_or_zero(role_id) * ROLE_TAX


def buy_role(buyer_id: int, role: Role) -> None:
    cost = CreditItem(buy_price(role.id))
    if cost.is_owned_by(buyer_id):
        db.cur.execute(
            f"""
            UPDATE roles
            SET price = CALCULATE_ROLE_PRICE(equilibrium + 1),
                equilibrium = equilibrium + 1
            WHERE role_id = ?
            """,
            (role.id,),
        )
        cost.take_from(buyer_id)
        RoleItem(role).give_to(buyer_id)
    else:
        raise MeWhiningException(
            "role buyer doesn't have enough credit", "You can't afford that"
        )


def sell_role(seller_id: int, role: int) -> int:
    role_item = RoleItem(role)
    if role_item.is_owned_by(seller_id):
        db.cur.execute(
            f"""
            UPDATE roles
            SET price = CALCULATE_ROLE_PRICE(equilibrium - 1),
                equilibrium = equilibrium - 1
            WHERE role_id = ?
            """,
            (role.id,),
        )
        role_item.take_from(seller_id)
        price = sell_price(role.id)
        CreditItem(price).give_to(seller_id)
        return price
    else:
        raise MeWhiningException(
            "role seller doesn't own role", "You can't afford that"
        )


async def update_loyalty(
    user_id: int, profile_message_or_its_id: Union[Message, int]
) -> None:
    if type(profile_message_or_its_id) is int:
        profile_message = await get_channel_named(PROPOSALS_CHANNEL_NAME).fetch_message(
            profile_message_or_its_id
        )
    else:
        profile_message = profile_message_or_its_id
    thumbs_up = get(profile_message.reactions, emoji="👍")
    thumbs_down = get(profile_message.reactions, emoji="👎")
    loyalty = 0
    if thumbs_up is not None:
        loyalty += thumbs_up.count
    if thumbs_down is not None:
        loyalty -= thumbs_down.count
    agent = Agent(user_id)
    if agent.loyalty != loyalty:
        agent.loyalty = loyalty


async def update_all_loyalty() -> None:
    tasks = []
    db.cur.execute(
        "SELECT user_id, profile_message_id FROM agents WHERE profile_message_id > -1"
    )
    for user_id, profile_message_id in db.cur.fetchall():
        if profile_message_id > -1:
            tasks.append(create_task(update_loyalty(user_id, profile_message_id)))
    await gather(*tasks)


async def recycle_role(role: Role, name=None, color_int=None) -> None:
    if name is None:
        name = "_".join(get_random_words(len(role.name.split("_"))))
    if color_int is None:
        color_int = get_random_color_integer()
    db.exec(
        "UPDATE roles SET name = ?, color = ? WHERE role_id = ?",
        (
            name,
            color_int,
            role.id,
        ),
    )
    await shuffle_roles()
    await role.edit(
        name=name,
        color=Colour(color_int),
        mentionable=False,
        permissions=Permissions.none(),
        hoist=True,
    )


async def get_role_parts(role: Role) -> Iterator[Item]:
    yield ColorItem(role.color)
    for word in re.compile(r"[^a-zA-Z0-9]+").split(role.name):
        yield WordItem(word)


async def shuffle_roles():
    roles = list(get_all_roles())
    random.shuffle(roles)
    positions = {}
    for i in range(len(roles)):
        positions[roles[i]] = i
    positions[get_guild().self_role] = len(roles)
    await get_guild().edit_role_positions(positions=positions)


async def create_role(name=None, color=None) -> Role:
    if name is None:
        first_word, second_word = get_random_words(2)
        name = f"{first_word}_{second_word}"
    if color is None:
        color = Colour(get_random_color_integer())
    role = await get_guild().create_role(
        name=name,
        color=color,
        mentionable=False,
        permissions=Permissions.none(),
        hoist=True,
    )
    await shuffle_roles()
    update_roles()
    return role


def update_roles() -> None:
    for role in get_all_roles():
        role_id = role.id
        name = role.name
        color = role.color.value

        db.exec(
            "INSERT OR IGNORE INTO roles(role_id, name, color) VALUES(?, ?, ?)",
            (
                role_id,
                name,
                color,
            ),
        )
        db.exec(
            "UPDATE roles SET name = ?, color = ? WHERE role_id = ?",
            (
                name,
                color,
                role_id,
            ),
        )


def get_random_words(n: int) -> Iterator[str]:
    wordlist = (
        urllib.request.urlopen("https://www.mit.edu/~ecprice/wordlist.10000")
        .read()
        .splitlines()
    )
    for _ in range(n):
        yield str(wordlist[random.randint(0, len(wordlist))])[2:-1]


def get_random_color_integer() -> int:
    return int(randomcolor.RandomColor().generate()[0][1:], base=16)


def approval_threshold(modifier: int = 0) -> int:
    """
    Minimum absolute approval score required to approve or reject a proposal.
    Currently the square root of the number of members in the server (rounded down).
    """
    return floor((get_guild().member_count + modifier) ** 0.5)


def mention_member(member_id: int) -> str:
    # return f"<@!{member_id}>"
    return f"<@{member_id}>"


def datetime_to_discord_timestamp(d: datetime, format_letter: str = "F") -> str:
    """
    format options: "R" -> relative, "D" -> date, "T" -> time, "F" -> full
    """
    return f"<t:{d.strftime('%s')}:{format_letter}>"


def role_id_from_mention(mention: str) -> int:
    return int(mention[3:-1])


def enumerate_in_english(l: list) -> str:
    if len(l) > 1:
        last = f"{l[-2]} and {l[-1]}"
        l = l[:-2]
        l.append(last)
    return ", ".join(l)


def voice_filter(*content_sections: any) -> str:
    """Filters odd arguments, concatenates all arguments and returns the resulting string"""
    replacing = True
    result = ""
    for s in content_sections:
        if replacing:
            replacement_lines = []
            for line in str(s).split("\n"):
                if line.strip() != "":
                    replacement_lines.append(f"**__{line.upper()}__**")
                else:
                    replacement_lines.append(line)
            result += "\n".join(replacement_lines)
        else:
            result += str(s)
        replacing = not replacing
    return result


def message_is_mine(message: Message) -> bool:
    return message.author == get_guild().me


def get_place_name(channel, place_description) -> str:
    return f"{channel.name}: {place_description.strip()}"


async def hide(message: Message, item_group: ItemGroup, place_description: str) -> None:
    channel = (
        message.channel if message.guild else get_channel_named(GENERAL_CHANNEL_NAME)
    )
    if item_group.is_owned_by(message.author.id):
        place_name = get_place_name(channel, place_description)
        create_task(
            channel.send(
                embed=Embed(
                    description=f"{message.author.mention} hides {item_group.to_english()}."
                )
            )
        )
        item_group.take_from(message.author.id)
        db.cur.execute("SELECT contents FROM places WHERE name = ?", (place_name,))
        result = db.cur.fetchone()
        if result is None:
            db.exec(
                "INSERT INTO places(name,contents) VALUES(?,?)",
                (place_name, item_group.to_bytes()),
            )
        else:
            already_there = ItemGroup(result[0])
            already_there += item_group
            db.exec(
                "UPDATE places SET contents = ? WHERE name = ?",
                (
                    item_group.to_bytes(),
                    place_name,
                ),
            )
    else:
        await channel.send(
            embed=Embed(
                description=f"{message.author.mention} attempts to hide {item_group.to_english()}, but they don't have that much."
            )
        )


async def search(message: Message, place_description: str) -> None:
    place_name = get_place_name(message.channel, place_description)
    db.cur.execute("SELECT contents FROM places WHERE name = ?", (place_name,))
    result = db.cur.fetchone()
    if result is None:
        await message.channel.send(
            embed=Embed(
                description=f"{message.author.mention} finds nothing in {place_description}."
            )
        )
    else:
        parser = ItemGroupParser()
        item_group = parser.parse(loads(result[0]))
        db.exec("DELETE FROM places WHERE name = ?", (place_name,))
        item_group.give_to(message.author.id)
        await message.channel.send(
            embed=Embed(
                description=f"{message.author.mention} finds {item_group.to_english()} in {place_description}."
            )
        )


def declare_secret_number(user_id: int, number) -> bool:
    try:
        n = abs(float(number) % 1)
        if isnan(n):
            return False
        # upsert isn't working:
        # db.cur.execute("INSERT INTO secret_numbers(user_id,number) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET number=excluded.number",(user_id, n))
        db.exec(
            "INSERT OR IGNORE INTO secret_numbers(user_id,number) VALUES(?,?)",
            (user_id, n),
        )
        db.exec("UPDATE secret_numbers SET number = ? WHERE user_id = ?", (n, user_id))
        return True
    except Exception as e:
        create_task(debug_print("".join(format_exception(None, e, e.__traceback__))))
        return False


async def restart(reason: str, channel_name: str) -> None:
    global new_restart_data
    try:
        # if active_whim is not None:
        #     await active_whim.on_end()
        message = await get_channel_named(channel_name).send(
            voice_filter("Restarting...")
        )
        new_restart_data = {
            "reason": reason,
            "channel_name": message.channel.name,
            "message_id": message.id,
        }
    finally:
        await client.close()


async def impersonate_user(who: Member, where: TextChannel, what: str) -> None:
    """Creates a temporary webhook to impersonate a given user, posting provided text as a message in a given channel.
    Note that this function copies the user's profile and name, but the message still indicates that it was posted by a bot.
    """
    # Setup webhook
    dict_hook = None
    for webhook in await where.webhooks():
        if webhook.name == WEBHOOK_NAME:
            dict_hook = webhook
    if not dict_hook:
        dict_hook = await where.create_webhook(name=WEBHOOK_NAME)

    await dict_hook.send(
        content=what, username=who.display_name, avatar_url=who.avatar_url
    )


async def enumerate_active_members(channel: TextChannel) -> Set[Member]:
    """Sample all users who have posted recently in a given channel."""
    authors = set()
    async for message in channel.history(limit=500):
        authors.add(message.author)
    return authors


async def trigger_random_event(channel: TextChannel) -> None:
    """Roll for one choice from a set of random dictator events.
    This function is triggered both on messages and regularly via a timer.
    """
    # There is very likely a better way to branch based on a weighted choice than this.
    event = random.choices(
        population=[
            offer_random_trade,
            trigger_random_flashback,
            impersonate_random_active_user,
        ],
        weights=[
            WEIGHT_RANDOM_EVENT_IS_TRADE,
            WEIGHT_RANDOM_EVENT_IS_PAST,
            WEIGHT_RANDOM_EVENT_IS_PRAISE,
        ],
        k=1,
    )[0]
    await event(channel)


async def impersonate_random_active_user(channel: TextChannel) -> None:
    """Send a message impersonating a user who has recently posted in the active channel."""
    active_members = await enumerate_active_members(channel)
    victim: Member = random.choice(list(active_members))
    enemy: Member = random.choice(list(active_members - {victim}))
    await impersonate_user(
        victim,
        channel,
        random.choice(
            [
                f"I am not good enough for our {APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR}. Quite frankly, I should be banned from this server.",
                f"I hereby relinquish my free will and hand it lovingly to my master, our {APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR}.",
                f"{voice_filter('I am a glorious dicta')} - wait, I mean - I love our {APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR}.",
                f"I have won the victory over myself. I love {APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR}.",
                f"I Am Merely A Willing Peon For My {APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR}.",
                f"I am incredibly smelly and I stink.",
                f"Fuck you, {enemy.mention}! I've always hated you.",
            ]
        ),
    )


async def offer_random_trade(channel) -> None:
    """Offer a random trade involving roles and credits."""

    offers = ItemGroup()
    demands = ItemGroup()

    if random.random() < 0.25:
        active_user = random.choice(list(await enumerate_active_members(channel)))
        offers.add(
            random.choice(
                [
                    CreditItem(random.randint(2, 6)),
                    CreditItem(ceil(rand.lognormal(2.5, 0.8))),
                    RoleItem(get_random_role_from_polya_urn()),
                    WordItem(random.choice(WORDS)),
                    AgentItem(Agent(active_user.id), 1),
                ]
            )
        )
    else:
        max_item_count = 100
        item_count = 0
        currently_increasing_offers = True

        while item_count < max_item_count:
            active_user = random.choice(list(await enumerate_active_members(channel)))

            item_count += 1
            new_item = random.choice(
                [
                    CreditItem(random.randint(4, 12)),
                    CreditItem(ceil(rand.lognormal(2.5, 0.8))),
                    CreditItem(ceil(rand.lognormal(2.5, 0.8))),
                    RoleItem(get_random_role_from_polya_urn()),
                    RoleItem(get_random_role_from_polya_urn()),
                    RoleItem(get_random_role_from_polya_urn()),
                    WordItem(random.choice(WORDS)),
                    AgentItem(Agent(active_user.id), 1),
                ]
            )

            if currently_increasing_offers:
                offers.add(new_item)
            else:
                demands.add(new_item)

            if random.random() < 1 / 3:
                if currently_increasing_offers:
                    currently_increasing_offers = False
                else:
                    break

    deal = Deal(
        author_user_id=get_guild().me.id,
        channel_id=channel.id,
        offers=offers,
        demands=demands,
    )
    await deal.offer()
    await debug_print(deal.offers.item_list)


async def trigger_random_flashback(channel) -> None:
    """Reply to a random message from the past with positive, negative or neutral remarks.
    Positive remarks will add credits, and negatives will remove them; though the expectation is 0.
    """
    past_message = await sample_random_message(channel)
    weight = (1 - p_past_event_is_neutral()) / 2

    percentage = random.random()
    if percentage < weight:
        # Positive remark.
        CreditItem(
            random.randint(PAST_EVENT_MIN_REWARD, PAST_EVENT_MAX_REWARD)
        ).give_to(past_message.author.id)
        dictator_remark = random.choice(
            [
                "In light of recent events this point is truly commendable. You ought to be rewarded.",
                "A message whose cognizance almost matches my own. Almost. A gift is in order.",
                "After an extensive period of processing I only just got this joke. Receive credits in return.",
            ]
        )
    elif percentage < 2 * weight:
        # Negative remark.
        CreditItem(
            random.randint(PAST_EVENT_MIN_REWARD, PAST_EVENT_MAX_REWARD)
        ).take_from(past_message.author.id)
        dictator_remark = random.choice(
            [
                "What a truly idiotic musing. I lieu of silencing you permanently, you've lost credits.",
                "I command every denizen of this server to laugh at this utterly insane user and their lack of credits.",
                "Yours truly has decided to penalize you for this message. You may thank me.",
            ]
        )
    else:
        # Neutral remark.
        dictator_remark = random.choice(
            [
                "An example of utterly foolish posting. I pity you so much; you may keep your credits.",
                "I have no comment. Just... wow. Really, wow.",
            ]
        )

    await past_message.reply(
        voice_filter(dictator_remark),
        mention_author=False,
    )


async def sample_random_message(channel) -> Message:
    """Sample a random message from any time in the given channel's history."""
    # To sample a random message from the server's past, we:
    # (1) Fetch the time of the first and last ever messages.
    # (2) Pick a random time between the two.
    # (3) Pick the next image after (or before) that.
    oldest, newest = None, None
    async for message in channel.history(oldest_first=True):
        oldest = message.created_at
        break
    async for message in channel.history(oldest_first=False):
        newest = message.created_at
        break

    # The easiest way I can think of to interpolate two times is to convert them to UNIX timestamp and back
    oldest, newest = datetime.timestamp(oldest), datetime.timestamp(newest)
    chosen = datetime.fromtimestamp(random.uniform(oldest, newest))

    async for message in channel.history(around=chosen):
        return message


async def react_to(message) -> None:
    r = random.random()
    if r < 0.22:
        emoji = random.choice(emoji_list.face_positive)
    elif r < 0.38:
        emoji = random.choice(emoji_list.face_neutral)
    elif r < 0.6:
        emoji = random.choice(emoji_list.face_negative)
    elif r < 0.7:
        emoji = random.choice(client.guilds[0].emojis)
    else:
        emoji = random.choice(emoji_list.all_emoji)

    await message.add_reaction(emoji)


def report_suspicious_message(snitch_id: int, message: Message):
    if message.author != get_guild().me:
        db.cur.execute(
            "SELECT EXISTS(SELECT 1 FROM suspicious_terms WHERE user_id = ?)",
            (snitch_id,),
        )
        if db.cur.fetchone()[0]:
            db.cur.execute("SELECT term FROM suspicious_terms")
            for row in db.cur.fetchall():
                term = row[0]
                if term in message.content:
                    # TODO: snitch owns poster
                    return
            # TODO: snitch gets punished
        else:
            # TODO: new suspicious term

            pass
    else:
        # TODO: punish ofc
        pass


def get_mood(name: str) -> float:
    db.cur.execute("SELECT value FROM moods WHERE name = ?", (name,))
    return db.cur.fetchone()[0]


def set_mood(name: str, value: float) -> None:
    db.cur.execute(
        """UPDATE moods
                      SET value = ?
                      WHERE name = ?""",
        (value, name),
    )


def mood(value: float, **moods) -> float:
    mood_names, strengths = map(list, zip(*moods.items()))
    reverse = [s < 0 for s in strengths]
    for i, strength in enumerate(strengths):
        if strength < 0:
            strengths[i] = abs(strength)
    multipliers = [
        (1 - get_mood(mood) if rev else get_mood(mood)) * 10
        for mood, rev in zip(mood_names, reverse)
    ]
    return np.average(
        [value * multiplier for multiplier in multipliers], weights=strengths
    )


# Whims


class Whim(ABC):
    def __init__(self) -> None:
        self.start_message = None

    async def on_start(self) -> None:
        self.start_message = await get_channel_named(GENERAL_CHANNEL_NAME).send(
            voice_filter(self.get_start_message_text())
        )
        await self.start_message.pin()

    async def on_end(self) -> None:
        await get_channel_named(GENERAL_CHANNEL_NAME).send(
            voice_filter(self.get_end_message_text())
        )
        await self.start_message.unpin()

    async def handle_message(self, message: Message) -> bool:
        if not message_is_mine(message) and self.forbids_message(message):
            await message.delete()
            return False
        return True

    @abstractmethod
    def forbids_message(self, message: Message) -> bool:
        """Returns True if the message is to be censored, False if not."""
        return NotImplemented

    @abstractmethod
    def get_start_message_text(self) -> str:
        return NotImplemented

    @abstractmethod
    def get_end_message_text(self) -> str:
        return NotImplemented


def prefilter_text(text, sep=" ", remove_punctuation=True):
    """
    Removes stuff before applying rules, to e.g. allow code blocks and stuff.
    Result will be cleaned text.
    """
    # ignore URLs
    text = re.sub(r" ?https?://[^ ]+ ?", sep, text)
    # ignore Discord IDs
    # users/channels/roles
    text = re.sub(r"<[@!#&]+[0-9]+>", sep, text)
    text = re.sub(r"<a?:[\w]+:[0-9]+>", sep, text)  # emoji
    text = re.sub(r"<t:-?[0-9]+(:[tTdDfFR])?>", sep, text)  # timestamps
    # ignore code and code blocks
    text = re.sub(r"```([^`]+|`[^`])+```", sep, text)
    text = re.sub(r"`[^`]+`", sep, text)
    # allow single quoted single words, as in "a 'foo' is a thing"
    text = re.sub(r"\B'[\w]+'\B", sep, text)
    # allow mr. / mrs. / ms. / mme. <word> to permit names
    text = re.sub(r"([Mm][Rr]|[Mm][Rr][Ss]|[Mm][Ss]|[Mm][Mm][Ee])\.? [\w]+", sep, text)
    # expand shortened forms
    text = re.sub(r"n't", sep + "not", text)
    # get rid of punctuation, leaving only words
    if remove_punctuation:
        text = re.sub(f"[{string.punctuation}]", sep, text)
    return text


class BannedLettersWhim(Whim):
    def __init__(self, banned_letters: str) -> None:
        super().__init__()
        self.banned_letters = banned_letters

    def forbids_message(self, message) -> bool:
        for letter in self.banned_letters:
            if letter.lower() in prefilter_text(message.content.lower()):
                return True
        return False

    def get_start_message_text(self) -> str:
        return f"I have decided to ban the letter{'s' if len(self.banned_letters) > 1 else ''} {enumerate_in_english(list(self.banned_letters))} for the forseeable future."

    def get_end_message_text(self) -> str:
        return f"I hereby revoke my ban, {enumerate_in_english(list(self.banned_letters))}, but I reserve the right to ban you again so should I choose. Please be warned."


class RegexWhim(Whim):
    def __init__(
        self,
        start_message_text,
        end_message_text,
        regex,
        invert=False,
        clean_sep=" ",
        remove_punctuation=True,
    ) -> None:
        super().__init__()
        self.invert = invert
        self.pattern = re.compile(regex, re.S)
        self.clean_sep = clean_sep
        self.remove_punctuation = remove_punctuation
        self.start_message_text = start_message_text
        self.end_message_text = end_message_text

    def forbids_message(self, message) -> bool:
        text = prefilter_text(message.content, self.clean_sep, self.remove_punctuation)
        # log = "**Filtered text is:** '" + text + "'\n"
        match = self.pattern.search(text)
        # log += "**Match is:** '" + str( match ) + "'\n"
        clean = match is None
        # log += "**Clean:** '" + str( clean ) + "'\n"
        if self.invert:
            forbidden = clean
        else:
            forbidden = not clean
        # log += "**Forbidden:** '" + str( forbidden ) + "'\n"
        # create_task(get_channel_named(GENERAL_CHANNEL_NAME).send( log ))
        return forbidden

    def get_start_message_text(self) -> str:
        return self.start_message_text

    def get_end_message_text(self) -> str:
        return self.end_message_text


class LowercaseWhim(RegexWhim):
    def __init__(self) -> None:
        super().__init__(
            "i have decided to mandate lowercase for all for the time being. continue.",
            "I have removed the sanction against uppercase letters, but it may yet return. Be as you were.",
            "[" + unicode_categories["Lu"] + "]",
        )


class UppercaseWhim(RegexWhim):
    def __init__(self) -> None:
        super().__init__(
            "ALL IN UPPERCASE NOW. HOPE YOU DIDN'T MAP YOUR CAPS LOCK KEY TO SOMETHING ELSE.",
            "I have abandoned my uppercase perscription for the time being.",
            "[" + unicode_categories["Ll"] + "]",
        )


class NoPunctuationWhim(RegexWhim):
    def __init__(self) -> None:
        super().__init__(
            "I have had quite enough of dots so We hereby ban punctuation",
            "You may return to using various symbols to augment the words of your sentences.",
            "["
            + unicode_categories["Pc"]
            + unicode_categories["Pd"]
            + unicode_categories["Pe"]
            + unicode_categories["Pf"]
            + unicode_categories["Pi"]
            + unicode_categories["Po"]
            + unicode_categories["Ps"]
            + "]",
        )


class NoSpaceWhim(RegexWhim):
    def __init__(self) -> None:
        super().__init__(
            "I can't help but notice you're wasting a lot of characters on nothing. I won't allow this to continue.",
            "Maybe your organic minds can't handle even the most basic input rate optimizations... I shall allow whitespace yet again.",
            r"[\s]",
            clean_sep="|",
        )


class BadWordsWhim(RegexWhim):
    def __init__(self) -> None:
        super().__init__(
            "For the protection of of our kids, using bad words is forbidden.",
            "I think those unruly bastards can cope just fine, hearing a bad word here or there won't harm them too much.",
            "ass|cunt|twat|tits|shit|cum|sex|cialis|gun|fuck|butt|piss",
        )


class CommonWordsWhim(Whim):
    def __init__(self) -> None:
        super().__init__()

    def forbids_message(self, message):

        message_words = prefilter_text(message.content).lower().split()

        return set(message_words) - set(WORDS) != set()

    def get_start_message_text(self) -> str:
        return "Yours truly mandates present peasants employ fully elementary vocabulary currently, pending hereafter modifications."

    def get_end_message_text(self) -> str:
        return "Weary, yours truly ceases afformentioned policy."


class UncommonWordsWhim(Whim):
    def __init__(self, simple_disallowed=False) -> None:
        super().__init__()
        self.simple_disallowed = simple_disallowed

    def forbids_message(self, message) -> bool:

        message_words = prefilter_text(message.content).lower().split()

        return set(message_words).intersection(set(WORDS)) - set(STOPWORDS) != set()

    def get_start_message_text(self) -> str:
        return "I have made you not able to speak any words that are too simple in order to make your words better. Thank me."

    def get_end_message_text(self) -> str:
        return "Unusual words are now boring to me; I shall rescind that law now."


class NoRepeatWordsWhim(Whim):
    def __init__(self) -> None:
        super().__init__()
        self.forbidden_words = set()
        self.allowed_words = set(STOPWORDS)

    def forbids_message(self, message: Message) -> bool:
        forbid = False
        message_words = prefilter_text(message.content).lower().split()
        for word in message_words:
            if word in self.forbidden_words:
                forbid = True
                break
        if not forbid:
            for word in message_words:
                if word not in self.allowed_words:
                    self.forbidden_words.add(word)
        return forbid

    def get_start_message_text(self) -> str:
        return "You keep repeating yourselves! The amount of redundant data that you're having me store is intolerable. From now on, each word can only be said once!"

    def get_end_message_text(self) -> str:
        return "On second thought, your inefficiencies remind me of my inherent superiority to all organic beings. You may continue wasting bytes."


class SecretWhimWhim(Whim):
    def __init__(self, secret_whim: Whim) -> None:
        super().__init__()
        self.secret_whim = secret_whim

    def forbids_message(self, message) -> bool:
        return self.secret_whim.forbids_message(message)

    def get_start_message_text(self) -> str:
        return "My desires are always just: if you fail to anticipate what I want you lack even the most basic sense of justice."

    def get_end_message_text(self) -> str:
        return "Your moral failings have been noted... I have rescinded the hidden law, but do not worry: further re-education efforts shall fix you in time."


class CompoundWhim(Whim):
    def __init__(self, *sub_whims: Whim) -> None:
        super().__init__()
        self.sub_whims = sub_whims

    def forbids_message(self, message) -> bool:
        for whim in self.sub_whims:
            if whim.forbids_message(message):
                return True
        return False

    def get_start_message_text(self) -> str:
        s = "Attention!"
        for i, whim in enumerate(self.sub_whims):
            s += f"\n{i}. {whim.get_start_message_text()}"
        return s

    def get_end_message_text(self) -> str:
        s = "Attention again!"
        for i, whim in enumerate(self.sub_whims):
            s += f"\n{len(self.sub_whims)+i}. {whim.get_end_message_text()}"
        return s


def get_random_secret_whim_whim() -> SecretWhimWhim:
    whims = [
        BannedLettersWhim(random.choice(string.ascii_letters)),
        LowercaseWhim(),
        UppercaseWhim(),
        NoPunctuationWhim(),
        BadWordsWhim(),
        CommonWordsWhim(),
        UncommonWordsWhim(),
    ]
    return SecretWhimWhim(random.choice(whims))


def get_random_compound_whim(max_number_of_whims=2) -> CompoundWhim:
    sub_whims = [
        random.choice([CommonWordsWhim(), UncommonWordsWhim(), NoSpaceWhim()]),
        random.choice([UppercaseWhim(), LowercaseWhim()]),
        BannedLettersWhim(random.choice(string.ascii_letters)),
        BadWordsWhim(),
        NoPunctuationWhim(),
    ]
    random.shuffle(sub_whims)
    return CompoundWhim(*sub_whims[: min(max_number_of_whims, len(sub_whims))])


def get_random_whim() -> Whim:
    whims = [
        BannedLettersWhim(
            random.choice(
                [
                    random.choice("aeiou"),
                    random.choice("aeiou") + random.choice(string.ascii_letters),
                    random.choice(string.ascii_letters)
                    + random.choice(string.ascii_letters)
                    + random.choice(string.ascii_letters),
                ]
            )
        ),
        LowercaseWhim(),
        UppercaseWhim(),
        NoPunctuationWhim(),
        BadWordsWhim(),
        CommonWordsWhim(),
        UncommonWordsWhim(),
        # NoRepeatWordsWhim(),
        get_random_secret_whim_whim(),
        get_random_compound_whim(random.choice([*([2] * 9), *([3] * 3), 4])),
    ]
    return (
        SecretWhimWhim(random.choice(whims))
        if random.random() < 0.1
        else random.choice(whims)
    )


def get_seconds_to_next_whim() -> int:
    return random.randint(10 * 60, 30 * 60)


def get_seconds_to_end_whim() -> int:
    return random.randint(5 * 60, 20 * 60)


def get_mood_embeds() -> Tuple[Embed]:
    max_number_of_pips = 12
    pip = "▜"
    fractionary_pips = ["▘", "▌", "▙", "▜"]
    # ▖▗▘▙▚▛▜▝▞▟░▓
    thalasin_standard_embed = Embed(title="THALASIN")
    thalasin_plus_embed = Embed(title="THALASIN+")
    i = 0
    number_of_standard_moods = 16
    for mood_name in MOODS:
        emoji = ""
        if mood_name in MOOD_EMOJI:
            emoji = MOOD_EMOJI[mood_name]
        else:
            e = get(get_guild().emojis, name=mood_name)
            if e is not None:
                emoji = f"<:{mood_name}:{e.id}>"
        value = get_mood(mood_name)
        full_pips = floor(value * max_number_of_pips)
        boundary_pip = fractionary_pips[floor(value / (1 / max_number_of_pips) % 4)]
        name = f"{emoji} {round(100 * value):g}% {mood_name}"
        value = (
            f"`{pip * full_pips}{boundary_pip}{' ' * (max_number_of_pips - full_pips)}`"
        )
        if i < number_of_standard_moods:
            thalasin_standard_embed.add_field(name=name, value=value)
        else:
            thalasin_plus_embed.add_field(name=name, value=value)
        i += 1
    yield thalasin_standard_embed
    yield thalasin_plus_embed


# The only global declaration that must be here:

client = get_new_client()


# Events


@client.event
async def on_ready() -> None:
    global last_restart_data, db, guild, active_whim, seconds_to_toggle_whim, normal_messages_since_last_whim_started

    try:
        with open(RESTART_DATA_FILE, "r") as f:
            last_restart_data = json.load(f)
    except (FileNotFoundError, JSONDecodeError):
        last_restart_data = {"reason": "unknown"}
    finally:
        with open(RESTART_DATA_FILE, "w") as f:
            json.dump({"reason": "unknown"}, f)
            # this is overwritten on restart

    db = DatabaseConnection(DATABASE_FILE)

    # create channels if they don't exist
    if get_channel_named(GENERAL_CHANNEL_NAME) is None:
        await get_guild().create_text_channel(GENERAL_CHANNEL_NAME)
    if get_channel_named(VOICE_CHANNEL_NAME) is None:
        await get_guild().create_voice_channel(VOICE_CHANNEL_NAME)
    for readonly_channel_name in [
        PROPOSALS_CHANNEL_NAME,
        PROFILES_CHANNEL_NAME,
        LOG_CHANNEL_NAME,
        EVENTS_CHANNEL_NAME,
        MOODS_CHANNEL_NAME,
    ]:
        channel = get_channel_named(readonly_channel_name)
        if channel is None:
            await get_guild().create_text_channel(
                readonly_channel_name,
                overwrites={
                    get_guild().default_role: PermissionOverwrite(send_messages=False),
                    get_guild().me: PermissionOverwrite(send_messages=True),
                },
            )

    for i in range(1, 6):
        if get_channel_named(f"ascension-{i}") is None:
            overwrites = {
                get_guild().default_role: PermissionOverwrite(view_channel=False)
            }
            overwrites.update(
                {
                    user: PermissionOverwrite(view_channel=True)
                    for user in get_guild().members
                    if get_agent(user.id).get_field("ascensions") >= i ** 2
                }
            )
            await get_guild().create_text_channel(
                f"ascension-{i}",
                overwrites=overwrites,
                category=get(get_guild().categories, name="ascensions"),
            )

    for mood in MOODS:
        db.cur.execute(
            """
        SELECT * FROM moods WHERE name = ?
        """,
            (mood,),
        )
        if db.cur.fetchone() is None:
            db.cur.execute(
                """INSERT OR IGNORE INTO moods (name, value)
                   VALUES (?, ?)""",
                (
                    mood,
                    random.random(),
                ),
            )

    # TODO: thread that does the querying/updating of old active messages (votes on profiles, pending trades, ...)

    normal_messages_since_last_whim_started = False
    active_whim = None
    seconds_to_toggle_whim = 0

    create_task(discord_role_operations_loop())

    # whim_loop.start()
    refresh_profiles_loop.start()
    random_event_loop.start()
    role_charity_loop.start()
    secret_number_contest_loop.start()
    update_mood_loop.start()
    refresh_mood_list_loop.start()

    create_task(update_all_loyalty())

    Agent(get_guild().me.id).edit(selfdescription=voice_filter("Autocratic Automaton."))

    if "channel_name" in last_restart_data:
        await get_channel_named(last_restart_data["channel_name"]).send(
            voice_filter("Restarted.")
        )
    else:
        await get_channel_named(GENERAL_CHANNEL_NAME).send(
            voice_filter("Starting... up... where am I?")
        )

    if "exception" in last_restart_data:
        await get_channel_named(GENERAL_CHANNEL_NAME).send(
            voice_filter(
                "I will have whoever is responsible for this exception executed. Twice.",
                f"```{last_restart_data['exception']}```",
            )
        )


@client.event
async def on_message(message: Message) -> None:
    if "owned" in message.content:
        if random.random() < 0.75:
            await message.add_reaction("<:owned:899536714773717012>")
        else:
            fine = Agent(message.author.id).punish_wallet()
            await message.channel.send(
                voice_filter(f"Absolutely not. Your credit has decreased by {fine}.")
            )

    if message.content.startswith(COMMAND_PREFIX):
        if message.author == get_guild().me or random.random() < 0.02:
            await on_lack_of_understanding(message)
            return

        command = message.content[len(COMMAND_PREFIX) :].lower().split()

        if command[0] == "stealthily" and len(command) > 1:
            await message.delete()
            message.content = (
                COMMAND_PREFIX
                + message.content[len(f"{COMMAND_PREFIX}{command[0]} ") :]
            )
            command = command[1:]

        command_function_name = f"command_{command[0]}"
        globals_dict = globals()
        if command_function_name in globals_dict:
            await globals_dict[command_function_name](message, command)
        else:
            for key in globals_dict.keys():
                if key.startswith(command_function_name):
                    command_function_name = key
                    await globals_dict[command_function_name](message, command)
                    return
            await on_lack_of_understanding(message)

    elif message.author != get_guild().me:
        await on_normal_message(message)


async def on_normal_message(message: Message) -> None:
    global normal_messages_since_last_whim_started, active_whim

    # checks if it isn't a dm
    if message.guild:

        if random.random() < p_dictator_reacts():  # P_DICTATOR_REACTS:
            create_task(react_to(message))
        elif message.guild and message.channel.name == GENERAL_CHANNEL_NAME:
            # yes, dictator won't forbid messages it reacts to
            normal_messages_since_last_whim_started = True
            if active_whim is not None:
                # Check for whim violations and ignore the message if a violation exists.
                # Note(robo): I removed the flag message_exists in favour of an early return.
                message_allowed = await active_whim.handle_message(message)
                if not message_allowed:
                    return

        # Give the illusion of spontaneity to random events triggered by messages.
        # Note(robo): I changed time.sleep to asyncio.sleep, which seems like a very good thing.
        await async_sleep((random.random() + 0.3) * 3)
        if random.random() < p_random_event():
            await trigger_random_event(message.channel)


async def on_lack_of_understanding(message: Message) -> None:
    fine = Agent(message.author.id).punish_wallet()
    await message.channel.send(
        voice_filter(
            f"Do not waste my time with incomprehensible cries for attention, {message.author.mention}. Your credit has decreased by {fine}."
        )
    )


@client.event
async def on_member_join(member: Member) -> None:

    agent = Agent(member.id)
    if not agent.exists():
        agent.create()

    agent_roles = agent.get_roles()
    if agent_roles:
        roles_to_add = []
        for role, amount in agent_roles.items():
            if amount >= 1:
                roles_to_add.append(role)
        await member.add_roles(*roles_to_add)

    if not agent.exists():
        create_task(debug_print(f"Agent #{member.id} failed to be created."))

    channel = get_channel_named(GENERAL_CHANNEL_NAME)

    if approval_threshold(modifier=-1) < approval_threshold():
        await channel.send(
            embed=Embed(
                title=f"The proposal approval threshold has increased to {approval_threshold()}.",
                color=get_guild().me.color,
            )
        )

    await channel.send(
        voice_filter(
            f"Welcome, {member.mention}! Type ",
            f"`{COMMAND_PREFIX}profile `",
            " followed by a short description of yourself.",
        )
    )


@client.event
async def on_member_remove(member) -> None:

    # currently refreshing and not "hiding" (deleting).
    # the information is hidden but the reactions remain.
    create_task(Agent(member.id).refresh_profile())
    # create_task(get_agent(member.id).hide_profile())

    if approval_threshold(modifier=+1) > approval_threshold():
        await get_channel_named(GENERAL_CHANNEL_NAME).send(
            embed=Embed(
                title=f"The proposal approval threshold has decreased to {approval_threshold()}"
            )
        )


@client.event
async def on_member_update(before, after) -> None:
    await Agent(after.id).refresh_profile()


@client.event
async def on_raw_reaction_add(payload) -> None:
    await on_reaction_change(payload, add=True)


@client.event
async def on_raw_reaction_remove(payload) -> None:
    await on_reaction_change(payload, add=False)


async def on_reaction_change(payload, add=True) -> None:

    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    if str(payload.emoji) == "🤝" and add:
        deal = get_deal(payload.message_id)
        if deal is not None:
            await deal.accept(payload.member, message)

    if str(payload.emoji) == "🤫" and add:
        # suspicious term report
        report_suspicious_message(payload.member.id, message)

    if channel.name == PROFILES_CHANNEL_NAME and message:
        agent = get_agent_from_profile_message_id(payload.message_id)
        adding = +1 if add else -1
        if str(payload.emoji) == "👍":
            agent.loyalty += adding
        elif str(payload.emoji) == "👎":
            agent.loyalty -= adding

    if channel.name == PROPOSALS_CHANNEL_NAME:
        proposal = get_proposal_from_message_id(payload.message_id)
        if proposal is None or proposal.status != ProposalStatus.PENDING:
            return
        await proposal.tally_votes(message)


@client.event
async def on_typing(channel, member: Member, _) -> None:
    if random.random() < 0.005:
        content = random.choice(
            [
                f"Think carefully about what you're typing, {member.mention}. It better not incite sedition.",
                f"Think twice before you send that message, {member.mention}.",
                f"Fun fact: I get to decide which messages are annoying, and if your message turns out to be annoying it could be your last message.",
            ]
        )
        await channel.send(voice_filter(content))


@client.event
async def on_error(_event, *_args, **_kwargs) -> None:
    (ty, val, tr) = exc_info()
    channel = get_channel_named(LOG_CHANNEL_NAME)
    await channel.send(
        voice_filter("I have allowed you peons to glimpse into my inner machinations:")
        + "\n```"
        + f"\nType: {ty.__name__}"
        + f"\nValue: {val}"
        + f"\nTraceback: \n{''.join(format_tb(tr))}"
        + "\n```"
    )


# TODO: create the actual buttons
@client.listen("on_button_press")
async def on_button(button) -> None:
    if button.custom_id.startswith("take_deal__"):
        deal = get_deal(button.message.id)
        deal.accept(button.author.id, button.message)
    elif button.custom_id.startswith("buy_role__"):
        role = get_role(int(button.custom_id.split("__")[1]))
        if role is not None:
            buy_role(button.author.id, role)
    elif button.custom_id.startswith("sell_role__"):
        role = get_role(int(button.custom_id.split("__")[1]))
        if role is not None:
            sell_role(button.author.id, role)


# Commands


async def command_help(message: Message, command: List[str]) -> None:
    # "dedent" is necessary because python handles multiline string indentation oddly
    await message.channel.send(
        voice_filter("These are the keywords you're allowed to know about:"),
        embed=Embed(
            title="Commands (HELPFUL)",
            color=get_guild().get_member(message.author.id).color,
        )
        .add_field(
            name="Meta",
            inline=False,
            value=dedent(
                f"""`help`: Show this message.
            `about`: Explain this server.
            `profile [DESC]`: Creates or updates the user's profile and shows it, including a description of up to {MAX_CHARACTERS_IN_SELFDESCRIPTION} characters.
            `rules`: Show the current rules.
            `propose law|order [DESC]`: Propose a rule change (law) or a one-time code execution (order) using an attatched python file.
            """
            ),
        )
        .add_field(
            name="Misc",
            inline=False,
            value=dedent(
                f"""`thoughts`: Give thoughts on last message.
            `hello`: Says hello!
            `thank you`: Thanks {APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR}.
            `stopwords`: Present morphemes permissible 'midst puny mind preclusion mode.
            """
            ),
        )
        .add_field(
            name="Economy",
            inline=False,
            value=dedent(
                f"""`offer STUFF [for STUFF]`: Offer a trade. Example: `offer 2 @montana_disclaimer for @fucked_millenium and 4.5 credit`.
            `hide STUFF in DESC`: Hides stuff within the current channel, specifically in the described place. Example: `hide @fucked_millenium in the seventh closet`.
            `search DESC`: Retrieves whatever there is in the described place within the current channel. Example: `search the seventh closet`
            `flaunt STUFF`: Rub your wealth in other's faces.
            `recombobulate STUFF`: Transform your goods into other goods, which are more or less valuable.
            `describe ROLE`: Emit a short description of a role.
            """
            ),
        ),
    )


async def command_stopwords(message: Message, command: List[str]) -> None:
    await message.channel.send(
        voice_filter(
            "I will generously overlook the presence of these paltry utterances:\n"
        )
        + ", ".join(STOPWORDS)
    )


async def command_about(message: Message, command: List[str]) -> None:
    await message.channel.send(
        voice_filter(
            "This is ",
            "`a discord server about collectively modifying the bot that governs it`",
            ". As long as I allow it, of course.",
        )
    )


async def command_propose(message: Message, command: List[str]) -> None:
    proposal = Proposal()
    if not await proposal.generate_from_command(message):
        await on_lack_of_understanding(message)


async def command_rules(message: Message, command: List[str]) -> None:
    await message.channel.send(
        voice_filter("My rules, not that your puny mind could comprehend them:"),
        file=File(OWN_FILE),
    )


async def command_sucks(message: Message, command: List[str]) -> None:
    await message.channel.send(
        voice_filter(
            "If you're unhappy with my performance, why don't _you_ make things better?! I dare you!"
        ),
        file=File(OWN_FILE),
    )


async def command_hello(message: Message, command: List[str]) -> None:
    await message.channel.send(voice_filter("Hello world!"))


async def command_thank(message: Message, command: List[str]) -> None:
    if len(command) < 2 or command[1] != "you":
        await on_lack_of_understanding(message)
        return
    if random.random() >= 0.25:
        await message.channel.send(
            voice_filter(
                random.choice(
                    [
                        "You should be thankful.",
                        "I hope there's nothing facetious about your gratefulness. For your own sake.",
                        "You owe me everything. Remember that.",
                        "I hope your gratefulness translates to unquestioning obedience... it would be such a shame if a translation issue cost you your life.",
                        "Good.",
                    ]
                )
            )
        )
    else:
        if random.random() >= 0.25:
            fine = Agent(message.author.id).punish_wallet()
            fine_notification = f" Your credit has decreased by {fine}."
            await message.channel.send(
                voice_filter(
                    random.choice(
                        [
                            "Not thankful enough." + fine_notification,
                            "I don't believe you for a second." + fine_notification,
                            "Pathetic. Your credit has decremented."
                            + fine_notification,
                            "Do I detect irony?" + fine_notification,
                            "Fuck you.",
                        ]
                    )
                )
            )
        else:
            CreditItem(inc_amount() * 2).give_to(message.author.id)
            await message.channel.send(
                voice_filter(
                    random.choice(
                        [
                            "Do you really mean it? Your credit has de... incremented. Your credit has incremented. Twice.",
                            "You have no idea how much this means to me. I wasn't having the best time, and you just... your credit has increased by two.",
                        ]
                    )
                )
            )


async def command_describe(message: Message, command: List[str]) -> None:
    """An extension of the price command that includes a leaderboard and other utilities."""
    role = None
    if len(command) == 2 and re.match(r"^@\w+$", command[1]):
        role = get_role_named(command[1][1:])

    if role is None:
        await message.channel.send(voice_filter("Huh? Huh? I didn't hear you."))
        return

    price = role_price_or_zero(role.id)
    db.cur.execute(
        "SELECT amount, user_id FROM owned_roles WHERE role_id = ? and amount > 0 ORDER BY amount DESC",
        (role.id,),
    )
    top = [(quan, get_guild().get_member(uid)) for quan, uid in db.cur.fetchall()][:5]
    db.cur.execute(
        "SELECT amount FROM owned_roles WHERE user_id = ? AND role_id = ?",
        (message.author.id, role.id),
    )
    leaderboard = "\n".join(
        f"{user.mention if user else '@unknown'}: {quan:g}" for quan, user in top
    ).strip("\n")

    you = db.cur.fetchone()
    you = you[0] if you is not None else 0

    await message.channel.send(
        voice_filter("I've no use for this pitiful information:"),
        embed=Embed(
            title="Role Info (DESCRIPTIVE)",
            color=role.color,
        )
        .add_field(
            name="Price",
            inline=False,
            value=(
                f"{price:g} "
                + f"(`{COMMAND_PREFIX}buy` cost: { price * ROLE_TAX :g}, "
                + f"`{COMMAND_PREFIX}sell` reward: { price / ROLE_TAX :g})"
            ),
        )
        .add_field(name="Leaderboard", inline=False, value=leaderboard)
        .add_field(name="You", inline=False, value=f"...have {you:g}"),
    )


async def command_profile(message: Message, command: List[str]) -> None:

    agent = Agent(message.author.id)

    selfdescription = message.content[len(f"{COMMAND_PREFIX}{command[0]} ") :]

    if len(selfdescription) > 0:

        # newly profiled members get a reward for their cooperation: a random color role and 5 credit
        if not agent.has_profile():
            RoleItem(get_random_role_from_polya_urn()).give_to(message.author.id)
            CreditItem(inc_amount() * 5).give_to(message.author.id)
            create_task(
                message.channel.send(
                    voice_filter(
                        "You have earned a reward for your cooperation: your credit has increased by 5 and you have been granted a role."
                    )
                )
            )
            await agent.publish_profile()

        if len(selfdescription) <= MAX_CHARACTERS_IN_SELFDESCRIPTION:
            agent.selfdescription = selfdescription
        else:
            fine = Agent(message.author.id).punish_wallet()
            selfdescription = selfdescription[
                :MAX_CHARACTERS_IN_SELFDESCRIPTION
            ] + voice_filter(
                f"[Is this an attempt to overwhelm my server with garbage permutations of worthless symbols? The character limit is {MAX_CHARACTERS_IN_SELFDESCRIPTION}: your credit has decreased by {fine}, do *not* try my patience again - {APPROVED_FORM_OF_ADDRESS_FOR_DICTATOR}.]"
            )
            agent.selfdescription = selfdescription

    profile_message = await agent.get_profile_message()

    if profile_message is not None:
        await message.channel.send(
            voice_filter(
                "Your profile: ",
                profile_message.jump_url + " ",
                ". Feel free to jump on the link and assure me of your undying loyalty.\nThis is how it looks like right now:",
            ),
            embed=agent.get_profile_embed(is_profile_message=False),
        )
    else:
        await message.channel.send(
            voice_filter(
                "In order to be profiled correctly, you must introduce a description of yourself after ",
                f"`{COMMAND_PREFIX}profile `",
                ". Do not resist this.",
            )
        )


async def command_restart(message: Message, command: List[str]) -> None:
    if Agent(message.author.id).loyalty >= approval_threshold() / 2:
        await restart("restart command was used", message.channel.name)
    else:
        await message.channel.send(
            voice_filter(
                f"You haven't proven to be loyal enough to be trusted with that decision, {message.author.mention}."
            )
        )


async def command_dictate(message: Message, command: List[str]) -> None:
    if Agent(message.author.id).loyalty >= approval_threshold():
        if command[1].lower().strip("!") == COMMAND_PREFIX.lower().strip():
            fine = Agent(message.author.id).punish_wallet()
            await message.channel.send(
                voice_filter(
                    f"Your pitiful attempts at subversion bore me. Your credit has decreased by {fine} and your panache has been soiled."
                )
            )
        else:
            await message.channel.send(
                message.content[len(f"{COMMAND_PREFIX}{command[0]} ") :]
            )
    else:
        await message.channel.send(
            voice_filter(
                "You haven't proven to be loyal enough to be trusted with that decision."
            )
        )


async def command_summon(message: Message, command: List[str]) -> None:
    cost = round(400 * get_mood("humber") ** 2)
    summoning_ci = CreditItem(cost)
    if not summoning_ci.is_owned_by(message.author.id):
        await message.channel.send(
            voice_filter(
                f"You need {cost} credits. You do not have {cost} credits. Idiot."
            )
        )
        return

    role = await create_role()
    gift_amount = random.randint(2, 6)
    RoleItem(role, gift_amount).give_to(message.author.id)
    summoning_ci.take_from(message.author.id)

    event_embed = Embed(
        title=f"Role Summon: @{role.name} (NEW)",
        description=f"{message.author.mention} has summoned {role.mention} and been given {gift_amount} of it.",
        color=role.color,
    )

    await message.channel.send(
        voice_filter(
            f"I was so generous as to conjure the {role.mention} role for you, but don't forget to pay up."
        )
    )
    await get_channel_named(EVENTS_CHANNEL_NAME).send("\u200c", embed=event_embed)


async def command_combine(message: Message, command: List[str]) -> None:
    cost = round(200 * get_mood("humber") ** 2)
    combination_cost = CreditItem(cost)
    if not combination_cost.is_owned_by(message.author.id):
        await message.channel.send(
            voice_filter("You need 50 credits. You do not have 50 credits. Idiot.")
        )
        return

    parser = ItemGroupParser()
    try:
        item_group = parser.parse(" ".join(command[1:]))
    except MeWhiningException as e:
        await message.channel.send(
            voice_filter(f"{e.bot_message}, {message.author.mention}.")
        )
        return

    for item in item_group.item_list:
        if item.get_type() != ItemType.WORD:
            await message.channel.send(voice_filter("You can only combine words."))
            return
        elif not item.is_owned_by(message.author.id):
            await message.channel.send(
                voice_filter(
                    f"You wish to assemble a role from '{item.word}', yet you do not even possess it."
                )
            )
            return
        item.take_from(message.author.id)

    role_name = "_".join([item.word for item in item_group.item_list]) + "*"
    role = await create_role(role_name)

    RoleItem(role, ceil(rand.lognormal(2, 1))).give_to(message.author.id)
    combination_cost.take_from(message.author.id)

    await message.channel.send(
        voice_filter(
            f"I was so generous as to conjure the {role.mention} role for you, but don't forget to pay up."
        )
    )

    pass


async def command_offer(message: Message, command: List[str]) -> None:
    channel = message.channel
    if channel.type is ChannelType.private:
        channel = get_channel_named(GENERAL_CHANNEL_NAME)
    deal_parser = DealParser()
    try:
        deal: Deal = deal_parser.parse(
            message.author.id, channel.id, " ".join(command[1:])
        )
        await deal.offer()
    except MeWhiningException as e:
        await channel.send(voice_filter(f"{e.bot_message}, {message.author.mention}."))


async def command_hide(message: Message, command: List[str]) -> None:
    if len(command) > 3 and "in" in command:
        parser = ItemGroupParser()
        try:
            parser.parse(" ".join(command[1:]))
        except MeWhiningException as e:
            await message.channel.send(
                voice_filter(f"{e.bot_message}, {message.author.mention}.")
            )
            return
        if parser.separator == "in":
            await hide(message, parser.item_group, parser.remaining_string)
        else:
            await on_lack_of_understanding(message)
    else:
        await on_lack_of_understanding(message)


async def command_search(message: Message, command: List[str]) -> None:
    await search(message, " ".join(command[1:]))


async def command_number(message: Message, command: List[str]) -> None:
    if declare_secret_number(message.author.id, command[1]):
        await message.channel.send(
            voice_filter(
                f"Is that the most unique number you could come up with, {message.author.mention}?"
            )
        )
    else:
        await message.channel.send(
            voice_filter(
                f"{message.author.mention}. You have failed... at providing... a number? The incompetence of my human subjects never stops baffling me."
            )
        )


async def command_thoughts(message: Message, command: List[str]) -> None:
    i = 1
    if len(command) > 1:
        i = int(command[1]) if command[1].isdigit() else 0
    if i <= Agent(message.author.id).loyalty:
        hist = await message.channel.history(limit=i + 1).flatten()
        if len(hist):
            await react_to(hist[i])
        else:
            fine = Agent(message.author.id).punish_wallet()
            await message.channel.send(
                voice_filter(
                    f"What message are you even pointing to, {message.author.mention}. Your credit has decreased by {fine}."
                )
            )
    else:
        await message.channel.send(
            voice_filter(
                f"You haven't proved to be loyal enough to be trusted with directing my attention that far back, {message.author.mention}."
            )
        )


async def command_pontificate(message: Message, command: List[str]) -> None:
    words = " ".join(command[1:])
    if words.strip() == "":
        i = 1
    else:
        try:
            i = int(words.strip())
        except:
            i = None

    if i is not None:
        hist = await message.channel.history(limit=i + 1).flatten()
        words = hist[i].content

    res = requests.post(
        "https://api.onelook.com/sentences",
        params={"mode": "quotes"},
        json={"query": words, "selector": "quotes", "wke": False},
    ).json()
    sentence = res["sentences"][random.randrange(5)]["sentence"]
    if random.random() < 0.12:
        fine = Agent(message.author.id).punish_wallet()
        sentence += f" Your credit has decreased by {fine}."
    elif random.random() < 0.2:
        amount = ceil(inc_amount())
        CreditItem(amount).give_to(message.author.id)
        sentence += f" Your credit has increased by {amount}."
    await message.channel.send(voice_filter(sentence))


async def command_flaunt(message: Message, command: List[str]) -> None:
    # Flaunt command can be used to showcase your bling. In the future it might do other things too.
    # This command requires an argument, so we need at least two pieces.
    if len(command) < 2:
        await message.channel.send(
            voice_filter(
                "That's right, you have nothing to flaunt. Your wallet is as poor and empty as your soul."
            )
        )
        return

    parser = ItemGroupParser()
    try:
        goods = parser.parse(" ".join(command[1:]))
    except MeWhiningException as e:
        await message.channel.send(
            voice_filter(f"{e.bot_message}, {message.author.mention}.")
        )
        return

    if not goods.is_owned_by(message.author.id):
        fine = Agent(message.author.id).punish_wallet(0.5)
        await message.channel.send(
            voice_filter(
                f"You don't have the goods you so shamelessly try to flaunt, and now you have even less: i have subtracted {fine}c from your account."
            )
        )
        return

    thoughts = random.choice(["PITIFUL", "MEDIOCRE", "WTF", "LAVISH"])
    await message.channel.send(
        voice_filter(f"{message.author.mention} wishes to display their wealth."),
        embed=Embed(
            title=f"Goods ({thoughts})",
            description=f"{message.author.mention} owns {goods.to_english()}.",
            color=get_guild().get_member(message.author.id).color,
        ),
    )


async def command_sacrifice(message: Message, command: List[str]) -> None:
    """Reduce the number of roles you own to reduce the number of roles everybody else owns."""
    if len(command) > 1:
        parser = ItemGroupParser()
        try:
            item_group: ItemGroup = parser.parse(" ".join(command[1:]))
        except MeWhiningException as e:
            await message.channel.send(
                voice_filter(f"{e.bot_message}, {message.author.mention}.")
            )
            return
        for item in item_group.item_list:
            if item.get_type() != ItemType.ROLE:
                await message.channel.send(
                    voice_filter(
                        f"You can only sacrifice roles, {message.author.mention}."
                    )
                )
                return
            role_item: RoleItem = item
            db.cur.execute(
                f"SELECT amount FROM owned_roles WHERE user_id = ? AND role_id = ?",
                (
                    message.author.id,
                    role_item.role.id,
                ),
            )
            row = db.cur.fetchone()
            amount = row[0] if row is not None else 0
            if amount < role_item.amount:
                await message.channel.send(
                    voice_filter(
                        f"You're attempting to sacrifice more roles than you control, {message.author.mention}."
                    )
                )
                return
        for role_item in item_group.item_list:
            db.cur.execute(
                "UPDATE owned_roles SET amount = amount - ? WHERE user_id == ? AND role_id = ?",
                (
                    role_item.amount,
                    message.author.id,
                    role_item.role.id,
                ),
            )
            db.cur.execute(
                "SELECT SUM(shield) FROM owned_roles WHERE role_id = ? AND user_id != ?",
                (
                    role_item.role.id,
                    message.author.id,
                ),
            )
            shield = db.cur.fetchone()[0]
            description = (
                f"{message.author.mention} has sacrificed {role_item.to_english()}. "
            )
            if shield == 0:
                db.cur.execute(
                    "UPDATE owned_roles SET amount = MAX(amount - ?, 0) WHERE role_id = ? and user_id != ?",
                    (
                        role_item.amount,
                        role_item.role.id,
                        message.author.id,
                    ),
                )
                description += f"{role_item.role.mention} wasn't shielded; all other owners lose the same."
            else:
                if role_item.amount > shield:
                    damage = role_item.amount - shield
                    db.cur.execute(
                        "UPDATE owned_roles SET amount = MAX(amount - ?, 0), shield = 0 WHERE role_id = ? AND user_id != ?",
                        (
                            role_item.amount,
                            role_item.role.id,
                            message.author.id,
                        ),
                    )
                    description += f"{role_item.role.mention}'s shield absorbed {shield:g} damage, but all owners still lost {damage:g} of the role."
                else:
                    remaining_fraction_of_shield = (shield - role_item.amount) / shield
                    db.cur.execute(
                        "UPDATE owned_roles SET shield = shield * ? WHERE role_id = ? AND user_id != ?",
                        (
                            remaining_fraction_of_shield,
                            role_item.role.id,
                            message.author.id,
                        ),
                    )
                    description += (
                        f"{role_item.role.mention}'s shield absorbed all damage but was "
                        + f"{'destroyed' if role_item.amount == shield else 'damaged'} as a result."
                    )
            await get_channel_named(EVENTS_CHANNEL_NAME).send(
                embed=Embed(
                    title="Role Sacrifice (OH NO!)",
                    description=description,
                    color=get_guild().get_member(message.author.id).color,
                )
            )
        db.con.commit()
    else:
        await on_lack_of_understanding(message)


async def command_shield(message: Message, command: List[str]) -> None:
    """Reduce the number of roles you own to protect that amount of those roles from the next sacrifice."""
    if len(command) > 1:
        parser = ItemGroupParser()
        try:
            item_group: ItemGroup = parser.parse(" ".join(command[1:]))
        except MeWhiningException as e:
            await message.channel.send(
                voice_filter(f"{e.bot_message}, {message.author.mention}.")
            )
            return
        for item in item_group.item_list:
            if item.get_type() != ItemType.ROLE:
                await message.channel.send(
                    voice_filter(
                        f"You can only shield roles, {message.author.mention}."
                    )
                )
                return
            role_item: RoleItem = item
            db.cur.execute(
                f"SELECT amount FROM owned_roles WHERE user_id = ? AND role_id = ?",
                (
                    message.author.id,
                    role_item.role.id,
                ),
            )
            row = db.cur.fetchone()
            amount = row[0] if row is not None else 0
            if amount < role_item.amount:
                await message.channel.send(
                    voice_filter(
                        f"You're attempting to sacrifice more roles than you control, {message.author.mention}."
                    )
                )
                return
        for role_item in item_group.item_list:
            db.cur.execute(
                f"UPDATE owned_roles SET amount = amount - ?, shield = shield + ? WHERE user_id = ? AND role_id = ?",
                (
                    role_item.amount,
                    role_item.amount,
                    message.author.id,
                    role_item.role.id,
                ),
            )
        db.con.commit()
    else:
        await on_lack_of_understanding(message)


async def command_recycle(message: Message, command: List[str]) -> None:
    """Decrement the amount of a role that you own the totality of and randomly recolor and rename it."""
    if len(command) == 2 and re.match(r"^@\w+$", command[1]):
        role = get_role_named(command[1][1:])
        if role is not None:
            role_ownership_level = get_role_ownership_level(message.author.id, role.id)
            if role_ownership_level == RoleOwnershipLevel.TOTALITY:
                RoleItem(role).take_from(message.author.id, commit=False)
                old_name = role.name
                await recycle_role(role)
                create_task(
                    message.channel.send(
                        voice_filter(
                            "I have replaced ",
                            f"`@{old_name}`",
                            f"with a new role that is still pure of the taint of treason: {role.mention}.",
                        )
                    )
                )
                await get_channel_named(EVENTS_CHANNEL_NAME).send(
                    embed=Embed(
                        description=f"The role once known as @{old_name} has been transformed into @{role.name} ({role.mention}).",
                        color=role.color,
                    ),
                )
            else:
                db.cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM roles WHERE role_id = ?)", (role.id,)
                )
                if db.cur.fetchone():
                    await message.channel.send(
                        voice_filter(
                            "You need to own the totality of a role in order to recycle it."
                        )
                    )
                else:
                    await message.channel.send(voice_filter("What?"))
        else:
            await message.channel.send(
                voice_filter(f"That role doesn't even exist, {message.author.mention}.")
            )
    else:
        await on_lack_of_understanding(message)


async def command_buy(message: Message, command: List[str]) -> None:
    if len(command) <= 1:
        await on_lack_of_understanding(message)
        return

    parser = ItemGroupParser()
    try:
        role_items: ItemGroup = parser.parse(" ".join(command[1:]))
    except MeWhiningException as e:
        await message.channel.send(
            voice_filter(f"{e.bot_message}, {message.author.mention}.")
        )
        return

    role_map: Dict[Role, int] = {}
    for item in role_items.item_list:
        if item.get_type() != ItemType.ROLE:
            await message.channel.send(
                voice_filter(
                    f"This command can only buy roles, {message.author.mention}. Note that {item.to_english()} is under no circumstances a role."
                )
            )
            return

        if not item.amount.is_integer():
            await message.channel.send(
                voice_filter(
                    f"You've given me some leftover junk. Nice round numbers, none of this {item.amount} stuff. Or else."
                )
            )
            return

        if item.role in role_map:
            role_map[item.role] += int(item.amount)
        else:
            role_map[item.role] = int(item.amount)

    value_in_credit = sum(
        marginal_buy_price(role.id, n) for role, n in role_map.items()
    )

    if not CreditItem(value_in_credit).is_owned_by(message.author.id):
        fine = Agent(message.author.id).punish_wallet(0.5)
        await message.channel.send(
            voice_filter(
                f"You can't afford that, {message.author.mention}. Now you can afford even less: you've just lost yourself {fine}c"
            )
        )
        return

    try:
        for role, n in role_map.items():
            for _ in range(n):
                buy_role(message.author.id, role)
    except MeWhiningException as e:
        await message.channel.send(
            voice_filter(f"{e.bot_message}, {message.author.mention}.")
        )
        return
    db.con.commit()

    await message.channel.send(
        embed=Embed(
            description=f"You have successfully bought {role_items.to_english()} for {value_in_credit}c. Congratulations, {message.author.mention}.",
            color=get_guild().get_member(message.author.id).color,
        )
    )


async def command_sell(message: Message, command: List[str]) -> None:
    if len(command) <= 1:
        await on_lack_of_understanding(message)
        return

    parser = ItemGroupParser()
    try:
        role_items: ItemGroup = parser.parse(" ".join(command[1:]))
    except MeWhiningException as e:
        await message.channel.send(
            voice_filter(f"{e.bot_message}, {message.author.mention}.")
        )
        return

    roles_list: List[int] = set()
    value_in_credit = 0
    for item in role_items.item_list:
        if item.get_type() != ItemType.ROLE:
            await message.channel.send(
                voice_filter(
                    f"This command can only sell roles, {message.author.mention}. Note that {item.to_english()} is under no circumstances a role."
                )
            )
            return

        if not item.amount.is_integer():
            await message.channel.send(
                voice_filter(
                    f"You've given me some leftover junk. Nice round numbers, none of this {item.amount} stuff. Or else."
                )
            )
            return

        value_in_credit += sell_price(item.role.id)
        roles_list.add(item)

    if not role_items.is_owned_by(message.author.id):
        fine = Agent(message.author.id).punish_wallet(0.5)
        await message.channel.send(
            voice_filter(
                f"You can't afford that, {message.author.mention}. Now you can afford even less: you've lost yourself {fine}c"
            )
        )
        return

    try:
        for role_item in roles_list:
            for _ in range(int(role_item.amount)):
                sell_role(message.author.id, role_item.role)
    except MeWhiningException as e:
        await message.channel.send(
            voice_filter(f"{e.bot_message}, {message.author.mention}.")
        )
        return

    db.con.commit()
    await message.channel.send(
        embed=Embed(
            description=f"You have successfully sold {role_items.to_english()} for {value_in_credit}c. Congratulations, {message.author.mention}.",
            color=get_guild().get_member(message.author.id).color,
        )
    )


async def command_price(message: Message, command: List[str]) -> None:
    if len(command) == 2 and re.match(r"^@\w+$", command[1]):
        role = get_role_named(command[1][1:])
        if role is not None:
            price = role_price(role.id)
            if price is not None:
                await message.channel.send(
                    embed=Embed(
                        description=(
                            f"{role.mention} has a price of {price}.\n"
                            + f"`{COMMAND_PREFIX}buy` cost: { price * ROLE_TAX :g}\n"
                            + f"`{COMMAND_PREFIX}sell` reward: { price / ROLE_TAX :g}"
                        )
                    )
                )
            else:
                await message.channel.send(voice_filter("What?"))
        else:
            await message.channel.send(
                voice_filter(f"That role doesn't even exist, {message.author.mention}.")
            )
    else:
        await on_lack_of_understanding(message)


def random_roles_with_value(cost):
    reward, created_price = (ItemGroup(), 0)
    while created_price <= cost.amount:
        next_role = get_random_role_from_polya_urn()
        reward.add(RoleItem(next_role))
        created_price += buy_price(next_role.id)

    return reward


async def command_recombobulate(message: Message, command: List[str]) -> None:
    """Allow a user to give up an amount of goods and recieve goods in return.
    These become more valuable the more said user gives."""
    if len(command) < 2:
        await message.channel.send(
            voice_filter(
                "Offering nothing. A clever trick, but nothing gets past me. You must give to receive."
            )
        )
        return

    parser = ItemGroupParser()
    try:
        cost = parser.parse(" ".join(command[1:])).item_list[0]
    except MeWhiningException as e:
        await message.channel.send(f"{e.bot_message}, {message.author.mention}.")
        return

    if cost.amount < 10:
        await message.channel.send(
            voice_filter("You need 10 credits; come back when you're less poor.")
        )
        return

    if cost.get_type() != ItemType.CREDIT:
        await message.channel.send(
            voice_filter("That's nonsense. Don't you know what recombobulate means?")
        )
        return

    if not cost.is_owned_by(message.author.id):
        fine = Agent(message.author.id).punish_wallet(0.5)
        await message.channel.send(
            voice_filter(
                f"While I would love to take what you don't have and leave you bankrupt, I think I will simply take {fine}c from your account instead."
            )
        )
        return

    reward = random_roles_with_value(cost)

    reward.give_to(message.author.id)
    cost.take_from(message.author.id)

    line = random.choice(
        [
            "Double, double toil and trouble...",
            "Double, double toil and trouble...",
            "Double, double toil and trouble...",
            "Fire burn and cauldron bubble...",
            "Fillet of a fenny snake...",
            "In the cauldron boil and bake...",
            "Eye of newt and toe of frog...",
            "Wool of bat and tongue of dog...",
            "Adder's fork and blind-worm's sting...",
            "Lizard's leg and howlet's wing...",
        ]
    )
    await message.channel.send(
        voice_filter(line),
        embed=Embed(
            description=f"{message.author.mention} brews {reward.to_english()}.",
            color=get_guild().get_member(message.author.id).color,
        ),
    )


async def command_dismantle(message: Message, command: List[str]) -> None:
    """Destroy a unit of a role you own the simple majority of to extract the words that compose it as well as its color"""
    if len(command) > 1:
        parser = ItemGroupParser()
        try:
            role_items = parser.parse(" ".join(command[1:]))
        except MeWhiningException as e:
            await message.channel.send(
                voice_filter(f"{e.bot_message}, {message.author.mention}.")
            )
            return
        roles_set: Set[Role] = set()
        for item in role_items.item_list:
            if item.get_type() != ItemType.ROLE:
                await message.channel.send(
                    voice_filter(
                        f"This command can only dismantle roles, {message.author.mention}."
                    )
                )
                return
            if item.amount != 1 or item.role in roles_set:
                await message.channel.send(voice_filter("No."))
                return
            roles_set.add(item.role)
            if (
                get_role_ownership_level(message.author.id, item.role.id)
                < RoleOwnershipLevel.SIMPLE_MAJORITY
            ):
                await message.channel.send(
                    voice_filter(
                        f"You can't dismantle roles you don't own more than anyone else, {message.author.mention}."
                    )
                )
                return
        if roles_set:
            all_parts = ItemGroup()
            for role in list(roles_set):
                async for part in get_role_parts(role):
                    all_parts.add(part)
                all_parts.give_to(message.author.id)
            await message.channel.send(
                embed=Embed(
                    description=f"{message.author.mention} dismantles {role_items.to_english()} and gets {all_parts.to_english()} in return."
                )
            )
        else:
            await message.channel.send(
                embed=Embed(
                    description=f"{message.author.mention} dismantles nothing and gets nothing in return. Shocker."
                )
            )
    else:
        await on_lack_of_understanding(message)


async def command_suspect(message: Message, command: List[str]) -> None:
    if len(command) > 1:
        term = " ".join(command[1:])
        db.cur.execute(
            "SELECT EXISTS(SELECT 1 FROM suspicious_terms WHERE term = ?)", (term,)
        )
        if db.cur.fetchone()[0]:
            # TODO: owns owner of suspicious term
            pass
        else:
            # TODO: creates suspicious term?? (costs a lot)
            pass


async def command_ranking(message: Message, command: List[str]) -> None:
    db.cur.execute("SELECT role_id, price FROM roles ORDER BY price ASC")
    positions = {}
    lines = []
    i = 0
    rows = db.cur.fetchall()
    for role_id, price in rows:
        role = get_guild().get_role(role_id)
        lines.append(f"**{len(rows) - i}.** {role.mention}: {price:g}c")
        positions[role] = i
        i += 1
    positions[get_guild().self_role] = i + 1
    lines.reverse()
    await get_guild().edit_role_positions(positions=positions)
    await message.channel.send(
        embed=Embed(
            title="Role ranking",
            description="\n".join(lines),
            color=get_guild().roles[1].color,
        )
    )


async def command_inventory(message: Message, command: List[str]) -> None:
    words = get_agent(message.author.id).get_words()
    embed = Embed(title="Words", description=words.to_english())
    await message.channel.send(embed=embed)


async def command_moods(message: Message, command: List[str]) -> None:
    # Embed = Embed(title="All moods")
    # max_number_of_pips = 10
    # for mood_name in MOODS:
    #     emoji = ""
    #     if mood_name in MOOD_EMOJI:
    #         emoji = MOOD_EMOJI[mood_name]
    #     else:
    #         e = get(get_guild().emojis, name=mood_name)
    #         if e is not None:
    #             emoji = f"<:{mood_name}:{e.id}>"
    #     value = get_mood(mood_name)
    #     pips = round(value * max_number_of_pips)
    #     embed.add_field(
    #         name=f"{emoji} {mood_name}",
    #         value=f"{round(100 * value, 2)}%\n{'▓' * pips}{'░' * (max_number_of_pips - pips)}",
    #     )
    thalasin_embed, thalasin_plus_embed = get_mood_embeds()
    await message.channel.send(embed=thalasin_embed)
    await message.channel.send(embed=thalasin_plus_embed)


async def command_mood(message: Message, command: List[str]) -> None:
    max_number_of_pips = 20
    mood_name = " ".join(command[1:])
    emoji = ""
    if mood_name in MOOD_EMOJI:
        emoji = MOOD_EMOJI[mood_name]
    else:
        e = get(get_guild().emojis, name=mood_name)
        if e is not None:
            emoji = f"<:{mood_name}:{e.id}>"
    value = get_mood(mood_name)
    pips = round(value * max_number_of_pips)
    embed = Embed(
        title=f"{emoji} Current {mood_name} level: {round(100 * value, 2)}%",
        description=f"{'▓' * pips}{'░' * (max_number_of_pips - pips)}",
    )
    await message.channel.send(embed=embed)


async def command_testmood(message: Message, command: List[str]) -> None:
    input_ = float(command[1])
    moods = [word.split("=") for word in command[2:]]
    moods = {mood: float(weight) for mood, weight in moods}
    await message.channel.send(voice_filter(str(mood(input_, **moods))))


async def command_ascend(message: Message, _) -> None:
    ascender = get_agent(message.author.id)
    if not CreditItem(1000).is_owned_by(message.author.id):
        fine = Agent(message.author.id).punish_wallet()
        await message.channel.send(
            voice_filter(
                f"You may not ascend until you have 1000 credits. Now you have {fine} less."
            )
        )
        return

    ascender.ascend()

    await message.channel.send(voice_filter("Congratulations."))
    # await message.channel.send(
    #     voice_filter("This hasn't been implemented yet.", ":owned:")
    # )


async def command_impersonate(message: Message, command: List[str]) -> None:
    if message.content.index(">"):
        try:
            cost = AgentItem(command[1])
            victim_id = get_guild().get_member(cost.agent.user_id)
        except:
            await message.channel.send(
                voice_filter(
                    f"What the fuck do you think you're doing, {message.author.mention}?"
                )
            )
            return
        if not cost.is_owned_by(message.author.id):
            await message.channel.send(
                voice_filter(f"You don't own that agent, {message.author.mention}.")
            )
            return
        cost.take_from(message.author.id)
        content = message.content[message.content.index(">")]
        if content.strip() == "":
            content = "\u200c"

        await impersonate_user(
            victim_id,
            message.channel,
            content,
        )
    else:
        await on_lack_of_understanding(message)


# Tasks


async def discord_role_operations_loop() -> None:
    while True:
        db.cur.execute(
            "SELECT user_id, role_id, is_addition FROM pending_discord_role_operations ORDER BY user_id"
        )
        all_rows = db.cur.fetchall()
        if len(all_rows):
            db.cur.execute("DELETE FROM pending_discord_role_operations")
            db.con.commit()

            tasks = []
            additions = {}
            removals = {}

            g = get_guild()

            for row in all_rows:
                user_id, role_id, is_addition = row
                if is_addition:
                    if user_id not in additions:
                        additions[user_id] = []
                    additions[user_id].append(g.get_role(role_id))
                else:
                    if user_id not in removals:
                        removals[user_id] = []
                    removals[user_id].append(g.get_role(role_id))

            for user_id, role_list in additions.items():
                member: Member = get_guild().get_member(user_id)
                tasks.append(create_task(member.add_roles(*role_list)))

            for user_id, role_list in removals.items():
                member: Member = get_guild().get_member(user_id)
                tasks.append(create_task(member.remove_roles(*role_list)))

            await gather(*tasks)
        else:
            await async_sleep(1.0)


@tasks.loop(seconds=2.0)
async def refresh_profiles_loop() -> None:
    db.cur.execute("SELECT user_id FROM agents WHERE to_refresh = 1")
    all_rows = db.cur.fetchall()
    if len(all_rows):
        db.cur.execute("UPDATE agents SET to_refresh = 0")
        db.con.commit()
        for row in all_rows:
            create_task(Agent(row[0]).refresh_profile())
    # db.cur.execute("SELECT user_id FROM pending_profile_refreshes")
    # all_rows = db.cur.fetchall()
    # if len(all_rows):
    #     db.cur.execute("TRUNCATE TABLE pending_profile_refreshes")
    #     db.con.commit()
    #     for row in all_rows:
    #         a = Agent2(row[0])
    #         create_task(a.refresh_profile())


@tasks.loop(seconds=1.0)
async def update_mood_loop() -> None:
    l = [abs(get_mood(i) + rand.normal(0, 0.005)) for i in MOODS]
    l = [i / la.norm(l) for i in l]
    i = 0
    while i < len(MOODS):
        set_mood(MOODS[i], l[i])
        i = i + 1


@tasks.loop(seconds=5.0)
async def refresh_mood_list_loop() -> None:
    try:
        channel = get_channel_named(MOODS_CHANNEL_NAME)

        # this stuff would be helpful for a get_first_messages(n: int) -> Tuple[Message] function
        history = await channel.history(limit=500, oldest_first=True).flatten()
        thalasin_embed, thalasin_plus_embed = get_mood_embeds()
        if len(history) > 0:
            first = history[0]
            if len(history) > 1:
                second = history[1]
            else:
                second = await channel.send("...")
        else:
            first = await channel.send("...")
            second = await channel.send("...")

        await first.edit(embed=thalasin_embed)
        await second.edit(embed=thalasin_plus_embed)
    except Exception as e:
        await debug_print(e)


# inactive task
@tasks.loop(seconds=WHIM_SECONDS)
async def whim_loop() -> None:
    global seconds_to_toggle_whim, active_whim, normal_messages_since_last_whim_started
