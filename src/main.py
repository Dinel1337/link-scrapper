"""Точка входа в приложение."""
from link_scrapper.container import create_app

if __name__ == "__main__":
    listener = create_app()
    listener.start()
