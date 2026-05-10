import sys
from link_scrapper.infra.db import SessionLocal, init_db
from link_scrapper.infra.repositories import LinkCommandRepository

if __name__ == '__main__':
    init_db()
    if len(sys.argv) > 1 and sys.argv[1] == '-d':
        session = SessionLocal()
        repo = LinkCommandRepository(session)
        deleted = repo.delete_all()
        session.close()
        print(f'Deleted {deleted} link(s) from database.')
    else:
        from link_scrapper.container import create_app
        app = create_app()
        app.start()
