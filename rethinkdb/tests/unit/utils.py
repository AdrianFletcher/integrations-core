# (C) Datadog, Inc. 2020-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from typing import Any, Dict, Iterator, List, Type

import rethinkdb


class MockConnectionInstance(object):
    def __init__(self, parent, *args, **kwargs):
        # type: (MockConnection, *Any, **Any) -> None
        self._parent = parent

    # Implement the connection instance interface used by RethinkDB.

    def connect(self, timeout):
        # type: (float) -> MockConnection
        return self._parent

    def is_open(self):
        # type: () -> bool
        return True

    def run_query(self, query, noreply):
        # type: (Any, bool) -> Iterator[Dict[str, Any]]
        return self._parent.mock_rows()


class MockConnection(rethinkdb.net.Connection):
    """
    A RethinkDB connection type that mocks all queries by sending a deterministic set of rows.

    Inspired by:
    https://github.com/rethinkdb/rethinkdb-python/blob/9aa68feff16dc984406ae0e276f24e87df89b334/rethinkdb/asyncio_net/net_asyncio.py
    """

    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        rows = kwargs.pop('rows')
        super(MockConnection, self).__init__(MockConnectionInstance, *args, **kwargs)
        self.rows = rows  # type: List[Dict[str, Any]]

    def mock_rows(self):
        # type: () -> Iterator[Dict[str, Any]]
        for row in self.rows:
            yield row


class MockRethinkDB(rethinkdb.RethinkDB):
    def __init__(self, connection_type):
        # type: (Type[rethinkdb.net.Connection]) -> None
        super(MockRethinkDB, self).__init__()
        self.connection_type = connection_type