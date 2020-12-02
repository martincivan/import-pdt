# Na zakódovanie piatich symbolov boli použité kódové slova 1, 010 a 001.
# Koľkými spôsobmi je možné doplniť zostávajúce dve kódové slová, ak ich dĺžka má byť maximálne 5 a má ísť o prefixový kód?

# hladanie viac-menej brute-force

start = ["1", "01"]
vysledky = []  # sety lebo na poradi nezalezi a nechceme duplikaty


def skontroluj(mnozina, cislo):
    for slovo in mnozina:
        if slovo.startswith(cislo) or cislo.startswith(slovo):
            return False
    return True


for i in range(32):  # hladame binarne cisla do 16 - lebo 2^5 = 32, ale prvy bit nesmie byt 1 - cize max po 15
    for z in range(7):  # pridanie roznych poctov nul na zaciatku
        cislo1 = ('{:0' + str(z) + 'b}').format(i)
        aktualne = start.copy()
        if skontroluj(aktualne, cislo1):
            aktualne.append(cislo1)
            for j in range(32):  # hladame druhe cislo
                for y in range(7):  # pridanie nul na zaciatku 2 cisla
                    cislo2 = ('{:0' + str(y) + 'b}').format(j)
                    if skontroluj(aktualne, cislo2):
                        najdene = aktualne.copy()
                        najdene.append(cislo2)
                        for a in range(32):  # hladame druhe cislo
                            for b in range(7):  # pridanie nul na zaciatku 2 cisla
                                cislo3 = ('{:0' + str(b) + 'b}').format(a)
                                if skontroluj(najdene, cislo3):
                                    najdene2 = najdene.copy()
                                    najdene2.append(cislo3)
                                    for c in range(32):  # hladame druhe cislo
                                        for d in range(7):  # pridanie nul na zaciatku 2 cisla
                                            cislo4 = ('{:0' + str(d) + 'b}').format(c)
                                            if skontroluj(najdene2, cislo4):
                                                najdene3 = najdene2.copy()
                                                najdene3.append(cislo3)
                                                # if najdene3 not in vysledky:
                                                vysledky.append(frozenset(najdene3))

print("Vysledkov: " + str(len(vysledky)))

# rozumne zoradenie pri vypise
# stringy = [str(sorted(vysledok, key=len)) for vysledok in vysledky]
# for string in sorted(stringy):
#     print(string)

# Vysledkov: 71
# ['1', '001', '010', '000', '0110']
# ['1', '001', '010', '000', '01100']
# ['1', '001', '010', '000', '01101']
# ['1', '001', '010', '000', '0111']
# ['1', '001', '010', '000', '01110']
# ['1', '001', '010', '000', '01111']
# ['1', '001', '010', '0000', '0001']
# ['1', '001', '010', '0000', '00010']
# ['1', '001', '010', '0000', '00011']
# ['1', '001', '010', '0000', '01100']
# ['1', '001', '010', '0000', '01101']
# ['1', '001', '010', '0000', '01110']
# ['1', '001', '010', '0000', '01111']
# ['1', '001', '010', '00000', '00001']
# ['1', '001', '010', '00000', '00010']
# ['1', '001', '010', '00000', '00011']
# ['1', '001', '010', '00000', '01100']
# ['1', '001', '010', '00000', '01101']
# ['1', '001', '010', '00000', '01110']
# ['1', '001', '010', '00000', '01111']
# ['1', '001', '010', '00001', '01101']
# ['1', '001', '010', '0001', '00000']
# ['1', '001', '010', '0001', '00001']
# ['1', '001', '010', '0001', '01100']
# ['1', '001', '010', '0001', '01101']
# ['1', '001', '010', '0001', '01110']
# ['1', '001', '010', '0001', '01111']
# ['1', '001', '010', '00010', '00001']
# ['1', '001', '010', '00010', '00011']
# ['1', '001', '010', '00010', '01100']
# ['1', '001', '010', '00010', '01101']
# ['1', '001', '010', '00010', '01110']
# ['1', '001', '010', '00010', '01111']
# ['1', '001', '010', '00011', '00001']
# ['1', '001', '010', '00011', '01100']
# ['1', '001', '010', '00011', '01101']
# ['1', '001', '010', '00011', '01110']
# ['1', '001', '010', '00011', '01111']
# ['1', '001', '010', '0110', '0000']
# ['1', '001', '010', '0110', '00000']
# ['1', '001', '010', '0110', '00001']
# ['1', '001', '010', '0110', '0001']
# ['1', '001', '010', '0110', '00010']
# ['1', '001', '010', '0110', '00011']
# ['1', '001', '010', '0110', '0111']
# ['1', '001', '010', '0110', '01110']
# ['1', '001', '010', '0110', '01111']
# ['1', '001', '010', '01100', '00001']
# ['1', '001', '010', '01100', '01101']
# ['1', '001', '010', '01100', '01110']
# ['1', '001', '010', '01100', '01111']
# ['1', '001', '010', '0111', '0000']
# ['1', '001', '010', '0111', '00000']
# ['1', '001', '010', '0111', '00001']
# ['1', '001', '010', '0111', '0001']
# ['1', '001', '010', '0111', '00010']
# ['1', '001', '010', '0111', '00011']
# ['1', '001', '010', '0111', '01100']
# ['1', '001', '010', '0111', '01101']
# ['1', '001', '010', '01110', '00001']
# ['1', '001', '010', '01110', '01101']
# ['1', '001', '010', '01110', '01111']
# ['1', '001', '010', '01111', '00001']
# ['1', '001', '010', '01111', '01101']
# ['1', '001', '011', '010', '000']
# ['1', '001', '011', '010', '0000']
# ['1', '001', '011', '010', '00000']
# ['1', '001', '011', '010', '00001']
# ['1', '001', '011', '010', '0001']
# ['1', '001', '011', '010', '00010']
# ['1', '001', '011', '010', '00011']
#
# Process finished with exit code 0
