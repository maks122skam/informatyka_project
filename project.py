import json
import math
import random
import sys
import copy


JEZYKI = {
    'pl': 'dane_gry_pl.json',
    'en': 'dane_gry_en.json',
}

lang = input("Wybierz jezyk / Select language ({langs}): ".format(langs=' / '.join(JEZYKI))).strip().lower()
if lang not in JEZYKI:
    lang = 'pl'

try:
    with open(JEZYKI[lang], 'r', ) as f:
        GRA_DANE = json.load(f)

except FileNotFoundError:
    print(f"Error: File '{JEZYKI[lang]}' not found!")
    sys.exit()

TEKSTY = GRA_DANE['teksty']
NAZWY_POL = GRA_DANE['nazwy_pol']

STAT_KOLEJNOSC = ['poziom', 'zycie', 'max_zycie', 'atak', 'obrona', 'unik', 'predokosc', 'exp', 'exp_do_awansu']


def pokaz_statystyki(gracz):
    """Wyświetla aktualne statystyki gracza (poziom, życie, atak ) """
    
    print(TEKSTY['statystyki_naglowek'])
    for pole in STAT_KOLEJNOSC:
        if pole in gracz and pole in NAZWY_POL:
            print(TEKSTY['stat_linia'].format(nazwa=NAZWY_POL[pole], wartosc=gracz[pole]))


def level_up(gracz):
    """Podnosi gracza o jeden poziom. Wyświetla komunikat o awansie i nowe statystyki."""
    
    gracz['zycie'] = math.ceil(gracz['max_zycie'] + 0.3 * gracz['max_zycie'])
    gracz['max_zycie'] = gracz['zycie']
    gracz['atak'] += math.ceil(0.2 * gracz['atak'])
    gracz['obrona'] += math.ceil(0.1 * gracz['obrona'])
    gracz['unik'] += math.ceil(0.05 * gracz['unik'])
    gracz['predokosc'] += math.ceil(0.05 * gracz['predokosc'])
    gracz['poziom'] += 1
    print(TEKSTY['awans'])
    pokaz_statystyki(gracz)


def dodaj_exp(gracz, ilosc_exp):
    """Dodaje ilosc_exp punktów doświadczenia graczowi. Jeśli gracz osiągnie próg exp_do_awansu, automatycznie wywołuje level_up()"""
    
    gracz['exp'] += ilosc_exp
    print(TEKSTY['exp_zdobywasz'].format(ilosc=ilosc_exp, exp=gracz['exp'], exp_do_awansu=gracz['exp_do_awansu']))

    while gracz['exp'] >= gracz['exp_do_awansu']:
        gracz['exp'] -= gracz['exp_do_awansu']
        level_up(gracz)
        gracz['exp_do_awansu'] = math.ceil(gracz['exp_do_awansu'] * 1.5)
        print(TEKSTY['nowy_prog_exp'].format(prog=gracz['exp_do_awansu']))


def attack(atakujacy, broniacy):
    """Wykonuje  atak atakującego na broniącego. Sprawdza szansę na unik, 
    losuje obrażenia z przedziału [50% ataku, atak] i odejmuje obronę broniącego.
    Zwraca zadane obrażenia (0 jeśli atak został unikiięty)."""
   
    if random.randint(1, 100) <= broniacy['unik']:
        print(TEKSTY['unikanie'].format(nazwa=broniacy['nazwa']))
        return 0

    min_obrazenia = max(1, int(atakujacy['atak'] * 0.5))
    surowe_obrazenia = random.randint(min_obrazenia, atakujacy['atak'])
    obrazenia = max(0, surowe_obrazenia - broniacy['obrona'])
    broniacy['zycie'] -= obrazenia
    print(TEKSTY['zadaje_obrazenia'].format(atakujacy=atakujacy['nazwa'], obrazenia=obrazenia, cel=broniacy['nazwa']))
    return obrazenia


def daj_potwora(nazwa_potwora):
    """Zwraca  kopię danych potwora o podanej nazwie klucza z pliku JSON."""
    
    return copy.deepcopy(GRA_DANE['potwory'][nazwa_potwora])


def walka(gracz, potwor):
    """Prowadzi turową walkę między graczem a potworem. 
    W każdej turze gracz wybiera atak (1) lub leczenie (2), potem potwór atakuje automatycznie.
    Zwraca True jeśli gracz wygrał, False jeśli przegrał."""
    
    print(TEKSTY['atak_na_ciebie'].format(nazwa=potwor['nazwa']))
    while gracz['zycie'] > 0 and potwor['zycie'] > 0:
        print(TEKSTY['zycie_status'].format(zycie=gracz['zycie'], zycie_przeciwnika=potwor['zycie']))
        action = input(TEKSTY['akcja_walka'])

        if action == '1':
            attack(gracz, potwor)
            if potwor['zycie'] <= 0:
                print(TEKSTY['pokonal'].format(nazwa=potwor['nazwa']))
                dodaj_exp(gracz, potwor['exp'])
                return True
        elif action == '2':
            procent_leczenia = random.randint(5, 15)
            wartosc_leczenia = max(1, math.ceil(gracz['max_zycie'] * procent_leczenia / 100))
            poprzednie_zycie = gracz['zycie']
            gracz['zycie'] = min(gracz['max_zycie'], gracz['zycie'] + wartosc_leczenia)
            realne_leczenie = gracz['zycie'] - poprzednie_zycie
            print(TEKSTY['leczenie'].format(ile=realne_leczenie, proc=procent_leczenia))
        else:
            print(TEKSTY['zla_akcja'])
            continue

        attack(potwor, gracz)
        if gracz['zycie'] <= 0:
            print(TEKSTY['przegrana'])
            return False

    return gracz['zycie'] > 0


def stworz_gracza(character_class):
    """Tworzy i zwraca  kopię danych gracza dla podanej klasy postaci. Jeśli klasa nie istnieje, zwraca None."""
    
    klasy = GRA_DANE['klasy_postaci']
    if character_class in klasy:
        return copy.deepcopy(klasy[character_class])
    return None






user_choice = input(TEKSTY['wybor_klasy'])

gracz = stworz_gracza(user_choice)

if gracz is None:
    print(TEKSTY['brak_klasy'])
    sys.exit()

pokaz_statystyki(gracz)

i = 0

input(TEKSTY['wchodzisz_loch'])

DRZWI = GRA_DANE['drzwi']

while i != 10 and gracz['zycie'] > 0:
    
    print(TEKSTY['drzwi_widok'])
    door = input(TEKSTY['wybor_drzwi'])

    if door not in DRZWI:
        print(TEKSTY['brak_drzwi'])
        continue

    wylosowany = random.choice(DRZWI[door])
    
    if wylosowany == 'przegrana':
        print(TEKSTY['przegrana'])
        break
    
    if not walka(gracz, daj_potwora(wylosowany)):
        break

    i += 1

if gracz['zycie'] > 0 and i == 10:
    print(TEKSTY['wygrana_loch'])