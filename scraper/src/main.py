from fastapi import FastAPI

app = FastAPI()


@app.get("/scrape/{amount}", summary="Scrape certain amount of images")
def scrape(amount: int):
    return amount
