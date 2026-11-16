"""The supported local API command must stay on loopback."""

from fraudlens import local_api


def test_local_api_launcher_uses_fixed_loopback_bind(monkeypatch):
    calls = []
    for name in ("APP_HOST", "FRAUDLENS_API_HOST", "UVICORN_HOST"):
        monkeypatch.setenv(name, "0.0.0.0")
    monkeypatch.setattr(local_api.uvicorn, "run", lambda *args, **kwargs: calls.append((args, kwargs)))

    local_api.main()

    assert calls == [
        (("fraudlens.main:app",), {"host": "127.0.0.1", "port": 8000, "reload": False})
    ]
