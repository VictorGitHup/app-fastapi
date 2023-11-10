from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import shutil
import vtracer
from starlette.responses import FileResponse
from uuid import uuid4

app = FastAPI()

# Directorios para guardar los archivos de entrada y salida
input_dir = "/input_images"  # Debería ser una ruta absoluta en producción
output_dir = "/output_images"  # Debería ser una ruta absoluta en producción

# Crear directorios si no existen
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

@app.post("/convert/")
async def convert_image(request: Request, file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Archivo no soportado. Solo se aceptan imágenes JPEG o PNG.")

    unique_id = str(uuid4())
    filename = f"{unique_id}-{os.path.basename(file.filename)}"
    input_path = os.path.join(input_dir, filename)
    output_filename = f"{unique_id}.svg"
    output_path = os.path.join(output_dir, output_filename)

    try:
        # Guardar la imagen de entrada
        with open(input_path, "wb") as image_file:
            shutil.copyfileobj(file.file, image_file)
        
        # Convertir la imagen a SVG
        # Asegúrese de que vtracer.convert_image_to_svg_py tome el path de entrada y salida correctamente
        vtracer.convert_image_to_svg_py(input_path, output_path)

        # Generar URL de descarga para el archivo SVG
        file_url = request.url_for('get_svg_image', path=output_filename)

        # Devolver la URL del archivo SVG convertido
        return JSONResponse(
            status_code=200,
            content={
                "url": str(file_url),
                "filename": output_filename
            }
        )

    except Exception as e:
        # Manejo de errores
        raise HTTPException(status_code=500, detail=f"Error durante la conversión: {str(e)}")

    finally:
        # Opcional: Puede que no quieras eliminar el archivo de entrada después de la conversión
        # Esto puede ser útil para guardar un historial de lo que se ha procesado
        # Si decides eliminarlo, descomenta la línea siguiente
        # os.remove(input_path)
        pass

@app.get("/images/{path:path}", name="get_svg_image")
async def get_svg_image(path: str):
    output_path = os.path.join(output_dir, path)
    if not os.path.isfile(output_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return FileResponse(output_path, media_type="image/svg+xml")

# Aquí se pueden añadir más rutas y funcionalidades al API
