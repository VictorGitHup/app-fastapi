from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import vtracer
import os
import uuid
import aiofiles


app = FastAPI()

# Directorio donde se guardarán los archivos convertidos de manera permanente
output_directory = "converted"
os.makedirs(output_directory, exist_ok=True)

@app.post("/convert-to-svg/")
async def convert_to_svg(file: UploadFile = File(...)):
    # Verificar el formato del archivo
    if file.content_type not in ["image/jpeg","image/jpg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file format.")

    # Preparar el nombre del archivo de entrada y salida
    filename_without_extension = os.path.splitext(file.filename)[0]
    unique_filename = f"{filename_without_extension}_{uuid.uuid4()}"
    input_path = os.path.join(output_directory, f"{unique_filename}.{file.content_type.split('/')[-1]}")
    output_path = os.path.join(output_directory, f"{unique_filename}.svg")

    # Guardar el archivo subido de manera temporal
    async with aiofiles.open(input_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write

    # Convertir la imagen a SVG
    # Aquí estamos utilizando los valores predeterminados para la conversión
    vtracer.convert_image_to_svg_py(input_path, output_path)

    # Suponiendo que tienes un mecanismo para servir estos archivos, por ejemplo, un servidor estático
    # La URL podría ser algo como 'http://<your-domain>/<path-to-static-files>/<output_filename>'
    converted_url = f"https://18.218.25.223/converted/{unique_filename}.svg"

    # Eliminar el archivo original después de la conversión para ahorrar espacio
    os.remove(input_path)

    # Devolver la URL completa como respuesta
    return {"url": converted_url}

# Endpoint para servir los archivos convertidos
@app.get("/converted/{filename}", response_class=FileResponse)
async def get_converted_file(filename: str):
    file_path = os.path.join(output_directory, filename)
    return FileResponse(file_path)
