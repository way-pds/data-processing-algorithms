import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# CONFIGURAÇÃO DOS SENSORES
# ---------------------------------------------------------

SENSOR_COLUMNS = {
    "accelerometer": ["Acc_X", "Acc_Y", "Acc_Z"],
    "gyroscope": ["Gyr_X", "Gyr_Y", "Gyr_Z"],
    "magnetometer": ["Mag_X", "Mag_Y", "Mag_Z"],
    "heart_rate": ["HR"],
}


# ---------------------------------------------------------
# BUSCAR ARQUIVOS CSV
# ---------------------------------------------------------

def find_csv_files(folder):

    folder = Path(folder)

    return list(folder.rglob("*.csv"))


# ---------------------------------------------------------
# CONTAR VALORES VÁLIDOS
# ---------------------------------------------------------

def count_valid_data(df, columns):

    counts = {}

    for col in columns:

        if col in df.columns:

            counts[col] = df[col].notna().sum()

    return counts


# ---------------------------------------------------------
# PROCESSAR ARQUIVOS
# ---------------------------------------------------------

def analyze_sensor_data(folder):

    files = find_csv_files(folder)

    results = []

    for file in files:

        try:

            df = pd.read_csv(file)

        except Exception:

            continue

        row = {"file": file.name}

        for sensor, columns in SENSOR_COLUMNS.items():

            counts = count_valid_data(df, columns)

            for col, value in counts.items():

                row[col] = value

        results.append(row)

    return pd.DataFrame(results)


# ---------------------------------------------------------
# EXECUÇÃO
# ---------------------------------------------------------

if __name__ == "__main__":

    folder = "data"

    dataset = analyze_sensor_data(folder)

    print("\nSummary of available data:\n")

    print(dataset.sum(numeric_only=True))