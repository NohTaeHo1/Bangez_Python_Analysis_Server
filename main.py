from fastapi import FastAPI

from app.routes.schedule_route import start_scheduler, shutdown_scheduler
from app.routes.startup_route import save_mongodb

app = FastAPI()  # FastAPI 인스턴스를 생성합니다.


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.on_event("startup")
def startup():
    start_scheduler()
    save_mongodb()


@app.on_event("shutdown")
def shutdown():
    shutdown_scheduler()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", reload=True, host="127.0.0.1", port=8000, log_level="info")