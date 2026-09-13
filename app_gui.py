import sys

from gui import run

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(130)