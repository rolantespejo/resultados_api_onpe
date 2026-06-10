from flask import Flask, jsonify
import requests

app = Flask(__name__)

def formatear_votos(numero):
    """Convierte un número entero en texto con separadores de miles (Ej: 9017296 -> 9,017,296)"""
    try:
        return f"{int(numero):,}"
    except (ValueError, TypeError):
        return str(numero)

@app.route('/votos')
def obtener_votos():
    url_onpe = "https://resultadosegundavuelta.onpe.gob.pe/presentacion-backend/resumen-general/participantes?idEleccion=10&tipoFiltro=eleccion"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://resultadosegundavuelta.onpe.gob.pe',
        'Referer': 'https://resultadosegundavuelta.onpe.gob.pe/'
    }

    try:
        # Intento 1: Conexión directa
        respuesta = requests.get(url_onpe, headers=headers, timeout=7)
        json_onpe = respuesta.json()
        lista_candidatos = json_onpe.get("data", [])
        
        votos_sanchez = "0"
        votos_fujimori = "0"
        
        for candidato in lista_candidatos:
            nombre = candidato.get("nombreCandidato", "")
            cantidad = formatear_votos(candidato.get("totalVotosValidos", 0))
            
            if "SANCHEZ" in nombre:
                votos_sanchez = cantidad
            elif "FUJIMORI" in nombre:
                votos_fujimori = cantidad
                
        if votos_sanchez != "0" or votos_fujimori != "0":
            return jsonify({
                "candidato1": "Sanchez", "votos1": votos_sanchez,
                "candidato2": "Fujimori", "votos2": votos_fujimori
            })
            
    except Exception:
        pass

    # Intento 2: Plan B (A través del espejo proxy si Render es bloqueado)
    try:
        url_espejo = "https://api.allorigins.win/get?url=" + requests.utils.quote(url_onpe)
        respuesta_espejo = requests.get(url_espejo, timeout=10)
        datos_espejo = respuesta_espejo.json()
        
        import json
        json_onpe = json.loads(datos_espejo['contents'])
        lista_candidatos = json_onpe.get("data", [])
        
        votos_sanchez = "0"
        votos_fujimori = "0"
        
        for candidato in lista_candidatos:
            nombre = candidato.get("nombreCandidato", "")
            cantidad = formatear_votos(candidato.get("totalVotosValidos", 0))
            
            if "SANCHEZ" in nombre:
                votos_sanchez = cantidad
            elif "FUJIMORI" in nombre:
                votos_fujimori = cantidad
                
        return jsonify({
            "candidato1": "Sanchez", "votos1": votos_sanchez,
            "candidato2": "Fujimori", "votos2": votos_fujimori
        })
    except Exception as e:
        # CAMBIO CLAVE: Si todo falla a nivel de red, enviamos una etiqueta clara de error.
        # El ESP32 recibirá esto y lo pintará directamente en la pantalla, alertándote de inmediato.
        return jsonify({
            "candidato1": "Error", "votos1": "SinConexion",
            "candidato2": "Error", "votos2": "ONPE_Down"
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
