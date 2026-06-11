from flask import Flask, jsonify
import requests
import time
import random

app = Flask(__name__)

# --- Base de datos en memoria caché local ---
cache_votos = {
    "num_sanchez": 9017296,   
    "num_fujimori": 9008103,
    "ultima_actualizacion_exitosa": 0
}

NAVEGADORES = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
]

def formatear_votos(numero):
    try:
        return f"{int(numero):,}"
    except (ValueError, TypeError):
        return str(numero)

@app.route('/votos')
def obtener_votos():
    # Intentaremos consumir desde una réplica abierta o el espejo alterno distribuido
    # que no cuenta con el firewall estricto de la infraestructura gubernamental peruana.
    url_onpe = "https://resultadosegundavuelta.onpe.gob.pe/presentacion-backend/resumen-general/participantes?idEleccion=10&tipoFiltro=eleccion"
    
    # URL Espejo de Datos (Usamos un proxy abierto y limpio que cachea datos de elecciones globales)
    url_espejo_noticias = "https://api.allorigins.win/get?url=" + requests.utils.quote(url_onpe)

    exito = False
    num_sanchez, num_fujimori = 0, 0
    user_agent_aleatorio = random.choice(NAVEGADORES)

    # --- INTENTO 1: Usando el agregador de datos espejo independiente ---
    try:
        respuesta = requests.get(url_espejo_noticias, timeout=7)
        if respuesta.status_code == 200:
            import json
            contents = respuesta.json().get('contents', '')
            # Si el contenido contiene la estructura esperada de la ONPE replicada
            if "nombreCandidato" in contents:
                lista = json.loads(contents).get("data", [])
                for cand in lista:
                    nom = cand.get("nombreCandidato", "")
                    votos = int(cand.get("totalVotosValidos", 0))
                    if "SANCHEZ" in nom: num_sanchez = votos
                    elif "FUJIMORI" in nom: num_fujimori = votos
                if num_sanchez != 0 or num_fujimori != 0:
                    exito = True
    except Exception:
        pass

    # --- INTENTO 2: Intento directo alterno con evasión de firmas ---
    if not exito:
        try:
            # Petición directa simulando una consulta limpia desde fuera de Latam
            respuesta = requests.get(url_onpe, headers={
                'User-Agent': user_agent_aleatorio,
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }, timeout=5)
            if respuesta.status_code == 200:
                lista = respuesta.json().get("data", [])
                for cand in lista:
                    nom = cand.get("nombreCandidato", "")
                    votos = int(cand.get("totalVotosValidos", 0))
                    if "SANCHEZ" in nom: num_sanchez = votos
                    elif "FUJIMORI" in nom: num_fujimori = votos
                if num_sanchez != 0 or num_fujimori != 0:
                    exito = True
        except Exception:
            pass

    # --- PROCESAMIENTO INTELIGENTE ---
    if exito:
        cache_votos["num_sanchez"] = num_sanchez
        cache_votos["num_fujimori"] = num_fujimori
        cache_votos["ultima_actualizacion_exitosa"] = time.time()
        
        status_votos1 = formatear_votos(num_sanchez)
        status_votos2 = formatear_votos(num_fujimori)
        dif_votos = abs(num_sanchez - num_fujimori)
    else:
        # Si todo lo externo falla, seguimos entregando la caché para no congelar el ESP32
        num_sanchez = cache_votos["num_sanchez"]
        num_fujimori = cache_votos["num_fujimori"]
        dif_votos = abs(num_sanchez - num_fujimori)
        
        status_votos1 = f"{formatear_votos(num_sanchez)}*"
        status_votos2 = f"{formatear_votos(num_fujimori)}*"

    return jsonify({
        "candidato1": "Sanchez", 
        "votos1": status_votos1,
        "candidato2": "Fujimori", 
        "votos2": status_votos2,
        "diferencia": formatear_votos(dif_votos)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
