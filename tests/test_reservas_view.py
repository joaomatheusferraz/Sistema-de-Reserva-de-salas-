import importlib


def test_criar_controller_reservas_sem_firebase(monkeypatch):
    mod = importlib.import_module("views.reservas_view")

    class ControllerQueQuebra:
        def __init__(self):
            raise RuntimeError("Credenciais do Firebase não configuradas")

    monkeypatch.setattr(mod, "ReservaController", ControllerQueQuebra, raising=True)

    controller = mod.criar_controller_reservas()

    assert controller is None
