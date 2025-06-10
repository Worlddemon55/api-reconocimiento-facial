# app.py
from flask import Flask, request, jsonify
import face_recognition
import numpy as np
import pickle
import base64
import cv2

# Crea el servidor web
app = Flask(__name__)

# --- CARGA INICIAL DE LA BASE DE DATOS Y MODELOS ---
print(">> INICIANDO SERVIDOR: Cargando base de datos...")

try:
    # Carga la base de datos de rostros que creamos con el otro script
    with open("database.pickle", "rb") as f:
        all_persons_data = pickle.load(f)
    
    # Extrae solo los "encodings" para que la comparación matemática sea más rápida
    known_encodings = [data["encoding"] for data in all_persons_data]
    print(f"✅ Base de datos con {len(known_encodings)} rostros cargada.")
except Exception as e:
    print(f"❌ ERROR: No se pudo cargar 'database.pickle'. Asegúrate de ejecutar 'create_database_v2.py' primero.")
    all_persons_data = []

# --- Endpoint de la API (/reconocer) ---
# Esta es la "puerta" a la que la app móvil enviará las imágenes
@app.route("/reconocer", methods=["POST"])
def reconocer_rostro():
    print("\n>> Petición de reconocimiento recibida...")
    
    if "image" not in request.json:
        print("❌ Petición rechazada: No contenía el campo 'image'.")
        return jsonify({"error": "Petición inválida. Falta el campo 'image'."}), 400

    # Decodifica la imagen que viene en formato Base64 desde la app
    image_b64 = request.json["image"]
    image_bytes = base64.b64decode(image_b64)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame_rgb = cv2.cvtColor(cv2.imdecode(image_array, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

    # Detecta las caras en la imagen y crea sus "huellas faciales"
    face_locations = face_recognition.face_locations(frame_rgb)
    face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)
    print(f"🔎 Se encontraron {len(face_encodings)} rostro(s) en la imagen.")

    found_matches = []

    # Compara cada cara encontrada con nuestra base de datos
    for face_encoding in face_encodings:
        # Compara la cara actual con TODAS las caras conocidas y mide la "distancia"
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        
        # Busca la distancia más pequeña (el rostro que más se parece)
        best_match_index = np.argmin(face_distances)
        min_distance = face_distances[best_match_index]
        
        # Convierte esa distancia a un porcentaje de similitud
        similarity_percentage = (1.0 - min_distance) * 100
        
        print(f"   - Mejor coincidencia: '{all_persons_data[best_match_index]['nombre']}' con distancia de {min_distance:.2f} ({similarity_percentage:.2f}%)")

        # Filtro de confianza del 80% que solicitaste
        if similarity_percentage >= 80:
            matched_person_data = all_persons_data[best_match_index].copy()
            matched_person_data['porcentaje_parecido'] = round(similarity_percentage, 2)
            del matched_person_data['encoding'] # No enviamos el dato técnico del encoding
            
            found_matches.append(matched_person_data)
            print(f"   ✅ COINCIDENCIA VÁLIDA: {matched_person_data['nombre']} ({similarity_percentage:.2f}%)")

    # Prepara y envía la respuesta final a la app móvil
    if found_matches:
        print(">> Enviando respuesta con coincidencias.")
        return jsonify({"status": "coincidencia_encontrada", "personas": found_matches})
    else:
        print(">> Enviando respuesta sin coincidencias válidas.")
        return jsonify({"status": "sin_coincidencias"})

# --- Comando para iniciar el servidor ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)