from faker import Faker
from random import choice
from hut_finder.models import Hut

fake = Faker()

# Extended list of real mountain names from the Alps and other famous mountain ranges
mountain_names = [
    "Matterhorn", "Mont Blanc", "Eiger", "Jungfrau", "Mönch", "Grossglockner", 
    "Dufourspitze", "Zugspitze", "Grand Combin", "Dent Blanche", "Weisshorn", 
    "Piz Bernina", "Ortler", "Grossvenediger", "Wildspitze", "Barre des Écrins", 
    "Piz Palü", "Dachstein", "Piz Badile", "Grand Paradis", "Aletschhorn", 
    "Dom", "Weissmies", "Finsteraarhorn", "Piz Roseg", "Piz Morteratsch", 
    "Bishorn", "Rimpfischhorn", "Piz Kesch", "Gran Zebru", "Adamello", 
    "Tre Cime di Lavaredo", "Kufstein", "Hochvogel", "Bärenhorn", 
    "Wildhorn", "Nadelhorn", "Gspaltenhorn", "Pointe de Zinal", "Ober Gabelhorn", 
    "Cima di Rosso", "Dent d'Hérens", "Silvretta", "Hohe Tauern", 
    "Schreckhorn", "Rätikon", "Tödi", "Similaun", "Niesen", "Diablerets", 
    "Finsteraarhorn", "Grand Muveran", "Weissfluh", "Liskamm", "Mont Pelvoux", 
    "Grosser Priel", "Marmolada", "Hohe Munde", "Piz Corvatsch", "Cima Tosa", 
    "Dammastock", "Piz Buin", "Serles", "Mont Pourri", "Aiguille du Dru", 
    "Mittelallalin", "Ortstock", "Lagginhorn", "Säntis", "Schilthorn", 
    "Piz Julier", "Kreuzspitze", "Nadelgrat", "Ringelspitz", "Blümlisalp", 
    "Hinter Fiescherhorn", "Trift Glacier", "Monte Leone", "Hochalmspitze", 
    "Aiguille Verte", "Pointe Percée", "Doldenhorn", "Le Catogne", "Mont Gelé", 
    "Wildstrubel", "Bernina", "Piz Beverin", "Weisskugel", "Glockturm", 
    "Piz Cengalo", "Hochfeiler", "Seehorn", "Flüela Wisshorn", "Mont Dolent", 
    "Galenstock"
]

# List of possible suffixes for hut names
suffixes = [
    "Hut", "Lodge", "Refuge", "Chalet", "Alp", "Cabin", 
    "Shelter", "Cottage", "Inn", "House", "Retreat", "Hideaway",
    "Alm", "Hütte"
]

descriptions = [
    "Located in a breathtaking mountain valley.",
    "Offers stunning views of nearby peaks.",
    "Known for its cozy atmosphere and hearty meals.",
    "Popular among hikers and climbers alike.",
    "Provides a refuge from harsh alpine weather.",
    "A starting point for many mountain adventures.",
    "Famous for its traditional alpine architecture.",
    "Has a rich history of mountaineering culture.",
    "Surrounded by pristine alpine wilderness.",
    "Hosts educational programs about local flora and fauna.",
    "Offers guided tours and alpine skills workshops.",
    "A favorite spot for stargazing enthusiasts.",
    "Named after a local mountaineering legend.",
    "Provides a warm welcome to weary travelers.",
    "Renowned for its homemade alpine cuisine.",
    "Home to a collection of antique mountaineering gear.",
    "A basecamp for challenging summit attempts.",
    "Offers comfortable accommodations at high altitudes.",
    "Surrounded by cascading alpine meadows.",
    "Known for its sustainable practices and eco-friendly initiatives."
]

def create_huts(num_huts):
    names = {}
    while len(names) < num_huts:
        mountain_name = choice(mountain_names)
        suffix = choice(suffixes).capitalize()
        name = f"{mountain_name} {suffix}"
        if name not in names:
            names[name] = True

    for name in names:
        description = choice(descriptions)
        hut = Hut.objects.create(name=name, description=description)
        print(f"🏞️ Added {name}: {description}")

create_huts(500)
