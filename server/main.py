from server.routers import flights, airports, statistics, geography
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

tags_metadata=[
    { "name": "flights" },
    { "name": "airports"},
    { "name": "statistics"},
    { "name": "geography"}
]

app = FastAPI(openapi_tags=tags_metadata)
build_path = Path(__file__).parent.parent / 'dist'

app.include_router(flights.router, prefix="/api")
app.include_router(airports.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")
app.include_router(geography.router, prefix="/api")

@app.get("/", include_in_schema=False)
@app.get("/new", include_in_schema=False)
@app.get("/flights", include_in_schema=False)
@app.get("/settings", include_in_schema=False)
async def root():
    with open(build_path / 'index.html', "r") as file:
        html = file.read()
    return HTMLResponse(content=html)

app.mount("/", StaticFiles(directory=build_path), name="app")
