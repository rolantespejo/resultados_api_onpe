from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/votos')
def obtener_votos():
    try:
        # 1. Reemplaza ESTA URL por el enlace completo que obtuviste en el DevTools
        # (Haz clic derecho sobre "participantes?idEleccion=10..." a la izquierda y dale a "Copy URL")
        url_api_onpe = "https://resultadosegundavuelta.onpe.gob.pe/presentacion-backend/resumen-general/participantes?idEleccion=10&tipoFiltro=eleccion" 
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Hacemos la consulta a la ONPE
        respuesta = requests.get(url_api_onpe, headers=headers, timeout=10)
        json_onpe = respuesta.json()
        
        # Variables para almacenar los porcentajes finales
        votos_sanchez = "0.0%"
        votos_fujimori = "0.0%"
        
        # 2. Navegamos la estructura exacta de tu imagen: json_onpe["data"]
        lista_candidatos = json_onpe.get("data", [])
        
        for candidato in lista_candidatos:
            nombre = candidato.get("nombreCandidato", "")
            # Obtenemos el porcentaje (ej: 49.974) y lo limitamos a 2 decimales agregando el símbolo %
            porcentaje = f"{round(candidato.get('porcentajeVotosValidos', 0.0), 2)}%"
            
            if "SANCHEZ" in nombre:
                votos_sanchez = porcentaje
            elif "FUJIMORI" in nombre:
                votos_fujimori = porcentaje
                
        # 3. Devolvemos el JSON limpio para el ESP32
        return jsonify({
            "candidato1": "Sanchez",
            "votos1": votos_sanchez,
            "candidato2": "Fujimori",
            "votos2": votos_fujimori
        })
        
    except Exception as e:
        return jsonify({
            "candidato1": "Error", "votos1": "0.0%",
            "candidato2": "Error", "votos2": "0.0%"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)