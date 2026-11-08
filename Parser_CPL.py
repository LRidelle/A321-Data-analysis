import pdfplumber
import re
from pathlib import Path

def analyse_pdf_cpl(pdf_path):
    filename = pdf_path.name.upper()

    is_free_state = "FREE STATE" in filename
    is_restrained = "AVEC POIDS" in filename

    result = {
        "of": None,
        "date": None,
        "skin free-state": {},
        "skin restrained": {},
        "stringers": {},
        "eeop": {},
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
            # SKIN
            elif "PROFIL MCTI-27-00-2006 - DETAIL CHORDS" in text or "PROFIL MCTI-27-00-2018 - DETAIL CHORDS" in text:
                if "#2" in text:
                    #print(f"\n========== PAGE {page_num} -> SKIN #2 IGNORE ==========")
                    continue

                if is_free_state:
                    #print(f"\n========== PAGE {page_num} -> SKIN FREE STATE DETECTED ==========")
                    result["skin free-state"].update(data_skin(page_num, page))
                    #print(result["skin free-state"])
                elif is_restrained:
                    #print(f"\n========== PAGE {page_num} -> SKIN RESTRAINED DETECTED ==========")
                    result["skin restrained"].update(data_skin(page_num, page))
                    #print(result["skin restrained"])

            # STRINGERS POSITION
            elif "ACTI-27-00-2021" in text or "ACTI-27-00-2023" in text:
                #print(f"\n========== PAGE {page_num} -> STRINGERS DETECTED ==========")
                result["stringers"].update(data_stringers(page_num, page))
                #print(result["stringers"])

            # EOP
            elif "ACTI-27-00-2020" in text or "ACTI-27-00-2022" in text:
                #print(f"\n========== PAGE {page_num} -> EEOP DETECTED ==========")
                result["eeop"].update(data_eeop(text, page_num))
                #print(result["eeop"])

    return result

def extract_header(text, result):
    m = re.search(r"OF:\s*(\d+)", text)
    if m:
        result["of"] = m.group(1)

    m = re.search(r"Date-Hour\s*:\s*(\d+/\d+/\d+)\s+(\d+:\d+:\d+)",text)
    if m:
        result["date"] = f"{m.group(1)} {m.group(2)}"

# --------------------------------
# Key characteristics for SKIN CPL
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

def data_stringers(page_num, page):
    #print(f"[STRINGERS] Analyse page {page_num}")

    data = {}
    for w in page.extract_words():
        if "ACTI-27-00-2021-PROS" not in w["text"] and "ACTI-27-00-2023-PROS" not in w["text"]:
            continue

        x = w["x0"]
        y = w["top"]

        text = page.crop((x - 5,y,x + 65,y + 35)).extract_text()
        if not text:
            continue

        numbers = re.findall(r"\d+\.\d+", text)
        if numbers:
            pos = w["text"].split("PROS")[-1]
            data[f"POS{pos}"] = float(numbers[-1])

    return data

def data_eeop(text, page_num):
    #print(f"[EEOP] Analyse page {page_num}")

    data = {}
    for line in text.splitlines()[4:7]:
        line = line.strip()
        numbers = re.findall(r"-?\d+\.\d+", line)
        if line.startswith("O "):
            data["ecart"] = float(numbers[1])

    return data

#if __name__ == '__main__':
    # SKIN CPL
    #pdf_test = Path("data_CPL\\E57573700005 01- OF50130082- AVEC POIDS AIRBUS REPORT 01.pdf")
    #pdf_test = Path("data_CPL\\E57573700005 01- OF50130082- FREE STATE AIRBUS REPORT 01.pdf")
    #pdf_test = Path("data_CPL\\E57573600005 01 - OF50096206 - AVEC POIDS - AIRBUS REPORT - 01.pdf")
    #pdf_test = Path("data_CPL\\E57573700005 01- OF50096509- AVEC POIDS AIRBUS REPORT 01.pdf")

    #pdf_test = Path("data_CPL\\E57573600005 01 - OF50115583 - AVEC POIDS - AIRBUS REPORT - 01.pdf")

    #pdf_test = Path("data_CPL\\E57573600004 00 - OF50130100 - AVEC POIDS - AIRBUS REPORT - 01.pdf")
    #pdf_test = Path("data_CPL\\E57573600004 00 - OF50130100 - FREE STATE - AIRBUS REPORT - 01.pdf")

    #contenu = analyse_pdf_cpl(pdf_test)
    #print(contenu)