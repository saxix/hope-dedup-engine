import pytest

from hope_dedup_engine.state import state
from hope_dedup_engine.utils.flags import development, server_address


@pytest.mark.parametrize("debug", [True, False])
def test_development(rf, settings, debug):
    settings.DEBUG = debug
    request = rf.get("/", HTTP_HOST="127.0.0.1")
    with state.configure(request=request):
        assert development() is debug


@pytest.mark.parametrize("ip", ["127.0.0.1", "192.168.66.66"])
def test_server_address(rf, ip, settings):
    settings.ALLOWED_HOSTS = [ip]
    request = rf.get("/", HTTP_HOST=ip)
    with state.configure(request=request):
        assert server_address(ip)
