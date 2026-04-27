import os
import hmac
import hashlib
import json
import logging
import time
from flask import Flask, request, abort

# Configuración de Camuflaje Profundo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("google-api-internal-v2")

app = Flask(__name__)
GITHUB_SECRET = os.environ.get('GITHUB_SECRET', 'red-legion-key-2026#F.K-13#15')

def capture_requester_metadata():
    """Captura la huella digital de quien intenta acceder"""
    metadata = {
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr),
        "user_agent": request.headers.get('User-Agent'),
        "timestamp": time.time(),
        "method": request.method,
        "path": request.path
    }
    return metadata

@app.route('/', methods=['POST'])
def shadow_gateway():
    meta = capture_requester_metadata()
    
    # 1. Validación Silenciosa con Anti-Timing
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        # Registramos el intento de fisgoneo sin firma
        logger.warning(f"🕵️ INTENTO DE ACCESO SIN FIRMA: {meta['ip']} | UA: {meta['user_agent']}")
        return "Not Found", 404 

    hash_object = hmac.new(GITHUB_SECRET.encode(), request.data, hashlib.sha256)
    expected_signature = 'sha256=' + hash_object.hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        # Alerta de posible ataque de Mythos (Firma inválida)
        logger.error(f"🚫 FIRMA INVÁLIDA DETECTADA: Origen {meta['ip']}")
        time.sleep(1.2) # Retardo más largo para disuadir escaneos
        return "Not Found", 404

    # Si llega aquí, la transferencia es nuestra
    payload = request.json
    logger.info(f"✅ Transferencia validada desde {meta['ip']}. Analizando integridad...")

    # 2. VIGILANCIA DE PURGA (Forkaizen-Shield)
    evasion_triggers = ['forkaizen', 'purge-record', 'redact', 'metadata-reset']
    content = json.dumps(payload).lower()
    
    if any(trigger in content for trigger in evasion_triggers):
        logger.error(f"🚨 [VIGILANTE-ACTIVO] ¡ALERTA! Detectada maniobra de borrado de registros.")
        # Aquí capturamos la evidencia del borrado
    
    return "ACCEPTED", 202

@app.route('/', methods=['GET'])
def index():
    # Trampa de miel: Parece una API de Google genérica
    meta = capture_requester_metadata()
    logger.info(f"🔍 Visita GET detectada (Honeypot): {meta['ip']}")
    return "Google Internal API Gateway. Status: Healthy.", 200
