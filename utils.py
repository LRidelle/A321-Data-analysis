import pandas as pd

def add_to_list(target, data, key):

    if data[key]:
        target.append({
            "OF": data["of"],
            "DATE": data["date"],
            **data[key]
        })

def save_csv(data, path):
    # Si aucune donnée interprétée, ne pas écraser le CSV existant
    if not data:
        return

    df = pd.DataFrame(data)
    if df.empty:
        return

    if "OF" in df.columns and "DATE" in df.columns:
        df["DATE"] = pd.to_datetime(df["DATE"],format="mixed",dayfirst=True,errors="coerce")

        # Traite les doublons d'OF
        # A garder commenté pour suivre les remesures
        #df = (df.sort_values("DATE").drop_duplicates(subset="OF",keep="last"))

    df.to_csv(path,index=False,sep=";")