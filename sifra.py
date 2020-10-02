#2.A SIFRATOR - najprv substitucna sifra nasledne Vigenerovou

def sifruj(permutacia, heslo, vstup):
    vystup = ''
    for cislo, pismenko in enumerate(vstup.lower()):
        po_substitucnej = permutacia[ord(pismenko)-ord('a')].lower()
        po_substitucnej_od_nuly = ord(po_substitucnej) - ord('a')
        posun = heslo[cislo % len(heslo)]
        posun_od_nuly = ord(posun) - ord('a')
        vystup += chr(((po_substitucnej_od_nuly + posun_od_nuly) % 26) + ord('a'))
    return vystup

p = input("Permutacia: ")
h = input("Heslo: ")
v = input("Vstup: ")
print(sifruj(p, h, v))


# 1.B DESIFROVANIE ked pozname algoritmus ale nemame kluc
# 1. najst dlzku kluca podla vzdialenosti vyskytov rovnakych skupiniek symbolov
# (dlzka kluca bude najvacsi spolocny delitel vzdialenosti avsak treba ratat s tym, ze niektore vyskyty su tam omylom navyse)

# 2. rozdelit vstup na skupiny po jednotlivych castiach kluca a pristupovat k nim ako k rieseniu r permutacii
# - napr. skusanim, pripadne frekvencnou analyzou?








def desifruj(permutacia, heslo, vstup):
    vystup = ''
    for cislo, pismenko in enumerate(vstup.lower()):
        od_nuly = ord(pismenko) - ord('a')
        posun = heslo[cislo % len(heslo)]
        posun_od_nuly = ord(posun) - ord('a')
        po_vygener = chr(((od_nuly - posun_od_nuly) % 26) + ord('a'))
        vystup += permutacia[ord(po_vygener)-ord('a')].lower()
    return vystup