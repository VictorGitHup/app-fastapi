from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import io
from vtracer import convert_image_to_svg_py
import shutil
import os

# Resto de tu código aquí


# Resto de tu código aquí


app = FastAPI()

@app.post("/convert-to-svg/")
async def convert_to_svg(file: UploadFile = File(...)):
    # Verificar el formato del archivo
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file format.")

    # Preparar el nombre del archivo de entrada y salida
    file_extension = file.filename.split('.')[-1]
    if file_extension.lower() not in ['jpg', 'jpeg', 'png']:
        raise HTTPException(status_code=400, detail="Invalid file extension.")
    
    input_path = f"temp/{file.filename}"
    output_path = f"temp/{file.filename}.svg"

    # Guarda el archivo subido en el sistema de archivos temporalmente
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convertir la imagen a SVG
    convert_image_to_svg_py(input_path, output_path)

    # Leer el archivo SVG resultante para enviarlo de vuelta al usuario
    with open(output_path, "rb") as svg_file:
        svg_content = svg_file.read()

    # Eliminar archivos temporales
    os.remove(input_path)
    os.remove(output_path)

    # Crear una respuesta de streaming para enviar el SVG directamente
    response = StreamingResponse(io.BytesIO(svg_content), media_type="image/svg+xml")
    response.headers["Content-Disposition"] = f"attachment; filename={file.filename}.svg"

    return response
