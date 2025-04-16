import pkg_resources

libraries = [
    "python-telegram-bot",
    "python-dotenv",
    "yandex-cloud-ml-sdk",
    "SQLAlchemy",
    "psycopg2-binary"
]

for library in libraries:
    try:
        version = pkg_resources.get_distribution(library).version
        print(f"{library}: {version}")
    except pkg_resources.DistributionNotFound:
        print(f"{library}: Not installed")