def test_connect1(qtbot):
    host = (host_ip, 80)
    relay = kmRelay.KMRelay(host)
    relay.user = 'astro'
    relay.password = 'astro'
    value = relay.getRelay('/status.xml')

    assert value.reason == 'OK'


def test_connect2(qtbot):
    host = (host_ip, 80)
    relay = kmRelay.KMRelay(host)
    relay.user = 'astro'
    relay.password = ''
    value = relay.getRelay('/status.xml')

    assert value.status_code == 401


def test_connect3(qtbot):
    host = (host_ip, 80)
    relay = kmRelay.KMRelay(host)
    relay.user = ''
    relay.password = 'astro'
    value = relay.getRelay('/status.xml')

    assert value.status_code == 401


def test_connect4(qtbot):
    host = (host_ip, 8)
    relay = kmRelay.KMRelay(host)
    relay.user = ''
    relay.password = ''
    value = relay.getRelay('/status.xml')

    assert value is None


def test_connect5(qtbot):
    host = ('192.168.2.255', 80)
    relay = kmRelay.KMRelay(host)
    relay.user = ''
    relay.password = ''
    value = relay.getRelay('/status.xml')

    assert value is None


def test_connect6(qtbot):
    relay = kmRelay.KMRelay(None)
    relay.user = ''
    relay.password = ''
    value = relay.getRelay('/status.xml')

    assert value is None
