import re

from config import (CPL_FOLDER,PP_FOLDER,TE_FOLDER)
from utils import *
from pathlib import Path
from Parser_CPL import analyse_pdf_cpl
from Parser_PP import analyse_pdf_pp
from Parser_TE import analyse_pdf_te

# -----------------------
# TODO
# 1) faire un truc qui va checker dans les data_pp et data_cpl tt seul (mieux un GUI)
# 2) les csv pour le patern de trous des lower pp et holes TE
# 3) des commentaire au dessus de chaque fonction pour dire ce qu'ells retourn comme valeur (ecart, dX, dY, dZ, ...)
# -----------------------
choice = input("Type CPL, PP, TE ou ALL ? ").upper()
debug = True
if debug:
    if choice == "CPL":
        folders = [Path("data_CPL")]
    elif choice == "PP":
        folders = [Path("data_PP")]
    elif choice == "TE":
        folders = [Path(r"D:\OneDrive\Ridellel\OneDrive - SONACA\Desktop\LASER")]#Path("data_TE")]
    elif choice == "ALL":
        folders = [Path("data_CPL"),
                   Path("data_PP"),
                   Path("data_TE")]
else:
    if choice == "CPL":
        folders = [CPL_FOLDER]
    elif choice == "PP":
        folders = [PP_FOLDER]
    elif choice == "TE":
        folders = [TE_FOLDER]
    elif choice == "ALL":
        folders = [CPL_FOLDER, PP_FOLDER, TE_FOLDER,]
    else:
        raise ValueError("Choix invalide : CPL, PP, TE ou ALL")

# UPPER CPL (E57573700...)
upper_cpl_skin_free_state = []
upper_cpl_skin_restrained = []
upper_cpl_stringers = []
upper_cpl_eeop = []

# LOWER CPL (E57573600...)
lower_cpl_skin_free_state = []
lower_cpl_skin_restrained = []
lower_cpl_stringers = []
lower_cpl_eeop = []

# UPPER PP (E57573250...)
upper_skin_free_state = []
upper_skin_restrained = []
upper_eeop = []
upper_holes_22_5 = []
upper_holes_da = []
upper_holes_cos = []
upper_holes_eng = []

# LOWER PP (E57573230...)
lower_skin_free_state = []
lower_skin_restrained = []
lower_eeop = []
lower_holes_11 = []
lower_holes_16 = []
lower_holes_6_5 = []
lower_holes_11_3 = []
lower_holes_da = []
lower_holes_cos = []
lower_holes_eng = []

# TE (E57573710...)
skin_upper = []
skin_lower = []
eeop_upper = []
eeop_lower = []
eeop_inbd = []
eeop_outbd = []
eeop_te = []
holes_upper = []
holes_lower = []


pattern_skin = re.compile(r"^E\d{11}\s\d{2}\s*-\s*OF\s*\d{8}.*AIRBUS REPORT", re.IGNORECASE)
pattern_te = re.compile(r"^E57573710\d{3}\s\d{2}\s*-\s*OF\s*\d{8}",re.IGNORECASE)
exclude_te = ("ANALYSE","LONGUEUR","REFERENCE","REFERENCES","CNTL")

countLO_read, countLO_ignore = 0, 0
countUP_read, countUP_ignore = 0, 0
countTE_read, countTE_ignore = 0, 0

