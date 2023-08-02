from ast import parse
from enum import Enum
import os
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse
from gtts import gTTS
from fastapi import FastAPI, Body, HTTPException, Request
from matplotlib import ticker
from pydantic import BaseModel
from typing import List, Tuple
import matplotlib.pyplot as plt
from multiprocessing import set_start_method
from multiprocessing import Process, Manager
from dateparser.search import search_dates
from dateutil.parser import parse

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app = FastAPI()

class Item(BaseModel):
    mes: str
    monto: float

# class TextoModel(BaseModel):
#     texto: str


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
    # Obtener el texto y el idioma del JSON 
    texto_recibido = data.get("texto", "")
    idioma_recibido: str = data.get("idioma", "")

    # Agregar comillas triples al texto recibido
    texto_recibido = f'\'\'\'{texto_recibido}\'\'\''

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
def recibir_datos(datos: List[Item]):
    # Extraer los datos de mes y monto para el gráfico
    meses = [item.mes for item in datos]
    montos = [item.monto for item in datos]

    # Crear el gráfico de barras
    plt.bar(meses, montos)
    plt.xlabel("Month")
    plt.ylabel("USD")
    plt.title("Monthly billing")

    # Formatear el eje y para mostrar valores legibles automáticamente
    def format_y_axis(value, _):
        if value >= 1e9:
            return f'{value / 1e9:.0f}B'
        elif value >= 1e6:
            return f'{value / 1e6:.0f}M'
        elif value >= 1e3:
            return f'{value / 1e3:.0f}K'
        else:
            return f'{value:.0f}'

    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_y_axis))

    # Ajustar el espaciado entre los ticks del eje x (meses)
    plt.xticks(range(len(meses)), meses, rotation=45, ha="right")

    # Guardar el gráfico en un archivo JPEG con alta calidad (calidad 95)
    plt.savefig("grafico.jpg", format="jpeg")

    # Cerrar la figura para liberar memoria
    plt.close()

    # Devolver la imagen generada como respuesta
    return FileResponse("grafico.jpg", media_type="image/jpeg")


# async def recibir_datos(datos: List[Item]):
#     # Extraer los datos de mes y monto para el gráfico
#     meses = [item.mes for item in datos]
#     montos = [item.monto for item in datos]

#     # Crear el gráfico de barras
#     plt.bar(meses, montos)
#     plt.xlabel("Month")
#     plt.ylabel("USD")
#     plt.title("Monthly billing")

#     # Guardar el gráfico en un archivo JPEG con alta calidad (calidad 95)
#     plt.savefig("grafico.jpg", format="jpeg", quality=95)

#     # Cerrar la figura para liberar memoria
#     plt.close()

#     # Devolver la imagen generada como respuesta
#     return FileResponse("grafico.jpg", media_type="image/jpeg")

# @app.post("/stringToDate/")
# async def string_to_date(texto_model: TextoModel):
#     try:
#         texto = texto_model.texto
#         extracted_dates = []
#         dates = search_dates(texto)
#         if dates is not None:
#             for d in dates:
#                 extracted_dates.append(str(d[1]))
#         else:
#             extracted_dates.append('None')

#         print(extracted_dates)
#         return extracted_dates
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Error processing the text: " + str(e))

# @app.post("/stringToDate/")
# async def string_to_date(request: Request):
#     try:
#         data = await request.json()
#         texto = data.get("texto", "")
#         extracted_dates = []
#         dates = search_dates(texto)
#         if dates is not None:
#             for d in dates:
#                 extracted_dates.append(str(d[1]))
#         else:
#             extracted_dates.append('None')

#         print(extracted_dates)
#         return JSONResponse(content=jsonable_encoder(extracted_dates))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Error processing the text: " + str(e))

@app.post("/stringToDate/")
async def string_to_date(request: Request):
    try:
        data = await request.json()
        texto = data.get("texto", "")
        extracted_dates = []
        dates = search_dates(texto)
        if dates is not None:
            for d in dates:
                extracted_dates.append(d[1])
        else:
            extracted_dates.append(None)

        print(extracted_dates)
        return JSONResponse(content=jsonable_encoder(extracted_dates))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing the text: " + str(e))