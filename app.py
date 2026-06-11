from flask import Flask, jsonify
import requests
import time
import random  # <-- IMPORTANTE: Librería para elegir al azar

app = Flask(__name__)

# --- Base de datos en memoria caché local ---
cache_votos = {
    "num_sanchez": 9032091,   
    "num_fujimori": 9032653,
    "ultima_actualizacion_exitosa": 0
}

# --- ESTRATEGIA 2: Catálogo de Identidades Reales (User-Agents) ---
# Almacenamos diferentes navegadores (celulares, Macs, Windows) para confundir al firewall
NAVEGADORES = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def formatear_votos(numero):
    try:
        return f"{int(numero):,}"
    except (ValueError, TypeError):
        return str(numero)

@app.route('/votos')
def obtener_votos():
    url_onpe = "https://resultadosegundavuelta.onpe.gob.pe/presentacion-backend/resumen-general/participantes?idEleccion=10&tipoFiltro=eleccion"
    
    # --- AQUÍ SE INCLUYE LA LÍNEA: Cambia de identidad en cada petición individual ---
    user_agent_aleatorio = random.choice(NAVEGADORES)
    
    headers = {
        'User-Agent': user_agent_aleatorio,  # <-- Se asigna la identidad camaleónica aquí
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Origin': 'https://resultadosegundavuelta.onpe.gob.pe',
        'Referer': 'https://resultadosegundavuelta.onpe.gob.pe/'
    }

    exito = False
    num_sanchez, num_fujimori = 0, 0

    # --- INTENTO 1: Conexión Directa ---
    try:
        respuesta = requests.get(url_onpe, headers=headers, timeout=5)
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

    # --- INTENTO 2: Plan B (Proxy AllOrigins) ---
    if not exito:
        try:
            url_espejo1 = "https://api.allorigins.win/get?url=" + requests.utils.quote(url_onpe)
            respuesta = requests.get(url_espejo1, timeout=6)
            if respuesta.status_code == 200:
                import json
                contents = respuesta.json().get('contents', '')
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

    # --- INTENTO 3: Plan C (Proxy Codetabs Alternativo) ---
    if not exito:
        try:
            url_espejo3 = "https://api.codetabs.com/v1/proxy/?quest=" + url_onpe
            respuesta = requests.get(url_espejo3, headers={'User-Agent': user_agent_aleatorio}, timeout=6)
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

    # --- PROCESAMIENTO INTELIGENTE DE RESULTADOS ---
    if exito:
        cache_votos["num_sanchez"] = num_sanchez
        cache_votos["num_fujimori"] = num_fujimori
        cache_votos["ultima_actualizacion_exitosa"] = time.time()
        
        status_votos1 = formatear_votos(num_sanchez)
        status_votos2 = formatear_votos(num_fujimori)
        dif_votos = abs(num_sanchez - num_fujimori)
    else:
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
