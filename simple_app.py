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

    # Call library factory method.
    world = World.__create__(ruler='gods')

    # Execute commands.
    world.make_it_so('dinosaurs')
    world.make_it_so('trucks')

    version = world.__version__ # note version at this stage
    world.make_it_so('internet')

    # Assign to event-sourced attribute.
    world.ruler = 'money'

    # View current state of aggregate.
    assert world.ruler == 'money'
    assert world.history[2].what == 'internet'
    assert world.history[1].what == 'trucks'
    assert world.history[0].what == 'dinosaurs'

    print(world.history)

    # Publish pending events (to persistence subscriber).
    world.__save__()

    # Retrieve aggregate (replay stored events).
    copy = app.repository[world.id]
    assert isinstance(copy, World)

    # View retrieved state.
    assert copy.ruler == 'money'
    assert copy.history[2].what == 'internet'
    assert copy.history[1].what == 'trucks'
    assert copy.history[0].what == 'dinosaurs'

    # Verify retrieved state (cryptographically).
    assert copy.__head__ == world.__head__

    # Discard aggregate.
    world.__discard__()
    world.__save__()

    # Discarded aggregate is not found.
    assert world.id not in app.repository
    try:
        # Repository raises key error.
        app.repository[world.id]
    except KeyError:
        pass
    else:
        raise Exception("Shouldn't get here")

    # Get historical state (at version from above).
    old = app.repository.get_entity(world.id, at=version)
    assert old.history[-1].what == 'trucks' # internet not happened
    assert len(old.history) == 2
    assert old.ruler == 'gods'

    # Optimistic concurrency control (no branches).
    old.make_it_so('future')
    try:
        old.__save__()
    except ConcurrencyError:
        pass
    else:
        raise Exception("Shouldn't get here")

    # Check domain event data integrity (happens also during replay).
    events = app.event_store.get_domain_events(world.id)
    last_hash = ''
    for event in events:
        event.__check_hash__()
        assert event.__previous_hash__ == last_hash
        last_hash = event.__event_hash__

    # Verify sequence of events (cryptographically).
    assert last_hash == world.__head__

    # Project application event notifications.
    from eventsourcing.interface.notificationlog import NotificationLogReader
    reader = NotificationLogReader(app.notification_log)
    notifications = reader.read()
    notification_ids = [n['id'] for n in notifications]
    assert notification_ids == [1, 2, 3, 4, 5, 6]

    # Check records are encrypted (values not visible in database).
    record_manager = app.event_store.record_manager
    items = record_manager.get_items(world.id)
    for item in items:
        assert item.originator_id == world.id
        assert 'dinosaurs' not in item.state
        assert 'trucks' not in item.state
        assert 'internet' not in item.state