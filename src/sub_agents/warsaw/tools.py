from enum import Enum
from typing import Any, Optional

import requests
import bs4


class WarsawCategories(str, Enum):
    PAPER = "Papier"
    METAL_AND_PLASTIC = "Metale i tworzywa sztuczne"
    GLASS = "Szkło"
    ORGANIC = "Bio"
    MIXED = "Odpady zmieszane"
    GREEN = "Odpady zielone"
    LARGE = "Odpady wielkogabarytowe"


def warsaw__get_garbage_schedule(address: str, category: str) -> list[str]:
    """Retrieves the schedule of upcoming garbage collections for a given address in Warsaw.

    Inputs:
        address: str: Location from where garbage will be picked up.
        category: str: garbage category. Must be one of Papier, Metale i tworzywa sztuczne, Szkło, Bio, Odpady zmieszane, Odpady zielone, Odpady wielkogabarytowe.
    Returns:
        list[str]: list of garbage collection dates in ISO 8601 format.
    """

    return ["2024-10-01", "2024-10-15", "2024-10-29"]


def warsaw__get_garbage_sorting_rules() -> dict:
    """Retrieves the general sorting rules for garbage in Warsaw.

    Returns:
        str: Garbage sorting rules in Polish.
    """
    url = "https://segregujna5.um.warszawa.pl/jak-segregowac/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return {}

    # Parse the HTML
    soup = bs4.BeautifulSoup(response.content, "html.parser")

    # Extract main content
    result = {
        "general_rules": [],
        "waste_categories": {},
        "special_disposal": {},
        "raw_text": "",
    }

    # Get all text content
    main_content = soup.get_text()
    result["raw_text"] = main_content

    # Parse structured information
    lines = [line.strip() for line in main_content.split("\n") if line.strip()]

    # Extract general rules (usually at the beginning)
    general_rules = []
    for line in lines:
        if line.startswith("- ") and any(
            keyword in line.lower()
            for keyword in ["nie", "opróżniamy", "odrywamy", "zgniatamy"]
        ):
            general_rules.append(line[2:])  # Remove "- " prefix

    result["general_rules"] = general_rules

    # Parse waste categories
    waste_categories: dict[str, Any] = {}
    current_category = None

    for i, line in enumerate(lines):
        # Detect category headers
        if line in ["Papier", "Bioodpady", "Szkło", "Zielone", "Odpady zmieszane"]:
            current_category = line
            waste_categories[current_category] = {"allowed": [], "not_allowed": []}

        # Extract TAK/NIE items
        elif line.startswith("TAK:") and current_category:
            items = line[4:].split(", ")
            waste_categories[current_category]["allowed"] = [
                item.strip() for item in items
            ]

        elif line.startswith("NIE:") and current_category:
            items = line[4:].split(", ")
            waste_categories[current_category]["not_allowed"] = [
                item.strip() for item in items
            ]

    result["waste_categories"] = waste_categories

    # Extract special disposal information
    special_disposal = {}
    special_keywords = [
        "Elektrośmieci",
        "Apteki",
        "PSZOK",
        "Baterie",
        "Odpady remontowe",
    ]

    for keyword in special_keywords:
        if keyword in main_content:
            # Find the section and extract relevant info
            keyword_index = main_content.find(keyword)
            if keyword_index != -1:
                # Get next few lines after the keyword
                section_text = main_content[keyword_index : keyword_index + 500]
                lines_section = section_text.split("\n")[:3]
                special_disposal[keyword] = " ".join(lines_section).strip()

    result["special_disposal"] = special_disposal

    return result


def warsaw__get_info_about_pszok() -> Optional[str]:
    """Retrieves the information about PSZOK places with addresses and specific garbage that should go there.

    Returns:
        str: Information about PSZOK.
    """

    url = "https://warszawa19115.pl/-/pszok-mpszok-punkty-selektywnej-zbiorki-odpadow-komunalny-1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

    # Parse the HTML
    soup = bs4.BeautifulSoup(response.content, "html.parser")

    main_content = soup.get_text()

    return main_content


