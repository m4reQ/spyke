from spyke.events import Event


def test_event_subscribe():
    result = 0

    def callback(e):
        nonlocal result
        result = e

    e = Event()
    e.subscribe(callback)
    e.invoke(1)

    assert result == 1

def test_event_subscribe_priority():
    result = 0

    def callback_low_priority(e):
        nonlocal result
        result = e

    def callback_high_priority(_):
        nonlocal result
        result = 2

    e = Event()
    e.subscribe(callback_low_priority)
    e.subscribe(callback_high_priority)
    e.invoke(1)

    assert result == 1

def test_event_subscribe_consume():
    result = 0

    def callback_first(e):
        nonlocal result
        result = e

    def callback_second(_):
        nonlocal result
        result = 2

    e = Event()
    e.subscribe(callback_first, should_consume=True)
    e.subscribe(callback_second)
    e.invoke(1)

    assert result == 1

def test_event_unsubscribe():
    result = 0

    def callback(e):
        nonlocal result
        result = e

    e = Event()
    e.subscribe(callback)
    e.unsubscribe(callback)
    e.invoke(1)

    assert result == 0

def test_event_clear_handlers():
    result = 0

    def callback(e):
        nonlocal result
        result = e

    e = Event()
    e.subscribe(callback)
    e.clear_handlers()
    e.invoke(1)

    assert result == 0
