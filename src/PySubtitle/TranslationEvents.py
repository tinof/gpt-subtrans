class SimpleEvents:
    """Simple event system replacement for the events package"""

    def __init__(self):
        self._handlers = {}

    def __getattr__(self, name):
        if name not in self._handlers:
            self._handlers[name] = EventHandler()
        return self._handlers[name]

class EventHandler:
    """Simple event handler that supports += and -= operators"""

    def __init__(self):
        self._callbacks = []

    def __iadd__(self, callback):
        if callback not in self._callbacks:
            self._callbacks.append(callback)
        return self

    def __isub__(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)
        return self

    def __call__(self, *args, **kwargs):
        for callback in self._callbacks:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                # Log the error but don't stop other callbacks
                import logging
                logging.warning(f"Error in event callback: {e}")

class TranslationEvents(SimpleEvents):
    """Event system for translation progress notifications"""
    pass

