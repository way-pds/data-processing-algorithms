import pandas as pd
from pathlib import Path


# ------------------------------------------------
# CONFIGURAÇÃO DOS SENSORES
# ------------------------------------------------

EXPECTED_FILES = {
    "accelerometer": 1,
    "ppg": 1,
    "bia": 2,
    "ecg": 2,
}

EXPECTED_LINES = {
    "accelerometer": 42000,
    "bia1": 150,
    "bia2": 150,
    "ecg1": 1500,
    "ecg2": 1500,
    "ppg": 85000,
}


# ------------------------------------------------
# BUSCAR ARQUIVOS CSV
# ------------------------------------------------

def find_csv_files(folder):

    folder = Path(folder)

    return list(folder.rglob("*.csv"))


# ------------------------------------------------
# EXTRAIR METADADOS DO CAMINHO
# ------------------------------------------------

def extract_metadata(file):

    parts = file.parts

    metadata = {
        "file": file,
        "file_name": file.name,
        "device": file.stem.lower(),
        "folder": file.parent.name,
    }

    return metadata


# ------------------------------------------------
# CONTAR LINHAS DOS ARQUIVOS
# ------------------------------------------------

def count_lines(file):

    try:
        df = pd.read_csv(file)

        return df.shape[0]

    except Exception:

        return None


# ------------------------------------------------
# GERAR DATASET DE METADADOS
# ------------------------------------------------

def build_metadata_dataset(folder):

    files = find_csv_files(folder)

    metadata = []

    for file in files:

        info = extract_metadata(file)

        info["line_count"] = count_lines(file)

        metadata.append(info)

    return pd.DataFrame(metadata)


# ------------------------------------------------
# VALIDAR QUANTIDADE DE ARQUIVOS
# ------------------------------------------------

def validate_file_quantity(df):

    counts = df.groupby("device").size()

    validation = {}

    for device, expected in EXPECTED_FILES.items():

        validation[device] = counts.get(device, 0) == expected

    return validation


# ------------------------------------------------
# VALIDAR QUANTIDADE DE LINHAS
# ------------------------------------------------

def validate_line_counts(df):

    validation = {}

    for device, threshold in EXPECTED_LINES.items():

        subset = df[df["device"].str.contains(device)]

        if subset.empty:

            validation[device] = False

        else:

            validation[device] = subset["line_count"].mean() >= threshold

    return validation


# ------------------------------------------------
# DETECTAR QUEBRAS EM SINAL
# ------------------------------------------------

def detect_signal_breaks(df, time_column="time"):

    df[time_column] = pd.to_datetime(df[time_column], errors="coerce")

    df["time_diff"] = df[time_column].diff()

    breaks = df[df["time_diff"] > pd.Timedelta(seconds=0.1)]

    return breaks


# ------------------------------------------------
# EXECUTAR PIPELINE
# ------------------------------------------------

def analyze_dataset(folder):

    metadata_df = build_metadata_dataset(folder)

    file_validation = validate_file_quantity(metadata_df)

    line_validation = validate_line_counts(metadata_df)

    return {
        "metadata": metadata_df,
        "file_validation": file_validation,
        "line_validation": line_validation,
    }


# ------------------------------------------------
# EXECUÇÃO
# ------------------------------------------------

if __name__ == "__main__":

    folder = "data"

    results = analyze_dataset(folder)

    print("\nFile validation:")
    print(results["file_validation"])

    print("\nLine validation:")
    print(results["line_validation"])