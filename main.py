import sys
from link_scrapper.container import create_app

if __name__ == '__main__':
    reset = '--save' not in sys.argv
    reverse = '-r' in sys.argv or '--reverse' in sys.argv
    app = create_app(reset_visited=reset, reverse=reverse)
    try:
        app.start()
    finally:
        app.close()
