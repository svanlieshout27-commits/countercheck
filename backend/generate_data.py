import json
import random
import os

random.seed(42)  # reproducible

AFFORDABLE_BRANDS = {
    "Casio": ["G-Shock GA-2100", "F-91W", "Edifice EFR-526", "Vintage A158WA"],
    "Seiko": ["5 Sports SRPD55", "Prospex SBDC053", "Presage SRPB41"],
    "Citizen": ["Eco-Drive BM8180", "Promaster Diver BN0150", "Corso BM7100"],
    "Fossil": ["Grant FS4835", "Townsman ME3061", "Neutra FS5380"],
    "Timex": ["Weekender TW2T29400", "Easy Reader T20441", "Expedition T49870"],
    "Bulova": ["Marine Star 98B203", "Classic 96A157"],
    "Hamilton": ["Khaki Field H68411533", "Jazzmaster H32411735"],
}
LUXURY_BRANDS = {
    "Rolex": ["Submariner 116610LN", "Datejust 126234", "GMT-Master II 126710BLNR"],
    "Omega": ["Speedmaster Professional 311.30.42", "Seamaster Diver 300M"],
    "Tag Heuer": ["Carrera CBN2A1A", "Aquaracer WAY201E"],
    "Breitling": ["Navitimer B01", "Superocean Heritage"],
}
SUSPECT_VARIANTS = {
    "Rolex": ["R0LEX", "Rolexx", "Rolax", "Roleex"],
    "Omega": ["0mega", "Omeega", "OMEEGA"],
    "Tag Heuer": ["T@g Heuer", "Tagg Heuer", "TAG HEUR"],
    "Breitling": ["Britling", "Breitliing"],
    "Casio": ["Casiio", "C@sio"],
    "Seiko": ["Seikko", "Saiko"],
}
SUSPECT_PHRASES = [
    "100% original brand new", "100% authentic guaranteed",
    "100% Genuine BRAND NEW with tags", "Factory sealed AAA+ quality",
    "1:1 mirror replica perfection", "BNWT super clone",
    "Best deal don't miss out!!!",
]
SUSPECT_DESCRIPTORS = [
    "shipping from China factory direct", "unbeatable price",
    "no questions asked refund", "limited stock!! buy now!!!",
    "perfect gift for boyfriend", "high quality replica wholesale",
]
LEGIT_DESCRIPTORS = [
    "Stainless steel case with sapphire crystal.",
    "Water resistant to 100m. Quartz movement.",
    "Includes original box and warranty card.",
    "Owned for 2 years, excellent condition. Comes with extra link.",
    "Authorized dealer with full manufacturer warranty.",
    "Certified pre-owned with 1-year shop warranty.",
    "Brand new in factory packaging from authorized retailer.",
]

def make_legit():
    if random.random() < 0.7:
        brand = random.choice(list(AFFORDABLE_BRANDS.keys()))
        model = random.choice(AFFORDABLE_BRANDS[brand])
        price = round(random.uniform(45, 480), 2)
    else:
        brand = random.choice(list(LUXURY_BRANDS.keys()))
        model = random.choice(LUXURY_BRANDS[brand])
        price = round(random.uniform(2200, 14500), 2)
    title = f"{brand} {model} Men's Watch"
    description = " ".join(random.sample(LEGIT_DESCRIPTORS, k=2))
    return {"title": title, "brand": brand, "price": price, "description": description}

def make_suspect():
    real_brand = random.choice(list(LUXURY_BRANDS.keys()) + ["Casio", "Seiko"])
    brand_text = (random.choice(SUSPECT_VARIANTS[real_brand])
                  if real_brand in SUSPECT_VARIANTS and random.random() < 0.7
                  else real_brand)
    if real_brand in LUXURY_BRANDS:
        model = random.choice(LUXURY_BRANDS[real_brand])
        price = round(random.uniform(15, 95), 2)  # absurdly low for luxury
    else:
        model = random.choice(AFFORDABLE_BRANDS[real_brand])
        price = round(random.uniform(8, 22), 2)
    phrase = random.choice(SUSPECT_PHRASES)
    title = f"{phrase} {brand_text} {model}"
    if random.random() < 0.5:
        title = title.upper()
    desc = " ".join(random.sample(SUSPECT_DESCRIPTORS + SUSPECT_PHRASES, k=3))
    return {"title": title, "brand": real_brand, "price": price, "description": desc}

listings = []
for _ in range(500):
    listings.append(make_legit() if random.random() < 0.5 else make_suspect())

random.shuffle(listings)
for idx, item in enumerate(listings):
    item["listing_id"] = idx

os.makedirs("../data", exist_ok=True)
with open("../data/listings.jsonl", "w", encoding="utf-8") as f:
    for item in listings:
        f.write(json.dumps(item) + "\n")

print(f"Generated 500 listings → ../data/listings.jsonl")