class DummyEvent:
    """ An event that can be used to simulate a real event for testing."""

    def __init__(self, event_type):
        self.type = event_type
