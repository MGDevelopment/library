"""TMK module for ILHSA SA

This module has support libraries for stage 0 (static content on IIS).

Part of the module will probably be deprecated later, other parts will
survive to support data extraction.

by Jose Luis Campanello
"""

def waste(x):
    return x + "/" + x

# Exported names
__all__ = [ "support", "url" ]

