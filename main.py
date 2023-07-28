from enum import Enum
import os
from fastapi.responses import FileResponse
from gtts import gTTS
from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List, Tuple
import matplotlib.pyplot as plt

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app = FastAPI()

class Item(BaseModel):
    mes: str
    monto: float


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.post("/text/")
async def texToAudio(data: dict = Body(..., embed=True)):
    # Obtener el texto y el idioma del JSON recibido
    texto_recibido = data.get("texto", "")
    idioma_recibido:str= data.get("idioma", "")

    # Directorio donde se guardarán los archivos de audio
    directorio_uploads = "uploads"
    os.makedirs(directorio_uploads, exist_ok=True)

    # Ruta completa del archivo de audio
    archivo_audio = os.path.join(directorio_uploads, "welcome.mp3")

    # Crear el archivo de audio con gTTS
    traduccion = gTTS(text=texto_recibido, lang=idioma_recibido, slow=False)
    traduccion.save(archivo_audio)

    # Enviar el archivo de audio en la respuesta
    return FileResponse(archivo_audio, media_type="audio/mpeg")



@app.post("/datos/")
async def recibir_datos(datos: List[Item]):
    # Extraer los datos de mes y monto para el gráfico
    meses = [item.mes for item in datos]
    montos = [item.monto for item in datos]

    # Crear el gráfico de barras
    plt.bar(meses, montos)
    plt.xlabel("Mes")
    plt.ylabel("Monto")
    plt.title("Gráfico de montos por mes")

    # Guardar el gráfico en un archivo JPEG con alta calidad (calidad 95)
    plt.savefig("grafico.jpg", format="jpeg", quality=95)

    # Cerrar la figura para liberar memoria
    plt.close()

    # Devolver la imagen generada como respuesta
    return FileResponse("grafico.jpg", media_type="image/jpeg")