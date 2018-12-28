# -*- coding: utf-8 -*-

# Install twisted asyncio loop

#import importlib
#import sys
#if 'twisted.internet.reactor' in sys.modules:
#    del sys.modules['twisted.internet.reactor']
def _install_asyncio_reactor():
    try:
        import asyncio
        from twisted.internet import asyncioreactor
    except ImportError:
        pass
    else:
        # FIXME maybe we don't need this? Adapted from pytest_twisted
        from twisted.internet.error import ReactorAlreadyInstalledError
        try:
            asyncioreactor.install(asyncio.get_event_loop())
        except ReactorAlreadyInstalledError:
            import twisted.internet.reactor
            if not isinstance(twisted.internet.reactor,
                              asyncioreactor.AsyncioSelectorReactor):
                raise
_install_asyncio_reactor()
del _install_asyncio_reactor
  


