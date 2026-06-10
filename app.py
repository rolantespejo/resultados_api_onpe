from flask import Flask, jsonify
import requests

app = Flask(__name__)

def formatear_votos(numero):
    try:
        return f"{int(numero):,}"
    except (ValueError, TypeError):
        return str(numero)

@app.route('/votos')
def obtener_votos():
    url_onpe = "https://resultadosegundavuelta.onpe.gob.pe/presentacion-backend/resumen-general/participantes?idEleccion=10&tipoFiltro=eleccion"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Origin': 'https://resultadosegundavuelta.onpe.gob.pe',
        'Referer': 'https://resultadosegundavuelta.onpe.gob.pe/'
    }

    # --- INTENTO 1: Conexión Directa ---
    try:
        respuesta = requests.get(url_onpe, headers=headers, timeout=6)
        if respuesta.status_code == 200:
            json_onpe = respuesta.json()
            lista = json_onpe.get("data", [])
            num_sanchez, num_fujimori = 0, 0
            for cand in lista:
                nom = cand.get("nombreCandidato", "")
                votos = int(cand.get("totalVotosValidos", 0))
                if "SANCHEZ" in nom: num_sanchez = votos
                elif "FUJIMORI" in nom: num_fujimori = votos
            if num_sanchez != 0 or num_fujimori != 0:
                return jsonify({
                    "candidato1": "Sanchez", "votos1": formatear_votos(num_sanchez),
                    "candidato2": "Fujimori", "votos2": formatear_votos(num_fujimori),
                    "diferencia": formatear_votos(abs(num_sanchez - num_fujimori))
                })
    except Exception:
        pass

    # --- INTENTO 2: Plan B (Proxy AllOrigins) ---
    try:
        url_espejo1 = "https://api.allorigins.win/get?url=" + requests.utils.quote(url_onpe)
        respuesta = requests.get(url_espejo1, timeout=8)
        if respuesta.status_code == 200:
            import json
            contents = respuesta.json().get('contents', '')
            json_onpe = json.loads(contents)
            lista = json_onpe.get("data", [])
            num_sanchez, num_fujimori = 0, 0
            for cand in lista:
                nom = cand.get("nombreCandidato", "")
                votos = int(cand.get("totalVotosValidos", 0))
                if "SANCHEZ" in nom: num_sanchez = votos
                elif "FUJIMORI" in nom: num_fujimori = votos
            if num_sanchez != 0 or num_fujimori != 0:
                return jsonify({
                    "candidato1": "Sanchez", "votos1": formatear_votos(num_sanchez),
                    "candidato2": "Fujimori", "votos2": formatear_votos(num_fujimori),
                    "diferencia": formatear_votos(abs(num_sanchez - num_fujimori))
                })
    except Exception:
        pass

    # --- INTENTO 3: Plan C (Proxy Alternativo ThingProxy) ---
    try:
        # Usamos otro puente público diseñado para saltar bloqueos de origen
        url_espejo2 = "https://thingproxy.freeboard.io/fetch/" + url_onpe
        respuesta = requests.get(url_espejo2, headers=headers, timeout=8)
        if respuesta.status_code == 200:
            json_onpe = respuesta.json()
            lista = json_onpe.get("data", [])
            num_sanchez, num_fujimori = 0, 0
            for cand in lista:
                nom = cand.get("nombreCandidato", "")
                votos = int(cand.get("totalVotosValidos", 0))
                if "SANCHEZ" in nom: num_sanchez = votos
                elif "FUJIMORI" in nom: num_fujimori = votos
            if num_sanchez != 0 or num_fujimori != 0:
                return jsonify({
                    "candidato1": "Sanchez", "votos1": formatear_votos(num_sanchez),
                    "candidato2": "Fujimori", "votos2": formatear_votos(num_fujimori),
                    "diferencia": formatear_votos(abs(num_sanchez - num_fujimori))
                })
    except Exception:
        pass

    # Si los 3 métodos fallan (porque la ONPE desconectó su servidor backend por completo),
    # devolvemos este estado intermedio para informarte en el LCD sin romper el JSON.
    return jsonify({
        "candidato1": "Error", "votos1": "ONPE_Down",
        "candidato2": "Error", "votos2": "Reintentando",
        "diferencia": "0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
