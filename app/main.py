from fastapi import FastAPI
from fastapi.security import HTTPBearer

from app.routers import user, project, image
from database.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

security = HTTPBearer()


app.include_router(user.router)
app.include_router(project.router)
app.include_router(image.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
