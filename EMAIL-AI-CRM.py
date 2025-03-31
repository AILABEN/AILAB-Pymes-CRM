import os
import sys
import json
import time
import datetime
import re
import logging
import openai
import urllib.parse
import webbrowser
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Cargar las variables de entorno desde .env
load_dotenv()

# Configurar logging si lo deseas
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configurar la clave de API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def obtener_respuesta_chatgpt(prompt: str, modelo="gpt-3.5-turbo") -> str:
    """
    Envía un prompt a ChatGPT usando la API de OpenAI y regresa la respuesta.
    """
    try:
        respuesta = openai.ChatCompletion.create(
            model=modelo,
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        # La respuesta principal suele venir en la primera posición de choices
        texto_respuesta = respuesta['choices'][0]['message']['content']
        return texto_respuesta.strip()
    except Exception as e:
        logging.error(f"Error al obtener la respuesta de ChatGPT: {e}")
        return ""

def enviar_correo(
    remitente: str, 
    password: str, 
    destinatario: str,
    asunto: str, 
    cuerpo: str, 
    archivo_adjunto: str = None
) -> None:
    """
    Envía un correo electrónico simple usando SMTP de Gmail (u otro proveedor).
    - remitente: dirección de correo desde donde se envía
    - password: contraseña o token de aplicación para ese correo
    - destinatario: dirección de correo del receptor
    - asunto: asunto del correo
    - cuerpo: texto del correo
    - archivo_adjunto: ruta de un archivo a adjuntar (opcional)
    """
    
    # Crear el objeto MIMEMultipart
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto

    # Adjuntar el cuerpo del mensaje (texto plano)
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Adjuntar un archivo si se proporciona una ruta
    if archivo_adjunto:
        try:
            with open(archivo_adjunto, "rb") as adj:
                # Se crea la instancia MIMEBase
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(adj.read())
            
            encoders.encode_base64(parte)
            parte.add_header('Content-Disposition', f'attachment; filename={os.path.basename(archivo_adjunto)}')
            mensaje.attach(parte)
        except FileNotFoundError:
            logging.warning(f"No se encontró el archivo {archivo_adjunto}. Se enviará el correo sin adjunto.")

    # Iniciar sesión en el servidor SMTP (en este ejemplo, Gmail)
    # Si usas otro proveedor, ajusta los datos (host, puerto, etc.)
    try:
        servidor_smtp = smtplib.SMTP('smtp.gmail.com', 587)
        servidor_smtp.starttls()
        servidor_smtp.login(remitente, password)
        texto = mensaje.as_string()
        servidor_smtp.sendmail(remitente, destinatario, texto)
        servidor_smtp.quit()
        logging.info("Correo enviado exitosamente.")
    except Exception as e:
        logging.error(f"Error al enviar el correo: {e}")

def main():
    # Definir tu prompt o pregunta para ChatGPT
    prompt = "Proporciona un resumen corto sobre la importancia de la IA en la educación."
    
    # Obtener la respuesta de ChatGPT
    respuesta_chatgpt = obtener_respuesta_chatgpt(prompt)
    logging.info(f"Respuesta de ChatGPT: {respuesta_chatgpt}")

    # Obtener credenciales desde variables de entorno
    remitente = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    destinatario = "destinatario@ejemplo.com"  # Cambia esto al correo que necesites

    # Asunto y cuerpo del correo
    asunto = "Resumen sobre IA y educación"
    cuerpo = f"Hola,\n\nEste es el resumen obtenido desde ChatGPT:\n\n{respuesta_chatgpt}\n\n¡Saludos!"

    # Enviar el correo
    enviar_correo(
        remitente=remitente,
        password=password,
        destinatario=destinatario,
        asunto=asunto,
        cuerpo=cuerpo,
        archivo_adjunto=None  # o especifica una ruta si quieres adjuntar un archivo
    )

if __name__ == "__main__":
    main()
