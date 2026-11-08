import pdfplumber
import re
from pathlib import Path

def analyse_pdf_pp(pdf_path):
    filename = pdf_path.name.upper()

    is_free_state = "FREE STATE" in filename
    is_restrained = "AVEC POIDS" in filename

    result = {
        "of": None,
        "date": None,
        "skin free-state": {},
        "skin restrained": {},
        "eeop": {},
        "holes_22_5": {}, #diam 22.5 UPPER
        "holes_11": {},   #diam 11 LOWER
        "holes_16": {},   #diam 16 LOWER
        "holes_6_5": {},  #diam 6.5 LOWER
        "holes_11_3": {}, #diam 11.3 LOWER
        "holes_da": {},
        "holes_cos": {},
        "holes_eng": {}
    }

    with pdfplumber.open(pdf_path) as pdf:

        for page_num, page in enumerate(pdf.pages, start=1):

            text = page.extract_text() or ""

            #print(f"\n========== PAGE {page_num} ==========")

            # Extraction OF / Date
            if result["of"] is None:
                #print(f"\n========== PAGE {page_num} -> HEADER DETECTED ==========")
                extract_header(text, result)

            # Routage selon le titre de page
            elif "MCTI-27-00-2006" in text or "MCTI-27-00-2018" in text:
                if "#2" in text:
                    #print(f"\n========== PAGE {page_num} -> SKIN #2 IGNORE ==========")
                    continue

                if is_free_state:
                    #print(f"\n========== PAGE {page_num} -> SKIN FREE STATE DETECTED ==========")
                    # noinspection PyUnresolvedReferences
                    result["skin free-state"].update(data_skin(page_num, page))
                    #print(result["skin free-state"])
                elif is_restrained:
                    #print(f"\n========== PAGE {page_num} -> SKIN RESTRAINED DETECTED ==========")
                    result["skin restrained"].update(data_skin(page_num, page))
                    #print(result["skin restrained"])

            elif "EOP" in text and "ALIGNEMENT PIECE" not in text:
                #print(f"\n========== PAGE {page_num} -> EOP DETECTED ==========")
                result["eeop"].update(data_eeop(page_num, page))
                #print(result["eeop"])

            elif "Ø22.5" in text:
                #print(f"\n========== PAGE {page_num} -> HOLES Ø22.5 DETECTED ==========")
                result["holes_22_5"].update(data_holes_22_5(page_num, page))
                #print(result["holes_22_5"])

            #TODO
            elif "Ø11" in text and "Ø16" in text and "Ø6.5" in text :
                #print(f"\n========== PAGE {page_num} -> HOLES Ø11, Ø16, Ø6.5 DETECTED ==========")
                result["holes_22_5"].update(data_holes_11(page_num, page))
                result["holes_16"].update(data_holes_16(page_num, page))
                result["holes_6_5"].update(data_holes_6_5(page_num, page))
                #print(result[""])

            elif "Ø11.3" in text:
                #print(f"\n========== PAGE {page_num} -> HOLES Ø11.3 DETECTED ==========")
                result["holes_11_3"].update(data_holes_11_3(page_num, page))
                #print(result["holes_11_3"])

            elif "DA Holes" in text:
                #print(f"\n========== PAGE {page_num} -> HOLES DA DETECTED ==========")
                result["holes_da"].update(data_holes_da(page_num, page))
                #print(result["holes_da"])

            elif "2.5 CoS" in text:
                #print(f"\n========== PAGE {page_num} -> HOLES COS DETECTED ==========")
                result["holes_cos"].update(data_holes_cos(page_num, page))
                #print(result["holes_cos"])

            elif "Engineering Holes" in text:
                #print(f"\n========== PAGE {page_num} -> HOLES ENG DETECTED ==========")
                result["holes_eng"].update(data_holes_eng(page_num, page))
                #print(result["holes_eng"])

    return result

def extract_header(text, result):
    m = re.search(r"OF:\s*(\d+)", text)
    if m:
        result["of"] = m.group(1)

    m = re.search(r"Date-Hour\s*:\s*(\d+/\d+/\d+)\s+(\d+:\d+:\d+)",text)
    if m:
        result["date"] = f"{m.group(1)} {m.group(2)}"

