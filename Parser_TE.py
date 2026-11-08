import pdfplumber
import re
from pathlib import Path

def analyse_pdf_te(pdf_path):

    result = {
        "of": None,
        "date": None,
        "skin_upper": {},
        "skin_lower": {},
        "eeop_upper": {},
        "eeop_lower": {},
        "eeop_inbd": {},
        "eeop_outbd": {},
        "eeop_te": {},
        "holes_upper": {},
        "holes_lower": {}
    }

    with pdfplumber.open(pdf_path) as pdf:

        for page_num, page in enumerate(pdf.pages, start=1):

            text = page.extract_text() or ""

            #print(f"\n========== PAGE {page_num} ==========")

            # Extraction OF / Date
            if result["of"] is None:
                # print(f"\n========== PAGE {page_num} -> HEADER DETECTED ==========")
                extract_header(text, result)

            # Routage selon le titre de page
            # SKIN UPPER
            elif "ACTI-27-00-2030" in text :
                # print(f"\n========== PAGE {page_num} -> SKIN DETECTED ==========")
                result["skin_upper"].update(data_skin(page_num, page))
                # print(result["skin_upper"])

            # SKIN LOWER
            elif "ACTI-27-00-2031" in text:
                # print(f"\n========== PAGE {page_num} -> SKIN DETECTED ==========")
                result["skin_lower"].update(data_skin(page_num, page))
                # print(result["skin_lower"])

            # EOP UPPER & LOWER
            elif "ACTI-27-00-2028" in text or "ACTI-27-00-2029" in text:
                # print(f"\n========== PAGE {page_num} -> EEOP UP & LO DETECTED ==========")
                eeop_up, eeop_lo = data_eeop_up_lo(page_num, page)
                result["eeop_upper"].update(eeop_up)
                result["eeop_lower"].update(eeop_lo)
                # print(result["eeop_upper"])
                # print(result["eeop_lower"])

            # EOP OUTBD & INBD
            elif "ACTI-27-00-2024" in text or "ACTI-27-00-2025" in text:
                # print(f"\n========== PAGE {page_num} -> EEOP INB & OUTB DETECTED ==========")
                eeop_indb, eeop_outbd = data_eeop_in_out(page_num, page)
                result["eeop_inbd"].update(eeop_indb)
                result["eeop_outbd"].update(eeop_outbd)
                # print(result["eeop_inbd"])
                # print(result["eeop_outbd"])

            # EOP TE
            elif "ACTI-27-00-2026" in text:
                # print(f"\n========== PAGE {page_num} -> EEOP TE DETECTED ==========")
                result["eeop_te"].update(data_eeop_te(page_num, page))
                # print(result["eeop_te"])

            # HOLES UPPER
            elif "HOLES UPPER" in text:
                # print(f"\n========== PAGE {page_num} -> HOLES UPPER DETECTED ==========")
                result["holes_upper"].update(data_holes(page_num, page))
                # print(result["eeop"])

            # HOLES LOWER
            elif "HOLES LOWER" in text or page_num == 15:
                # print(f"\n========== PAGE {page_num} -> HOLES LOWER DETECTED ==========")
                result["holes_lower"].update(data_holes(page_num, page))
                # print(result["holes_lower"])

            # SECTIONS DES SKIN
            elif re.search(r"\bV\s*\d+\b", text) and not "SECTIONS" in text:
                width = page.width
                height = page.height

                #print(f"\n========== PAGE {page_num} -> SECTION DETECTED ==========")
                page_upp = page.crop((10, 170, width / 2, height-10))
                result["skin_upper"].update(data_sect(page_num, page_upp))
                # print(result["skin_upper"])

                # print(f"\n========== PAGE {page_num} -> SECTION DETECTED ==========")
                page_lo = page.crop((width / 2, 190, width, height-10))
                result["skin_lower"].update(data_sect(page_num, page_lo))
                # print(result["skin_lower"])


    return result

def extract_header(text, result):
    m = re.search(r"O/F\s*:\s*(\d+)", text)
    if m:
        result["of"] = m.group(1)

    m = re.search(r"Date-heure\s*:\s*(\d+-\d+-\d+)\s+(\d+:\d+:\d+)",text)
    if m:
        result["date"] = f"{m.group(1)} {m.group(2)}"

# --------------------------------
# Key characteristics for TE
# --------------------------------
def data_sect(page_num, page):
    #print(f"[SECTION] Analyse page {page_num}")

    data = {}

    for w in page.extract_text_lines():
        if "V" in w["text"] and "V.G." not in w["text"]:# and "X4 V18 SP2" not in w["text"]:
            x = w["x0"]
            y = w["top"]

            text = page.crop((x - 5, y, x + 50, y + 20)).extract_text()
            if not text:
                continue

            for line in text.splitlines():
                line = line.strip()
                numbers = re.findall(r"-?\d+\.\d+", line)

                if line.startswith("V "):
                    pos = line.split()[1]
                elif line.startswith("V.G."):
                    data[f"V{pos}"] = float(numbers[-1])

    return data

def data_skin(page_num, page):
    #print(f"[SKIN] Analyse page {page_num}")

    data = {}

    for w in page.extract_words():
        if "ACTI-27-00-203" in w["text"]:
            x = w["x0"]
            y = w["top"]

            text = page.crop((x - 20, y, x + 35, y + 45)).extract_text()
            if not text:
                continue

            for line in text.splitlines():
                line = line.strip()
                numbers = re.findall(r"-?\d+\.\d{2,3}", line)

                if line.startswith("O "):
                    data["ecart"] = float(numbers[-1])
                elif line.startswith("Max."):
                    data["tol_max"] = float(numbers[-1])
                elif line.startswith("Min."):
                    data["tol_min"] = float(numbers[-1])

    return data