for pdf_folder in folders:
    for pdf in pdf_folder.glob("*.pdf"):
        filename = pdf.name.upper()

        is_te = (pattern_te.match(filename) and not any(word in filename for word in exclude_te))
        is_cpl = (pattern_skin.search(filename) and filename.startswith(("E57573600", "E57573700")))
        is_pp = (pattern_skin.search(filename) and filename.startswith(("E57573230", "E57573250")))

        # =====================================================
        # 1 - Verifier si le titre de fichier est à interpréter
        # =====================================================
        if not (is_te or is_cpl or is_pp):
            print(f"Rapport ignoré :        {pdf.name}")
            countLO_ignore += filename.startswith("E57573600")
            countUP_ignore += filename.startswith("E57573700")
            countTE_ignore += filename.startswith("E57573710")
            continue
        else:
            print(f"Traitement du rapport : {pdf.name}")
            countLO_read += filename.startswith("E57573600")
            countUP_read += filename.startswith("E57573700")
            countTE_read += filename.startswith("E57573710")

        # =====================================================
        # 2 - Choisir le bon parser selon la pièce
        # =====================================================
        is_free_state = "FREE STATE" in filename

        if is_cpl:
            data = analyse_pdf_cpl(pdf)

            # Type de pièce
            if filename.startswith("E57573700"):
                skin_free_state = upper_cpl_skin_free_state
                skin_restrained = upper_cpl_skin_restrained
                stringers = upper_cpl_stringers
                eeop = upper_cpl_eeop

            elif filename.startswith("E57573600"):
                skin_free_state = lower_cpl_skin_free_state
                skin_restrained = lower_cpl_skin_restrained
                stringers = lower_cpl_stringers
                eeop = lower_cpl_eeop

            else:
                print(f"Type CPL inconnu : {pdf.name}")
                continue

            if is_free_state:
                add_to_list(skin_free_state, data, "skin free-state")
            else:
                add_to_list(skin_restrained, data, "skin restrained")
                add_to_list(stringers, data, "stringers")
                add_to_list(eeop, data, "eeop")

        elif is_pp:
            data = analyse_pdf_pp(pdf)
            print("PP")

            # Type de pièce
            if filename.startswith("E57573230"):
                skin_free_state = lower_skin_free_state
                skin_restrained = lower_skin_restrained
                eeop = lower_eeop
                holes_da = lower_holes_da
                holes_cos = lower_holes_cos
                holes_eng = lower_holes_eng
                holes_11 = lower_holes_11
                holes_16 = lower_holes_16
                holes_6_5 = lower_holes_6_5
                holes_11_3 = lower_holes_11_3

            elif filename.startswith("E57573250"):
                skin_free_state = upper_skin_free_state
                skin_restrained = upper_skin_restrained
                eeop = upper_eeop
                holes_da = upper_holes_da
                holes_cos = upper_holes_cos
                holes_eng = upper_holes_eng
                holes_22_5 = upper_holes_22_5

            else:
                print(f"Type PP inconnu : {pdf.name}")
                continue

            if is_free_state:
                add_to_list(skin_free_state, data, "skin free-state")
            else:
                add_to_list(skin_restrained, data, "skin restrained")
                add_to_list(eeop, data, "eeop")

                add_to_list(holes_da, data, "holes_da")
                add_to_list(holes_cos, data, "holes_cos")
                add_to_list(holes_eng, data, "holes_eng")

                add_to_list(upper_holes_22_5, data, "holes_22_5")

                add_to_list(lower_holes_11, data, "holes_11")
                add_to_list(lower_holes_16, data, "holes_16")
                add_to_list(lower_holes_6_5, data, "holes_6_5")
                add_to_list(lower_holes_11_3, data, "holes_11_3")

        elif is_te:
            data = analyse_pdf_te(pdf)

            add_to_list(skin_upper, data,  "skin_upper")
            add_to_list(skin_lower, data,  "skin_lower")
            add_to_list(eeop_upper, data,  "eeop_upper")
            add_to_list(eeop_lower, data,  "eeop_lower")
            add_to_list(eeop_inbd, data,   "eeop_inbd")
            add_to_list(eeop_outbd, data,  "eeop_outbd")
            add_to_list(eeop_te, data,     "eeop_te")
            add_to_list(holes_upper, data, "holes_upper")
            add_to_list(holes_lower, data, "holes_lower")

# CREATION OF CSV
for folder in ("Export UPPER CPL", "Export LOWER CPL", "Export UPPER PP", "Export LOWER PP", "Export TE"):
    Path(folder).mkdir(exist_ok=True)