# --------------------------------
# Key characteristics for SKIN PP
# --------------------------------
def data_skin(page_num, page):
    #print(f"[SKIN] Analyse page {page_num}")

    data = {}
    for w in page.extract_words():
        if "Etat" in w["text"]:

            x = w["x0"]
            y = w["bottom"]

            text = page.crop((x - 45, y - 25, x + 40, y + 35)).extract_text()
            if not text:
                continue

            for line in text.splitlines():
                line = line.strip()
                numbers = re.findall(r"-?\d+\.\d+", line)

                if line.startswith("O "):
                    data["ecart"] = float(numbers[-1])

                elif line.startswith("Max."):
                    data["tol_max"] = float(numbers[-1])

                elif line.startswith("Min."):
                    data["tol_min"] = float(numbers[-1])

            break
    return data

def data_eeop(page_num, page):
    #print(f"[EOP] Analyse page {page_num}")

    data = {}
    for w in page.extract_words():
        #print(w["text"])
        if "PROS2" in w["text"]:
            x = w["x0"]
            y = w["top"]

            text = page.crop((x - 5, y, x + 50, y + 50)).extract_text()
            if not text:
                continue

            for line in text.splitlines():
                line = line.strip()
                numbers = re.findall(r"-?\d+\.\d+", line)

                if line.startswith("O "):
                    data["ecart"] = float(numbers[-1])

                elif line.startswith("Max."):
                    data["tol_max"] = float(numbers[-1])

                elif line.startswith("Min."):
                    data["tol_min"] = float(numbers[-1])

        elif "V.G" in w["text"]:
            x = w["x0"]
            y = w["bottom"]

            text = page.crop((x, y - 18, x + 45, y)).extract_text()
            if not text:
                continue

            m = re.search(r"(EOP-\d+(?:-\d+)?)", text)
            if not m:
                continue
            pos = m.group(1)

            numbers = re.findall(r"\d+\.\d+", text)
            if numbers:
                data[pos] = float(numbers[-1])

    return data

def data_holes_22_5(page_num, page):
    #print(f"[HOLES 22.5mm] Analyse page {page_num}")

    data = {}
    for w in page.extract_words():
        if "Ø22.5-" in w["text"] and "LOCA" not in w["text"]:
            x = w["x0"]
            y = w["top"]

            text = page.crop((x - 5, y, x + 50, y + 30)).extract_text()
            if not text:
                continue

            for line in text.splitlines():
                line = line.strip()
                numbers = re.findall(r"-?\d+\.\d+", line)

                if line.startswith("X "):
                    pos = w["text"].split("Ø22.5-")[-1]
                    data[f"{pos}-dX"] = float(numbers[-1])

                elif line.startswith("Y "):
                    pos = w["text"].split("Ø22.5-")[-1]
                    data[f"{pos}-dY"] = float(numbers[-1])

                elif line.startswith("Z "):
                    pos = w["text"].split("Ø22.5-")[-1]
                    data[f"{pos}-dZ"] = float(numbers[-1])

        elif "LOCAØ22.5-" in w["text"]:
            x = w["x0"]
            y = w["top"]

            text = page.crop((x - 5, y, x + 50, y + 35)).extract_text()
            if not text:
                continue

            numbers = re.findall(r"\d+\.\d+", text)
            if numbers:
                pos = w["text"].split("LOCAØ22.5-")[-1]
                data[f"{pos}-ecart"] = float(numbers[-1])

    return data

#TODO
def data_holes_11(page_num, page):
    #print(f"[HOLES 11mm] Analyse page {page_num}")

    data = {}
    return data

#TODO
def data_holes_16(page_num, page):
    #print(f"[HOLES 16mm] Analyse page {page_num}")

    data = {}
    return data

#TODO
def data_holes_6_5(page_num, page):
    #print(f"[HOLES 6.5mm] Analyse page {page_num}")

    data = {}
    return data

