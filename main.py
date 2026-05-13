import sys
from link_scrapper.container import create_app

if __name__ == '__main__':
    reset = '--save' not in sys.argv
    reverse = '-r' in sys.argv or '--reverse' in sys.argv
    auto_interval = 0
    skip = 0
    count = 0

    if '--auto' in sys.argv:
        idx = sys.argv.index('--auto')
        if idx + 1 < len(sys.argv):
            try:
                auto_interval = int(sys.argv[idx+1])
            except ValueError:
                print("Usage: --auto N (seconds)")
                sys.exit(1)
        else:
            print("Please specify interval in seconds after --auto")
            sys.exit(1)

    if '--skip' in sys.argv:
        idx = sys.argv.index('--skip')
        if idx + 1 < len(sys.argv):
            try:
                skip = int(sys.argv[idx+1])
            except ValueError:
                print("Usage: --skip N (number of links to skip)")
                sys.exit(1)
        else:
            print("Please specify number of links to skip")
            sys.exit(1)

    if '--count' in sys.argv:
        idx = sys.argv.index('--count')
        if idx + 1 < len(sys.argv):
            try:
                count = int(sys.argv[idx+1])
            except ValueError:
                print("Usage: --count N (number of chats to process)")
                sys.exit(1)
        else:
            print("Please specify number of chats to process")
            sys.exit(1)

    app = create_app(reset_visited=reset, reverse=reverse,
                     auto_interval=auto_interval, skip=skip, count=count)
    try:
        app.start()
    finally:
        app.close()
