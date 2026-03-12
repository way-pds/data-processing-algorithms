import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# CONFIGURAÇÃO DOS DISPOSITIVOS
# ---------------------------------------------------------

DEVICE_CONFIG = {
    "VivaSensing": ("Timestamp", "ms"),
    "COLA": ("Timestamp_Sensor(us)", "us"),
    "BIA": ("TimeStamp", "ms"),
    "TANITA": ("time", None),
    "psgSleepStaging": ("Timestamp_ms", "ms"),
}


# ---------------------------------------------------------
# BUSCAR ARQUIVOS CSV
# ---------------------------------------------------------

def find_csv_files(folder_path):
    folder = Path(folder_path)
    return list(folder.rglob("*.csv"))


# ---------------------------------------------------------
# EXTRAIR METADADOS DO NOME DO ARQUIVO
# ---------------------------------------------------------

def extract_metadata(file_path):
    name_parts = file_path.name.split("_")

    metadata = {
        "file": file_path,
        "project": file_path.parents[1].name if len(file_path.parents) > 1 else None,
        "device_type": None,
        "file_type": None,
    }

    if len(name_parts) > 2:
        device_info = name_parts[2].split("-")
        metadata["device_type"] = device_info[0]

        if len(device_info) > 1:
            metadata["file_type"] = device_info[1]
        else:
            metadata["file_type"] = "Acc"

    return metadata


# ---------------------------------------------------------
# LER ARQUIVO CSV
# ---------------------------------------------------------

def read_file(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


# ---------------------------------------------------------
# CALCULAR FREQUÊNCIA DE AMOSTRAGEM
# ---------------------------------------------------------

def calculate_sampling_frequency(df, device_type):

    if device_type not in DEVICE_CONFIG:
        return None, None

    column, unit = DEVICE_CONFIG[device_type]

    if column not in df.columns:
        return None, None

    time = pd.to_datetime(df[column], unit=unit)

    diff = time.diff().dt.total_seconds()

    frequency = 1 / diff

    return frequency.mean(), frequency.std()


# ---------------------------------------------------------
# PROCESSAR DATASET
# ---------------------------------------------------------

def analyze_dataset(folder_path):

    files = find_csv_files(folder_path)

    metadata_list = [extract_metadata(f) for f in files]

    dataset = pd.DataFrame(metadata_list)

    dataset = dataset[dataset["device_type"].isin(DEVICE_CONFIG.keys())]

    dataset["dataframe"] = dataset["file"].apply(read_file)

    freq_mean = []
    freq_std = []

    for _, row in dataset.iterrows():

        df = row["dataframe"]

        if df is None:
            freq_mean.append(None)
            freq_std.append(None)
            continue

        mean, std = calculate_sampling_frequency(df, row["device_type"])

        freq_mean.append(mean)
        freq_std.append(std)

    dataset["frequency_mean"] = freq_mean
    dataset["frequency_std"] = freq_std

    return dataset


# ---------------------------------------------------------
# EXECUÇÃO
# ---------------------------------------------------------

if __name__ == "__main__":

    folder = "data"

    result = analyze_dataset(folder)

    print(result.groupby(["device_type", "file_type"])[
        ["frequency_mean", "frequency_std"]
    ].agg({
        "frequency_mean": ["count", "mean", "std"],
        "frequency_std": ["min", "mean", "max"]
    }))