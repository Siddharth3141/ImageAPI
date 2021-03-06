import os

from fastapi import FastAPI, Path, Query, HTTPException, status
from fastapi.responses import FileResponse

from .database import (
    get_image_by_id,
    get_image_id,
    upload,
    get_images_by_label,
    get_image_id,
    delete_image_by_id,
    delete_category,
)
from .utils import delete_image, generate_pallet, to_png

app = FastAPI(
    title="Image API",
    description="An API where you can share labeled images and generate color pallets for images.",
    docs_url="/",
    redoc_url=None,
)

if not os.path.exists("images"):
    os.mkdir("images")


@app.get("/image/{id}")
async def get_image(
    id: int = Path(None, description="The id of the image that should be returned.")
):
    path = get_image_by_id(id)
    if path:
        return FileResponse(path)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.get("/images/{label}/{number}")
async def get_image_by_label(
    label: str = Path(
        None, description="The label of the image that should be returned."
    ),
    number: int = Path(
        0,
        description="The number of the image in the category that should be returned.",
    ),
):
    images = get_images_by_label(label)
    if images:
        path = images[number][0]
        return FileResponse(path)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.get("/image/get_id/{label}/{number}")
async def get_image_id_by_label(
    label: str = Path(
        None, description="The label of the image whose id should be returned."
    ),
    number: int = Path(
        None,
        description="The number of the image in the category whose id should be returned.",
    ),
):
    id = get_image_id(label, number)
    if id:
        return {"id": id}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/image/{label}/")
async def post_image(
    label: str = Path(
        None, description="The label of the image that should be uploaded."
    ),
    image: str = Query(
        None,
        description="The base 64 encoded version of the image that should be uploaded.",
    ),
):
    name = label + str(len(get_images_by_label(label)))
    path = f"images/{name}.png"
    to_png(path, image)
    upload(label, path)


@app.delete("/image/{id}")
async def delete_image_by_id(
    id: int = Path(None, description="The id of the image that should be deleted.")
):
    path = get_image_by_id(id)
    if path:
        delete_image(path)
        delete_image_by_id(id)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/images/{label}")
async def delete_images_by_label(
    label: str = Path(None, description="The label that images with should be deleted")
):
    images = get_images_by_label(label)
    if images:
        for image in images:
            delete_image(image[0])
        delete_category(label)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.put("/image/{id}")
async def update_image(
    id: int = Path(None, description="The id of the image that should be updated."),
    image: str = Query(None, description="The base 64 version of the updated image."),
):
    path = get_image_by_id(id)
    if path:
        to_png(path, image)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.get("/colorpallet/{id}}")
async def generate_colorpallet(
    id: int = Path(
        None,
        description="The id of the image that a color pallet should be generated for.",
    ),
    max_num_colors: int = Query(
        5,
        description="The maximum number of colors that should be in the color pallet that is generated.",
    ),
    rgb: bool = Query(
        False,
        description="Should the color scheme be returned as a list of RGB values?",
    ),
):
    path = get_image_by_id(id)
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    colors = generate_pallet(path, max_num_colors, rgb)
    return {"color_pallet": colors}
