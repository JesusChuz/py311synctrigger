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
#@app.function_name("blob_triggerATF")
@app.blob_trigger(arg_name="myblob", path="datos/{name}", connection="AzureWebJobsStorage")
def blob_trigger(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob: {myblob.name}, Blob Size: {myblob.length} bytes")

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    try:
        # Leer el contenido del blob directamente sin guardarlo en el sistema de archivos
        source = myblob.read()
        logging.info("Blob leído exitosamente")

        # Procesar el documento usando Azure Form Recognizer
        poller = document_analysis_client.begin_analyze_document(
            model_id=model_id, document=source
        )
        result = poller.result()
        logging.info("Documento analizado exitosamente")

        arreglo_resultados = {}

        for document in result.documents:
            for field_name, field in document.fields.items():
                arreglo_resultados[field_name] = field.value

        datos = pd.DataFrame([arreglo_resultados])
        #Cadena de conexion a la base de datos de Azure SQL
        connection_string = (
            'Driver={ODBC Driver 18 for SQL Server};'
            'Server=tcp:<bd-name>.database.windows.net,1433;'
            'Database=<database-name>;'
            'Uid=<user-id>;'
            'Pwd=<password-user>'
            'Encrypt=yes;'
            'TrustServerCertificate=no;'
            'Connection Timeout=30;'
        )

        try:
            connection = pyodbc.connect(connection_string)
            cursor = connection.cursor()
            logging.info("Conexión Correcta")

            # Iterar sobre el DataFrame y ejecutar la inserción para cada fila
            for index, row in datos.iterrows():
                cursor.execute(
                    """
                    INSERT INTO <Table-name> (
                        <Query to run in SQL Server>
                    ) VALUES <>
                    """,
                    myblob.name,
                    
                )
                # Confirmar la inserción en la base de datos
                connection.commit()
                logging.info(f"Fila {index+1} insertada con éxito")

        except Exception as e:
            logging.error(f"Error al conectar a la base de datos o insertar datos: {e}")

        finally:
            # Cerrar la conexión
            if connection:
                connection.close()
                logging.info("Conexión cerrada")

    except Exception as e:
        logging.error(f"Error durante el análisis del documento: {e}")
        raise

