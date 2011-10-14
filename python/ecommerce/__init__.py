"""Ecommerce module for ILHSA SA
by Alejo Sanchez, Jose Luis Campanello and Mariano Goldsman
"""

# Initialize module
# Find this user/host configuration
#   Try current directory or standard locations
dirs = [ "./config", "/etc/ecommerce", 
# Exported names
__all__ = [ "test" ]

if __name__ == "__main__":
    print "Exports: ", __all__
