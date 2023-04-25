from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.routers import user, project, image
from database.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

security = HTTPBasic()

app.include_router(user.router)
app.include_router(project.router)
app.include_router(image.router)


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "testuser"
    correct_password = "testpassword"
    if (credentials.username != correct_username or
            credentials.password != correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/protected")
async def read_protected(username: str = Depends(get_current_username)):
    return {"username": username}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
