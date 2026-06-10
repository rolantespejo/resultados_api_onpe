from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/votos')
def obtener_votos():
    try:
        # Tu URL del backend de la ONPE
        url_api_onpe = "https://resultadosegundavuelta.onpe.gob.pe/presentacion-backend/resumen-general/participantes?idEleccion=10&tipoFiltro=eleccion" 
        
        # Cabeceras ultra-completas para clonar exactamente el comportamiento de tu Google Chrome
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'es-419,es;q=0.9,en;q=0.8',
            'Origin': 'https://resultadosegundavuelta.onpe.gob.pe',
            'Referer': 'https://resultadosegundavuelta.onpe.gob.pe/',
            'Connection': 'keep-alive'
        }
        
        # Hacemos la consulta simulando una sesión activa
        sesion = requests.Session()
        respuesta = sesion.get(url_api_onpe, headers=headers, timeout=10)
        
        # Si la ONPE nos da un error de bloqueo (ej: 403 o 400), forzamos a ver qué pasó en los logs de Render
        respuesta.raise_for_status()
        
        json_onpe = respuesta.json()
        
        votos_sanchez = "0.0%"
        votos_fujimori = "0.0%"
        
        lista_candidatos = json_onpe.get("data", [])
        
        for candidato in lista_candidatos:
            nombre = candidato.get("nombreCandidato", "")
            porcentaje = f"{round(candidato.get('porcentajeVotosValidos', 0.0), 2)}%"
            
            if "SANCHEZ" in nombre:
                votos_sanchez = porcentaje
            elif "FUJIMORI" in nombre:
                votos_fujimori = porcentaje
                
        return jsonify({
            "candidato1": "Sanchez",
            "votos1": votos_sanchez,
            "candidato2": "Fujimori",
            "votos2": votos_fujimori
        })
        
    except Exception as e:
        # Imprime el error exacto en la consola negra de Render para poder auditarlo si persiste
        print(f"Error detallado en la extracción: {str(e)}")
        return jsonify({
            "candidato1": "Error", "votos1": "0.0%",
            "candidato2": "Error", "votos2": "0.0%"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