# -----------------------
# TE
# -----------------------
save_csv(skin_upper,  "Export TE/Skin_Upper.csv")
save_csv(skin_lower,  "Export TE/Skin_Lower.csv")
save_csv(eeop_upper,  "Export TE/EEOP_Upper.csv")
save_csv(eeop_lower,  "Export TE/EEOP_Lower.csv")
save_csv(eeop_inbd,   "Export TE/EEOP_INBD.csv")
save_csv(eeop_outbd,  "Export TE/EEOP_OUTBD.csv")
save_csv(eeop_te,     "Export TE/EEOP_TE.csv")
save_csv(holes_upper, "Export TE/Holes_Upper.csv")
save_csv(holes_lower, "Export TE/Holes_Lower.csv")

# -----------------------
# UPPER CPL
# -----------------------
save_csv(upper_cpl_skin_free_state, "Export UPPER CPL/Vue_Profile_FreeState.csv")
save_csv(upper_cpl_skin_restrained, "Export UPPER CPL/Vue_Profile_Restrained.csv")
save_csv(upper_cpl_stringers,       "Export UPPER CPL/Vue_Stringers_Position.csv")
save_csv(upper_cpl_eeop,            "Export UPPER CPL/Vue_EEOP.csv")

# -----------------------
# LOWER CPL
# -----------------------
save_csv(lower_cpl_skin_free_state, "Export LOWER CPL/Vue_Profile_FreeState.csv")
save_csv(lower_cpl_skin_restrained, "Export LOWER CPL/Vue_Profile_Restrained.csv")
save_csv(lower_cpl_stringers,       "Export LOWER CPL/Vue_Stringers_Position.csv")
save_csv(lower_cpl_eeop,            "Export LOWER CPL/Vue_EEOP.csv")

# -----------------------
# UPPER PP
# -----------------------
save_csv(upper_skin_free_state, "Export UPPER PP/Vue_Profile_FreeState.csv")
save_csv(upper_skin_restrained, "Export UPPER PP/Vue_Profile_Restrained.csv")
save_csv(upper_eeop,            "Export UPPER PP/Vue_EEOP.csv")

save_csv(upper_holes_22_5, "Export UPPER PP/Vue_Holes_22_5.csv")
save_csv(upper_holes_da,   "Export UPPER PP/Vue_Holes_DA.csv")
save_csv(upper_holes_cos,  "Export UPPER PP/Vue_Holes_COS.csv")
save_csv(upper_holes_eng,  "Export UPPER PP/Vue_Holes_ENG.csv")

# -----------------------
# LOWER PP
# -----------------------
save_csv(lower_skin_free_state, "Export LOWER PP/Vue_Profile_FreeState.csv")
save_csv(lower_skin_restrained, "Export LOWER PP/Vue_Profile_Restrained.csv")
save_csv(lower_eeop,            "Export LOWER PP/Vue_EEOP.csv")

save_csv(lower_holes_11,   "Export LOWER PP/Vue_Holes_11.csv")
save_csv(lower_holes_16,   "Export LOWER PP/Vue_Holes_16.csv")
save_csv(lower_holes_6_5,  "Export LOWER PP/Vue_Holes_6_5.csv")
save_csv(lower_holes_11_3, "Export LOWER PP/Vue_Holes_11_3.csv")
save_csv(lower_holes_da,   "Export LOWER PP/Vue_Holes_DA.csv")
save_csv(lower_holes_cos,  "Export LOWER PP/Vue_Holes_COS.csv")
save_csv(lower_holes_eng,  "Export LOWER PP/Vue_Holes_ENG.csv")

if choice == "CPL" or choice == "PP":
    print(f"Rapports UPPER {choice} analysé avec succès :  {countUP_read} lu, {countUP_ignore} ignoré")
    print(f"Rapports LOWER {choice} analysé avec succès :  {countLO_read} lu, {countLO_ignore} ignoré")
elif choice == "TE":
    print(f"Rapports {choice} analysé avec succès :  {countTE_read} lu, {countTE_ignore} ignoré")
elif choice == "ALL":
    print(f"Rapports {choice} analysé avec succès :  {countTE_read+countUP_read+countLO_read} lu, {countTE_ignore+countUP_ignore+countLO_ignore} ignoré")
print("CSV générés avec succès")