def data_eeop_up_lo(page_num, page):
    #print(f"[EEOP UP & LO] Analyse page {page_num}")

    data_up, data_lo = {}, {}

    for w in page.extract_words():
        if "ACTI-27-00-2028" in w["text"]:
            x = w["x0"]
            y = w["top"]

            text = page.crop((x - 20, y, x + 38, y + 45)).extract_text()
            if not text:
                continue

            for line in text.splitlines():
                line = line.strip()
                numbers = re.findall(r"-?\d+\.\d+", line)

                if line.startswith("O "):
                    data_up["ecart"] = float(numbers[-1])

                elif line.startswith("Max."):
                    data_up["tol_max"] = float(numbers[-1])

                elif line.startswith("Min."):
                    data_up["tol_min"] = float(numbers[-1])

        elif "ACTI-27-00-2029" in w["text"]:
            x = w["x0"]
            y = w["top"]

            text = page.crop((x - 20, y, x + 38, y + 45)).extract_text()
            if not text:
                continue

            for line in text.splitlines():
                line = line.strip()
                numbers = re.findall(r"-?\d+\.\d+", line)

                if line.startswith("O "):
                    data_lo["ecart"] = float(numbers[-1])

                elif line.startswith("Max."):
                    data_lo["tol_max"] = float(numbers[-1])

                elif line.startswith("Min."):
                    data_lo["tol_min"] = float(numbers[-1])

    return data_up, data_lo

def data_eeop_in_out(page_num, page):
    #print(f"[EEOP INBD & OUTB] Analyse page {page_num}")

    data_inbd, data_outbd = {}, {}

    for w in page.extract_words():
        if "ACTI-27-00-2025" in w["text"]:
            x = w["x0"]
            y = w["top"]

            text = page.crop((x - 20, y, x + 38, y + 45)).extract_text()
            if not text:
                continue

            for line in text.splitlines():
                line = line.strip()
                numbers = re.findall(r"-?\d+\.\d+", line)

                if line.startswith("O "):
                    data_inbd["ecart"] = float(numbers[-1])

                elif line.startswith("Max."):
                    data_inbd["tol_max"] = float(numbers[-1])

                elif line.startswith("Min."):
                    data_inbd["tol_min"] = float(numbers[-1])

        elif "ACTI-27-00-2024" in w["text"]:
            x = w["x0"]
            y = w["top"]

            text = page.crop((x - 20, y, x + 38, y + 45)).extract_text()
            if not text:
                continue

            for line in text.splitlines():
                line = line.strip()
                numbers = re.findall(r"-?\d+\.\d+", line)

                if line.startswith("O "):
                    data_outbd["ecart"] = float(numbers[-1])

                elif line.startswith("Max."):
                    data_outbd["tol_max"] = float(numbers[-1])

                elif line.startswith("Min."):
                    data_outbd["tol_min"] = float(numbers[-1])

    return data_inbd, data_outbd

def data_eeop_te(page_num, page):
    #print(f"[EEOP TE] Analyse page {page_num}")

    data = {}

    for w in page.extract_words():
        if "ACTI-27-00-2026" in w["text"]:
            x = w["x0"]
            y = w["top"]

            text = page.crop((x - 20, y, x + 38, y + 45)).extract_text()
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

    return data

# Grosse galère mais utiliser un reader pour faire de l OCR en json puis parser ces json
def data_holes(page_num, page):
    #print(f"[HOLES] Analyse page {page_num}")

    data = {}
    r"""
    crop = page.crop((50, 180, page.width-30, page.height-220))
    img = crop.to_image(resolution=300).original
    img.save("holes_upper.png")

    results = reader.readtext(np.array(img),detail=1)

    holes = {}
    for bbox, text, conf in results:

        m = re.search(r"HOLE\s*(\d+)", text.upper())

        if m:
            hole_id = int(m.group(1))

            holes[hole_id] = {"x": bbox[0][0],"y": bbox[0][1],"values": []}

    for bbox, text, conf in results:

        nums = re.findall(r"-?\d+\.\d+", text)

        if not nums:
            continue

        x = bbox[0][0]
        y = bbox[0][1]

        closest_hole = min(holes,key=lambda h: abs(x - holes[h]["x"]))

        holes[closest_hole]["values"].extend(map(float, nums))

    data = {}

    for hole_id, hole_data in holes.items():

        values = hole_data["values"]

        if not values:
            continue

        data[hole_id] = {"max_dev": max(values, key=abs)}
        print(f"{hole_id} : {values}")
    
    results = reader.readtext(
        np.array(img),
        detail=1
    )

    for bbox, text, conf in results:
        print(
            round(bbox[0][0]),
            round(bbox[0][1]),
            text
        )
    """
    #for w in page.extract_words():
        #print(w["text"])
        #print(page.extract_text())

    return data


if __name__ == '__main__':
    # TE LH
    #pdf_test = Path("data_TE\\E57573710004 00 - OF 50115603.pdf")
    #pdf_test = Path("data_TE\\E57573710004 00 - OF 50115603.pdf")

    # TE RH
    #pdf_test = Path("data_TE\\E57573710004 00 - OF 50115603.pdf")
    #pdf_test = Path("data_TE\\E57573710004 00 - OF 50115603.pdf")
    #pdf_test = Path("data_TE\\E57573710000 00 - OF 115580689300001 - FREE STATE.pdf")
    pdf_test = Path("data_TE\\E57573710000 00 - OF50021514.pdf")

    contenu = analyse_pdf_te(pdf_test)
    #print(contenu)