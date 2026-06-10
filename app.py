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
        
        num_sanchez = 0
        num_fujimori = 0
        
        for candidato in lista_candidatos:
            nombre = candidato.get("nombreCandidato", "")
            votos_puros = int(candidato.get("totalVotosValidos", 0))
            
            if "SANCHEZ" in nombre:
                num_sanchez = votos_puros
            elif "FUJIMORI" in nombre:
                num_fujimori = votos_puros
                
        if num_sanchez != 0 or num_fujimori != 0:
            # Calculamos la diferencia absoluta (siempre positiva)
            dif_numerica = abs(num_sanchez - num_fujimori)
            
            return jsonify({
                "candidato1": "Sanchez", "votos1": formatear_votos(num_sanchez),
                "candidato2": "Fujimori", "votos2": formatear_votos(num_fujimori),
                "diferencia": formatear_votos(dif_numerica) # Nueva llave calculada
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
        
        num_sanchez = 0
        num_fujimori = 0
        
        for candidato in lista_candidatos:
            nombre = candidato.get("nombreCandidato", "")
            votos_puros = int(candidato.get("totalVotosValidos", 0))
            
            if "SANCHEZ" in nombre:
                num_sanchez = votos_puros
            elif "FUJIMORI" in nombre:
                num_fujimori = votos_puros
                
        dif_numerica = abs(num_sanchez - num_fujimori)
        return jsonify({
            "candidato1": "Sanchez", "votos1": formatear_votos(num_sanchez),
            "candidato2": "Fujimori", "votos2": formatear_votos(num_fujimori),
            "diferencia": formatear_votos(dif_numerica) # Nueva llave calculada
        })
    except Exception as e:
        return jsonify({
            "candidato1": "Error", "votos1": "SinConexion",
            "candidato2": "Error", "votos2": "ONPE_Down",
            "diferencia": "0"
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
