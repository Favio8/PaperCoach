import uvicorn

from papercoach.config import Settings


def main() -> None:
    settings = Settings()
    uvicorn.run(
        "papercoach.app:create_app",
        host=settings.host,
        port=settings.port,
        factory=True,
        reload=False,
    )
