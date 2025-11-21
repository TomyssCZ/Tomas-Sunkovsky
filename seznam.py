# Seznam věcí
seznam = [
    "Jablko",
    "Banán",
    "Pomeranč",
    "Jahoda",
    "Malina",
    "Černý rybíz",
    "Červený rybíz",
    "Ananas",
    "Kiwi",
    "Mango",
    "Papája",
    "Hruška",
    "Broskev",
    "Třešeň",
    "Meruňka",
    "Řepa",
    "Mrkev",
    "Okurka",
    "Rajče",
    "Paprika",
    "Cibule",
    "Česnek",
    "Salát",
    "Kapusta",
    "Brokolice",
    "Cauliflower",
    "Zucchini",
    "Batát",
    "Brambory",
    "Kukuřice",
]

# Tisk seznamu
print("=== PŮVODNÍ SEZNAM ===")
for i, položka in enumerate(seznam, 1):
    print(f"{i}. {položka}")
print(f"Délka seznamu: {len(seznam)}\n")

# Úkol 1: Přidá do listu další položku
print("=== ÚKOL 1: Přidání nové položky ===")
seznam.append("Vodní meloun")
print(f"Přidáno: Vodní meloun")
print(f"Nový počet položek: {len(seznam)}\n")

# Úkol 2: Odstraní z listu první prvek
print("=== ÚKOL 2: Odebrání prvního prvku ===")
první_prvek = seznam.pop(0)
print(f"Odstraněno: {první_prvek}")
print(f"Nový počet položek: {len(seznam)}\n")

# Úkol 3: Vypíše délku listu
print("=== ÚKOL 3: Délka seznamu ===")
print(f"Aktuální délka seznamu: {len(seznam)}\n")

# Úkol 4: Vypíše celý list
print("=== ÚKOL 4: Celý seznam ===")
print("Aktuální obsah seznamu:")
for i, položka in enumerate(seznam, 1):
    print(f"{i}. {položka}")
