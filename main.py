from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from starlette.responses import FileResponse
from pathlib import Path
import shutil
import uuid

from vtracer import convert_image_to_svg_py

app = FastAPI()

# Directorio donde se guardarán los archivos convertidos de manera temporal
temp_directory = "temp"
output_directory = "converted"

# Asegúrate de que los directorios existen
Path(temp_directory).mkdir(exist_ok=True)
Path(output_directory).mkdir(exist_ok=True)

@app.post("/convert-to-svg/")
async def convert_to_svg(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Verificar el formato del archivo
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file format.")
    
    # Generar un nombre de archivo único para evitar colisiones
    file_name = f"{uuid.uuid4()}.{file.filename.rsplit('.', 1)[-1].lower()}"
    
    input_path = Path(temp_directory) / file_name
    output_path = Path(output_directory) / f"{file_name}.svg"

    # Guardar el archivo subido temporalmente
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Llamar a la función de conversión en segundo plano
    background_tasks.add_task(
        convert_and_delete, input_path, output_path
    )

    # Generar un enlace a la imagen convertida
    converted_url = f"/download/{file_name}.svg"
    
    # Devolver la URL completa como respuesta
    return {"url": converted_url}

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = Path(output_directory) / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(path=file_path, filename=filename)

async def convert_and_delete(input_path: Path, output_path: Path):
    # Convertir la imagen a SVG
    try:
        convert_image_to_svg_py(input_path, output_path)
    except Exception as e:
        print(f"Error during conversion: {e}")
        input_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Error during conversion.")
    finally:
        # Eliminar el archivo de entrada temporal
        input_path.unlink(missing_ok=True)

# Asegúrate de que el directorio de salida esté limpio al iniciar y al salir de la aplicación
@app.on_event("startup")
async def startup_event():
    shutil.rmtree(output_directory, ignore_errors=True)
    Path(output_directory).mkdir(exist_ok=True)

@app.on_event("shutdown")
async def shutdown_event():
    shutil.rmtree(output_directory, ignore_errors=True)
