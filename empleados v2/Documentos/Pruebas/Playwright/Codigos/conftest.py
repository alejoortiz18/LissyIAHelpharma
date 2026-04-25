import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "recuperacion: pruebas del flujo de recuperación de contraseña",
    )
