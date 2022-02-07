from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# from os.path import dirname, join

# current_dir = dirname(__file__)  # this will be the location of the current .py file
# template_path = join(current_dir, "templates")
templates = Jinja2Templates(directory="src/app/templates")


app = FastAPI()
app.mount(
    "/src/app/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)

stub = {
    "table_data": {
        
    }
}

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "id": id})
