from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os
import vtracer

app = FastAPI()

# Directorio para guardar los archivos de entrada y salida
input_dir = "input_images"
output_dir = "output_images"

# Asegurarse de que los directorios existan
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Ruta para cargar y convertir una imagen
@app.post("/convert/")
async def convert_image(file: UploadFile):
    try:
        # Ruta de entrada y salida
        input_path = os.path.join(input_dir, file.filename)
        output_path = os.path.join(output_dir, file.filename.replace(".jpg", ".svg"))

        # Guardar la imagen de entrada
        with open(input_path, "wb") as image_file:
            image_file.write(file.file.read())

        # Convertir la imagen
        vtracer.convert_image_to_svg_py(input_path, output_path)

        # Devolver el archivo SVG convertido al usuario
        return FileResponse(output_path, media_type="image/svg+xml", filename=file.filename.replace(".jpg", ".svg"))
        # Devolver el archivo SVG convertido al usuario
        #return FileResponse(output_path, media_type="image/svg+xml", filename=file.filename.replace(".jpg", ".svg"))

    except Exception as e:
        # Manejo de errores
        raise HTTPException(status_code=500, detail=f"Error durante la conversión: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