# def warsaw__get_garbage_sorting_rules() -> str:
#     """Retrieves the general sorting rules for garbage in Warsaw.
#
#     Returns:
#         str: Garbage sorting rules in Polish.
#     """
#
#     return """
#     Frakcje odpadów komunalnych w Warszawie to:
#
#     a. papier (kolor pojemników lub naklejek informacyjnych oraz worków – niebieski, wrzucamy np.: czyste opakowania z papieru i tektury, gazety, czasopisma i ulotki, kartony, zeszyty, papier biurowy,
#     b. metale i tworzywa sztuczne (kolor pojemników lub naklejek informacyjnych oraz worków – żółty ), wrzucamy np.: puste, zgniecione butelki plastikowe, puste aerozole, zakrętki od butelek i słoików, plastikowe opakowania, torebki, worki foliowe, kartony po sokach i mleku (tzw. tetrapaki), zgniecione puszki po napojach i żywności,
#     c. szkło (kolor pojemników lub naklejek informacyjnych oraz worków – zielony ), wrzucamy np.: puste, szklane butelki, słoiki, szklane opakowania po kosmetykach, puste szklane opakowania po lekach,
#     d. bio (kolor pojemników lub naklejek informacyjnych oraz worków – brązowy ), wrzucamy np.: odpadki warzywne i owocowe, skorupki jaj, fusy po kawie i herbacie, zwiędłe kwiaty oraz rośliny doniczkowe, resztki jedzenia bez mięsa, kości oraz tłuszczów zwierzęcych,
#     e. zmieszane (kolor pojemników lub naklejek informacyjnych oraz worków – czarny); odpady pozostałe po wysegregowaniu pozostałych frakcji, czyli tylko to czego udało się rozdzielić do wymienionych pojemników na odpady segregowane lub czego nie można oddać do Punktu Selektywnej Zbiórki Odpadów Komunalnych, tzw. PSZOK.
#     f. odpady zielone (kolor worków lub naklejek informacyjnych – szary ), np.: liście, skoszona trawa, rozdrobnione gałęzie (odbiór od marca do listopada),
#     g. jako odpady wielkogabarytowe , np.: stare meble (także rozłożone na części) oraz wyroby tapicerskie (np. fotele, wersalki, pufy), materace, zabawki dużych rozmiarów.Pamiętaj: zapytaj swojego administratora, gdzie znajdziesz miejsce przeznaczone do składowania odpadów wielkogabarytowych.
#
#     Do pojemników przeznaczonych na segregację odpadów komunalnych NIE WOLNO WRZUCAĆ:
#
#     a. papier: zatłuszczonych opakowań z papieru, zużytych ręczników papierowych i chusteczek,
#     b. metale i tworzywa sztuczne : zużytych baterii i akumulatorów, sprzętu elektrycznego oraz elektronicznego, puszek i pojemników po farbach, butelek po olejach samochodowych, opakowań po olejach silnikowych, zatłuszczonego styropianu po żywności,
#     c. szkło : szkła stołowego, ceramiki, wyrobów ze szkła żaroodpornego, szkła okiennego, luster, szyb, żarówek świetlówek,
#     d. bioodpady : resztek mięsnych, kości oraz tłuszczy zwierzęcych, oleju jadalnego, ziemi i kamieni, odchodów zwierząt,
#     e. zmieszane: sprzętu elektrycznego oraz elektronicznego, AGD, baterii i akumulatorów, odpadów budowlanych i remontowych, odpadów zielonych, leków oraz chemikaliów.
#     f. do odpadów zielonych : kamieni, popiołu, ziemi,
#     g. jako odpady wielkogabarytowe : sprzętu elektrycznego oraz elektronicznego (np.: starych pralek, lodówek), materiałów i odpadów budowlanych, remontowych, wanien, umywalek, grzejników, muszli toaletowych, ram okiennych, drzwi, niesprasowanych dużych kartonów, opon samochodowych.
#     """


def warsaw__get_garbage_category_from_website(garbage_object: str) -> str:
    return WarsawCategories.ORGANIC.value


def warsaw__get_garbage_categories() -> list[str]:
    """Retrieves the list of garbage categories in Warsaw.

    Returns:
        list[str]: List of garbage categories.
    """

    return [c.value for c in WarsawCategories]


