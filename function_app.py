import logging
from azure.storage.blob import BlobServiceClient
import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import pandas as pd
import pyodbc
#credenciales para llamar al Documnt Intelligence de Azure AI Services para procesar los blob
endpoint = "a"
key = "a"
model_id = "a"

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="datos/{name}", connection="AzureWebJobsStorage") 
def blob_trigger(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob: {myblob.name}, Blob Size: {myblob.length} bytes")
    try:
        # Leer el contenido del blob directamente sin guardarlo en el sistema de archivos
        source = myblob.read()
        logging.info("Blob leído exitosamente")

    except Exception as e:
        logging.error(f"Error durante el análisis del documento: {e}")
        raise


