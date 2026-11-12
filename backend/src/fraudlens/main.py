"""Local foundation application; only health is implemented in phase 3."""
from typing import Annotated

from fastapi import Depends, FastAPI, Request

from fraudlens.contracts import Health
from fraudlens.settings import Settings, load_settings


def get_settings(request: Request) -> Settings:
    """Dependency override point scoped to this application instance."""
    return request.app.state.settings


def create_app(settings: Settings | None = None) -> FastAPI:
    app = FastAPI(title='FraudLens AI')
    app.state.settings = settings if settings is not None else load_settings()

    @app.get('/api/health', response_model=Health)
    def health(config: Annotated[Settings, Depends(get_settings)]) -> Health:
        return Health(status='ok', mode=config.mode)

    return app


app = create_app()
