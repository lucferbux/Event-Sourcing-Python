from eventsourcing.application.sqlalchemy import SimpleApplication
from eventsourcing.exceptions import ConcurrencyError
from eventsourcing.application.sqlalchemy import SimpleApplication
from eventsourcing.exceptions import ConcurrencyError
from world import World
from eventsourcing.utils.random import encode_random_bytes
import os


# Keep this safe.
cipher_key = encode_random_bytes(num_bytes=32)

# Optional cipher key (random bytes encoded with Base64).
os.environ['CIPHER_KEY'] = cipher_key

# SQLAlchemy-style database connection string.
os.environ['DB_URI'] = 'sqlite:///:memory:'


# Construct simple application (used here as a context manager).
with SimpleApplication(persist_event_type=World.Event) as app:

    # 1. Call library factor method as 'Geekshub' user.

    # 2. Check if the ruler is Geekshub

    # 3. Change the ruler

    # 4. Add  a feature to your world

    # 5. Save version of event

    # 6. Add a new feature

    # 7. Print the history

