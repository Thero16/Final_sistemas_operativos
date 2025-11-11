from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import boto3
import pandas as pd
import io
from botocore.exceptions import ClientError

app = FastAPI()

# Cliente S3 (usa las credenciales configuradas con AWS CLI)
s3 = boto3.client("s3")

# Nombre del bucket y archivo
BUCKET_NAME = "final-sis-operativos-jpcb"
CSV_FILE = "datos.csv"


# Modelo de datos
class Persona(BaseModel):
    nombre: str = Field(..., example="Juan")
    edad: int = Field(..., gt=0, example=25)
    altura: float = Field(..., gt=0, example=1.75)


@app.post("/personas")
def agregar_persona(persona: Persona):
    """Recibe datos y los guarda en un archivo CSV dentro del bucket S3"""
    try:
        # Intentar leer el CSV existente
        try:
            response = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_FILE)
            df = pd.read_csv(io.BytesIO(response["Body"].read()))
        except s3.exceptions.NoSuchKey:
            df = pd.DataFrame(columns=["nombre", "edad", "altura"])

        # Agregar nueva fila
        nueva_fila = pd.DataFrame([persona.dict()])
        df = pd.concat([df, nueva_fila], ignore_index=True)

        # Guardar CSV actualizado en S3
        with io.StringIO() as csv_buffer:
            df.to_csv(csv_buffer, index=False)
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=CSV_FILE,
                Body=csv_buffer.getvalue()
            )

        return {"mensaje": "Datos guardados correctamente", "total_registros": len(df)}

    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error al acceder a S3: {str(e)}")


@app.get("/personas")
def contar_personas():
    """Devuelve el número de filas en el CSV almacenado en S3"""
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_FILE)
        df = pd.read_csv(io.BytesIO(response["Body"].read()))
        return {"filas": len(df)}
    except s3.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="No existe el archivo CSV aún.")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error al acceder a S3: {str(e)}")
