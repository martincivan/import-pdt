# Na zakódovanie piatich symbolov boli použité kódové slova 1, 010 a 001.
# Koľkými spôsobmi je možné doplniť zostávajúce dve kódové slová, ak ich dĺžka má byť maximálne 5 a má ísť o prefixový kód?


start = ["1", "010", "001"]
# vysledky = []
vysledky = []


def skontroluj(mnozina, cislo):
    for slovo in mnozina:
        if slovo.startswith(cislo) or cislo.startswith(slovo):
            return False
    return True


def zarovnat_na(co):
    for zaklad in range(6):
        if (co < 2 ** zaklad):
            return zaklad + 1
    raise RuntimeError("mali zaklad")


for i in range(32):  # hladame do 16 - lebo 2^5 = 32, ale prvy bit nesmie byt 1 - cize max po 15
    for z in range(4):
        cislo1 = ('{:0' + str(zarovnat_na(i) + z) + 'b}').format(i)
        if len(cislo1) > 5:
            continue
        aktualne = start.copy()
        if skontroluj(aktualne, cislo1):
            aktualne.append(cislo1)
            for j in range(16):
                for y in range(4):
                    cislo2 = ('{:0' + str(zarovnat_na(j) + y) + 'b}').format(j)
                    if len(cislo2) > 5:
                        continue
                    if skontroluj(aktualne, cislo2):
                        najdene = aktualne.copy()
                        najdene.append(cislo2)
                        vysledky.append(najdene)

print("Vysledkov: " + str(len(vysledky)))
for vysledok in vysledky:
    print(vysledok)
