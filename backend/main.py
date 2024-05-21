from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from domain.info import info_router
from domain.wav import wav

app = FastAPI()

app.include_router(info_router.router)
app.include_router(wav.router)

# CORS 이슈 해결 -> 접근 허용할 origin 추가
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)