def warsaw__get_garbage_category_details(category: str) -> dict:
    """Retrieves the details of given garbage category.

    Inputs:
        category: str: garbage category. Must be one of Papier, Metale i tworzywa sztuczne, Szkło, Bio, Odpady zmieszane, Odpady zielone, Odpady wielkogabarytowe.
    Returns:
        dict: Details about garbage category.
    """

    paper = {
        "throw_away": "czyste opakowania z papieru, tektury, gazety, czasopisma i ulotki, kartony (zgniecione), zeszyty, papier biurowy",
        "do_not_throw_away": "zatłuszczone opakowania z papieru, zużyte ręczniki papierowe i chusteczki",
        "color": "niebieski",
        "instructions": "Brudny, zatłuszczony papier i karton nie nadają się do segregacji, a kartony i inne papierowe opakowania złóż lub zgnieć.",
    }

    glass = {
        "throw_away": "opakowania szklane, w szczególności: puste butelki, słoiki, opakowania po kosmetykach, puste opakowania po lekach",
        "do_not_throw_away": "szkło stołowe, ceramika, wyroby ze szkła żaroodpornego, szkło okienne, lustra, szyby, żarówki, świetlówki, porcelana",
        "color": "green",
        "instructions": "Zbite szklane naczynia takie jak kubki, talerze czy lustra wyrzucaj do odpadów zmieszanych",
    }

    metal_and_plastic = {
        "throw_away": "puste i zgniecione butelki plastikowe, zakrętki od butelek i słoików, worki foliowe, plastikowe opakowania, kartony typu tetrapak, puszki po napojach i żywności, puste pojemniki pod ciśnieniem, czyste opakowania styropianowe",
        "do_not_throw_away": "zużyte baterie i akumulatory, zużyty sprzęt elektryczny i elektroniczny, puszki i pojemniki po farbach, butelki po olejach samochodowych, opakowania po olejach silnikowych, zabrudzone opakowania styropianowe",
        "color": "yellow",
        "instructions": "Puszki, butelki plastikowe kartony i inne możliwe odpady przed ich wyrzuceniem zgnieć lub złóż.",
    }

    organic = {
        "throw_away": "odpadki warzywne i owocowe, skorupki jaj, fusy po kawie i herbacie, zwiędłe kwiaty oraz rośliny doniczkowe, resztki jedzenia bez mięsa, bez kości, bez tłuszczów zwierzęcych",
        "do_not_throw_away": "resztki mięsne, kości oraz tłuszcze zwierzęce, olej jadalny, ziemia i kamienie, odchody zwierząt",
        "color": "brown",
        "instructions": "Bioodpady stanowiące odpady komunalne umieszcza się w przeznaczonych na te odpady pojemnikach, luzem lub w certyfikowanych workach kompostowalnych oznaczonych odpowiednim symbolem. Sery, jogurty, masła i inne wyroby mleczne są produktem odzwierzęcym i nie wyrzucamy ich do odpadów BIO! Tak samo żywności, w której skład wchodzi jakikolwiek produkt pochodzenia zwierzęcego. Wyjątkiem są skorupki jajek!",
    }

    mixed = {
        "throw_away": "resztki mięsne oraz kości, mokry lub zabrudzony papier, zużyte materiały higieniczne, w tym pieluchy jednorazowe, żwirek z kuwet dla zwierząt, fajans, potłuczone szyby i lustra",
        "do_not_throw_away": "sprzęt elektryczny oraz elektroniczny, AGD, baterie i akumulatory, odpady budowlane i remontowe, odpady zielone, leki, chemikalia, tekstylia i odzież",
        "color": "black",
        "instructions": "Do pojemnika na odpady zmieszane wrzucaj odpady resztkowe, których nie udało się rozdzielić do pojemników na odpady segregowane lub czego nie można oddać do PSZOK-u lub MPSZOK-u.",
    }

    large = {
        "throw_away": "drzwi, stare meble (także rozłożone na części) oraz wyroby tapicerskie (np. fotele, wersalki, pufy), materace, zabawki dużych rozmiarów",
        "do_not_throw_away": "sprzęt elektryczny oraz elektroniczny, AGD (np.: stare pralki, lodówki), odpady budowlane i remontowe, wanny, umywalki, grzejniki, muszle toaletowe, ramy okienne, duże kartony, opony samochodowe, choinki",
        "color": "orange",
        "instructions": "Odpady wielkogabarytowe zostawiaj w wyznaczonym do tego miejscu, nie wcześniej niż na 72 godziny przed planowanym odbiorem. Zapytaj swojego administratora, gdzie znajdziesz miejsce przeznaczone do gromadzenia odpadów wielkogabarytowych.",
    }

    try:
        return {
            WarsawCategories.PAPER.value.lower(): paper,
            WarsawCategories.GLASS.value.lower(): glass,
            WarsawCategories.METAL_AND_PLASTIC.value.lower(): metal_and_plastic,
            WarsawCategories.ORGANIC.value.lower(): organic,
            WarsawCategories.MIXED.value.lower(): mixed,
            WarsawCategories.LARGE.value.lower(): large,
        }[category.lower()]
    except KeyError:
        return {}
