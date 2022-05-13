import os
from snapshot import Snapshot


class Snapshot$$:
    def __init__(self, snapshot: Snapshot):
        self.snapshot = snapshot

    async def execute(self):
        pass


class RemoveSummary$$:
    def __init__(self, snapshot: Snapshot):
        self.snapshot = snapshot

    async def execute(self):
        if self.snapshot.address_book.perform_actions_summary.exists():
            os.remove(self.snapshot.address_book.perform_actions_summary)

