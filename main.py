import os
import shutil
import asyncio
import vtracer
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

# Directorio para guardar los archivos de entrada y salida
input_dir = "uploads"
output_dir = "converted"

# Asegurarse de que los directorios existan
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

async def delete_file_after_delay(file_path: str, delay: int):
    """Eliminar el archivo después de un retraso especificado en segundos."""
    await asyncio.sleep(delay)  # Espera 'delay' segundos antes de eliminar el archivo
    if os.path.exists(file_path):
        os.unlink(file_path)  # Eliminar el archivo después del retraso

@app.get("/status")
def get_status():
    return {"status": "Servidor FastAPI en funcionamiento."}

@app.post("/vtracer/")
async def convert_image(file: UploadFile = File(...)):
    valid_extensions = ['.jpg', '.jpeg', '.png']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in valid_extensions:
        raise HTTPException(status_code=415, detail="Formato de archivo no soportado.")

    input_path = os.path.join(input_dir, file.filename)
    output_filename = os.path.splitext(file.filename)[0] + ".svg"
    output_path = os.path.join(output_dir, output_filename)

    with open(input_path, "wb") as image_file:
        shutil.copyfileobj(file.file, image_file)

    vtracer.convert_image_to_svg(input_path, output_path)

    os.unlink(input_path)  # Eliminar el archivo de entrada después de la conversión

    response = FileResponse(output_path, media_type="image/svg+xml", filename=output_filename)
    
    # Programar la eliminación con un retraso de una hora (3600 segundos)
    asyncio.create_task(delete_file_after_delay(output_path, 3600))
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