#TODO TO END
def data_holes_11_3(page_num, page):
    #print(f"[HOLES 11.3mm] Analyse page {page_num}")

    data = {}
    for w in page.extract_words():
        if "Ø11.3-" in w["text"] and "LOCA" not in w["text"]:
            x = w["x0"]
            y = w["top"]

            text = page.crop((x - 5, y, x + 20, y + 26)).extract_text()
            if not text:
                continue

            for line in text.splitlines():
                line = line.strip()
                numbers = re.findall(r"-?\d+\.\d+", line)

                if line.startswith("X "):
                    pos = w["text"].split("Ø22.5-")[-1]
                    data[f"{pos}-dX"] = float(numbers[-1])

                elif line.startswith("Y "):
                    pos = w["text"].split("Ø22.5-")[-1]
                    data[f"{pos}-dY"] = float(numbers[-1])

                elif line.startswith("Z "):
                    pos = w["text"].split("Ø22.5-")[-1]
                    data[f"{pos}-dZ"] = float(numbers[-1])

        elif "LOCAØ22.5-" in w["text"]: #ERREUR A GERER CAR LOCAX n'est pas identique a Ø11.3-Y dans le rapport (X != Y)
            x = w["x0"]
            y = w["top"]

            text = page.crop((x - 5, y, x + 50, y + 35)).extract_text()
            if not text:
                continue

            numbers = re.findall(r"\d+\.\d+", text)
            if numbers:
                pos = w["text"].split("LOCAØ22.5-")[-1]
                data[f"{pos}-ecart"] = float(numbers[-1])

    return data

def data_holes_da(page_num, page):
    #print(f"[HOLES DA] Analyse page {page_num}")

    data = {}
    mapping = { #DA1 is the INBOARD HOLES, DA2 is the OUTBOARD one
        "LOCAØ3.2-1": "DA1",
        "LOCAØ3.2-2": "DA2",
        "LOCA30": "DA1",
        "LOCA31": "DA2"
    }
    for w in page.extract_words():
        if w["text"] not in mapping:
            continue

        x = w["x0"]
        y = w["top"]

        text = page.crop((x - 5, y, x + 35, y + 32)).extract_text()
        if not text:
            continue

        numbers = re.findall(r"\d+\.\d+", text)
        if numbers:
            data[mapping[w["text"]]] = float(numbers[-1])

    return data

def data_holes_cos(page_num, page):
    #print(f"[HOLES COS] Analyse page {page_num}")

    data = {}
    for w in page.extract_words():
        if "Etat" in w["text"]:
            x = w["x0"]
            y = w["bottom"]

            text = page.crop((x - 25, y - 20, x + 25, y + 5)).extract_text()
            if not text:
                continue

            m = re.search(r"LOCAØ2\.5-(\d+)", text)
            if not m:
                continue
            pos = m.group(1)

            numbers = re.findall(r"\d+\.\d+", text)
            #print(f"{pos}-{numbers}")
            if numbers:
                data[pos] = float(numbers[-1])

        elif w["text"] == "D":
            x = w["x0"]
            y = w["bottom"]

            text = page.crop((x, y - 30, x + 38, y)).extract_text()
            if not text:
                continue

            m = re.search(r"LOCAØ2\.5-(\d+)", text)
            if not m or m.group(1) in data:
                continue
            pos = m.group(1)

            numbers = re.findall(r"\d+\.\d+", text)
            #print(f"{pos}-{numbers}")
            if numbers:
                data[pos] = float(numbers[-1])

    return data

def data_holes_eng(page_num, page):
    #print(f"[HOLES ENG] Analyse page {page_num}")

    data = {}
    for w in page.extract_words():
        if w["text"]=="D":
            x = w["x0"]
            y = w["bottom"]

            text = page.crop((x, y-30, x + 35, y)).extract_text()
            if not text:
                continue

            m = re.search(r"LOCAØ2\.5-(\d+)", text)
            if not m:
                continue
            pos = m.group(1)

            numbers = re.findall(r"\d+\.\d+", text)
            if numbers:
                data[f"{pos}-ecart"] = float(numbers[-1])

    return data

#if __name__ == '__main__':
    # SKIN PP
    # UPPER LH
    #pdf_test = Path("data_PP\\E57573250202 01 - OF50128585 - AVEC POIDS - AIRBUS REPORT - NEW ALIGNMENT - 01.pdf")
    #pdf_test = Path("data_PP\\E57573250202 01 - OF50128585 - FREE STATE - AIRBUS REPORT - 01.pdf")
    # UPPER RH
    #pdf_test = Path("data_PP\\E57573250203 01 - OF50095661 - AVEC POIDS - AIRBUS REPORT - NEW ALIGNMENT - 01.pdf")

    # LOWER LH
    #pdf_test = Path("data_PP\\E57573230202 01 - OF50106924 - AVEC POIDS - AIRBUS REPORT - NEW ALIGNMENT - 01.pdf")
    #pdf_test = Path("data_PP\\E57573230202 01 - OF50106924 - FREE STATE - AIRBUS REPORT - 01.pdf")

    #contenu = analyse_pdf_pp(pdf_test)
    #print(contenu)
