from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
from database import engine
import models
# from routers.user import router as user_router

app = FastAPI(
    title="Drive or Die",
    description="API Fahrschule",
    version="1.0.0"
)

# app.include_router(user_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        errors.append({
            "field": err["loc"][-1],
            "message": err["msg"]
        })

    return JSONResponse(
        status_code=422,
        content={"errors": errors}
    )

@app.get("/")
def root():
    return {"message": "API läuft"}



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
