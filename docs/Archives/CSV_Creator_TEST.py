import re

from pathlib import Path


#choice = input("Type CPL, PP , TE ou ALL ? ").upper()
choice = "ALL"
if choice == "CPL":
    folders = [Path(r"S:\DQ\Partage\Controle DIM QP\PPE MO CF90\Rapports PDF\2026\A321 FLAP\CPL")]
    #folders = [Path(r"D:\OneDrive\Ridellel\OneDrive - SONACA\Desktop\CF90\CPL")]
elif choice == "PP":
    folders = [Path(r"S:\DQ\Partage\Controle DIM QP\PPE MO CF90\Rapports PDF\2026\A321 FLAP")]
    #folders = [Path(r"D:\OneDrive\Ridellel\OneDrive - SONACA\Desktop\CF90")]
elif choice == "TE":
    folders = [Path(r"S:\DQ\Partage\Controle DIM QP\GPE LASER API\Metrolog\PDF\A321")]
    #folders = [Path(r"D:\OneDrive\Ridellel\OneDrive - SONACA\Desktop\LASER")]
elif choice == "ALL":
    folders = [Path(r"S:\DQ\Partage\Controle DIM QP\GPE LASER API\Metrolog\PDF\A321"),
               Path(r"S:\DQ\Partage\Controle DIM QP\PPE MO CF90\Rapports PDF\2026\A321 FLAP\CPL"),
               Path(r"S:\DQ\Partage\Controle DIM QP\PPE MO CF90\Rapports PDF\2026\A321 FLAP")]
    #folders = [Path(r"D:\OneDrive\Ridellel\OneDrive - SONACA\Desktop\LASER"),
    #           Path(r"D:\OneDrive\Ridellel\OneDrive - SONACA\Desktop\CF90"),
    #           Path(r"D:\OneDrive\Ridellel\OneDrive - SONACA\Desktop\CF90\CPL")]

pattern_skin = re.compile(r"^E\d{11}\s\d{2}\s*-\s*OF\s*\d{8}.*AIRBUS REPORT",re.IGNORECASE)
pattern_te = re.compile(r"^E5757371\d{4}\s\d{2}\s*-\s*OF\s*\d{8}",re.IGNORECASE)
exclude_te = (
    "ANALYSE",
    "LONGUEUR",
    "REFERENCE",
    "REFERENCES",
    "CNTL"
)

countLO_read, countLO_ignore = 0, 0
countUP_read, countUP_ignore = 0, 0
countTE_read, countTE_ignore = 0, 0

for pdf_folder in folders:
    for pdf in pdf_folder.glob("*.pdf"):
        filename = pdf.name.upper()

        is_te = (pattern_te.match(filename) and not any(word in filename for word in exclude_te))
        is_cpl = (pattern_skin.search(filename) and filename.startswith(("E57573600", "E57573700")))
        is_pp = (pattern_skin.search(filename) and filename.startswith(("E57573230", "E57573250")))

        if not (is_te or is_cpl or is_pp):
            print(f"Rapport ignoré :        {pdf.name}")
            countLO_ignore += filename.startswith("E57573600")
            countUP_ignore += filename.startswith("E57573700")
            countTE_ignore += filename.startswith("E57573710")
            continue
        else:
            # print(f"Traitement du rapport : {pdf.name}")
            countLO_read += filename.startswith("E57573600")
            countUP_read += filename.startswith("E57573700")
            countTE_read += filename.startswith("E57573710")

if choice == "CPL" or choice == "PP":
    print(f"Rapports UPPER {choice} analysé avec succès :  {countUP_read} lu, {countUP_ignore} ignoré")
    print(f"Rapports LOWER {choice} analysé avec succès :  {countLO_read} lu, {countLO_ignore} ignoré")
elif choice == "TE":
    print(f"Rapports {choice} analysé avec succès :  {countTE_read} lu, {countTE_ignore} ignoré")