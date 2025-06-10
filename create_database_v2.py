# create_database_v2.py (Versión final para leer SIEMPRE desde Google Drive)

import face_recognition
import requests
import pandas as pd
import pickle
import cv2
import numpy as np

# --- CONFIGURACIÓN ---
# Se usa el link directo a tu Google Sheet para que se descargue como un archivo CSV.
# Esta es la única fuente de datos.
CSV_URL = "https://docs.google.com/spreadsheets/d/1GenR7X8aV4PrLnv9sv0mg2E8lJfrDXiy8kU2-9Fz1ew/export?format=csv"

print(">> INICIANDO: Creación de base de datos de rostros.")
print(f"📖 Conectando a Google Drive para leer los datos desde la URL...")

try:
    # Leemos el archivo CSV directamente desde la URL de exportación de Google
    df = pd.read_csv(CSV_URL)
    print("✅ Hoja de cálculo leída correctamente desde Google Drive.")
except Exception as e:
    # Este error puede ocurrir si la hoja no es pública.
    print(f"❌ ERROR: No se pudo leer el archivo. Asegúrate de que el permiso de la hoja sea 'Cualquier persona con el enlace puede ver'.")
    print(f"   Detalle técnico: {e}")
    exit()

# Validar que las columnas esperadas existen (esta es la lista sin la columna 'estado')
columnas_esperadas = ['id', 'nombre', 'sexo', 'lugar_rq', 'delito', 'recompensa', 'imagen_url']
if not all(col in df.columns for col in columnas_esperadas):
    print("❌ ERROR: Faltan columnas esperadas en el archivo.")
    print(f"   Se esperaban: {columnas_esperadas}")
    print(f"   Se encontraron: {list(df.columns)}")
    exit()

all_persons_data = []

print("⚙️  Procesando imágenes de referencia desde los links del archivo...")
for index, row in df.iterrows():
    # Verifica si hay datos válidos en 'nombre' y 'imagen_url' para evitar errores
    if pd.isna(row['nombre']) or pd.isna(row['imagen_url']):
        print(f"⚠️  Fila {index + 2} omitida: falta 'nombre' o 'imagen_url'.")
        continue

    person_info = {
        "id": row['id'],
        "nombre": row['nombre'],
        "sexo": row['sexo'],
        "lugar_rq": row['lugar_rq'],
        "delito": row['delito'],
        "recompensa": row['recompensa'],
        "encoding": None
    }

    url_imagen = row['imagen_url']
    print(f"\n🧑 Procesando fila {index + 2}: {person_info['nombre']}")

    try:
        response = requests.get(url_imagen, stream=True).raw
        image_array = np.asarray(bytearray(response.read()), dtype="uint8")
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_image)

        if face_encodings:
            person_info["encoding"] = face_encodings[0]
            all_persons_data.append(person_info)
            print(f"✅ Rostro de {person_info['nombre']} codificado y guardado.")
        else:
            print(f"❌ No se detectó rostro en la imagen de {person_info['nombre']}. Fila omitida.")
    except Exception as e:
        print(f"❌ ERROR procesando la imagen de {person_info['nombre']}. Revisa el link de la imagen. Detalle: {e}")

# Guardamos los datos en el archivo local 'database.pickle'
with open("database.pickle", "wb") as f:
    pickle.dump(all_persons_data, f)

print(f"\n🎉 ¡PROCESO FINALIZADO! Base de datos creada con {len(all_persons_data)} registros válidos.")
print("   Archivo 'database.pickle' guardado en tu carpeta.")