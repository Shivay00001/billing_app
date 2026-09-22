"""Smoke tests for the license manager (stdlib only, no network, no GUI)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from license.license_manager import LicenseManager


class FakeDB:
    def __init__(self, row=None):
        self.row = row

    def fetchone(self, *a, **k):
        return self.row

    def execute(self, *a, **k):
        pass

    def commit(self):
        pass

    def set_setting(self, *a, **k):
        pass


def test_trial_not_exhausted_allows_invoice():
    lm = LicenseManager(FakeDB({"invoices_created": 3, "invoice_limit": 10}))
    ok, msg = lm.can_create_invoice()
    assert ok is True, msg


def test_trial_exhausted_blocks_invoice():
    lm = LicenseManager(FakeDB({"invoices_created": 10, "invoice_limit": 10}))
    ok, msg = lm.can_create_invoice()
    assert ok is False
    assert msg, "expected a human-readable block message"


def test_check_trial_exhausted_helper():
    lm = LicenseManager(FakeDB())
    assert lm._check_trial_exhausted({"invoices_created": 0, "invoice_limit": 10}) is False
    assert lm._check_trial_exhausted({"invoices_created": 10, "invoice_limit": 10}) is True
    assert lm._check_trial_exhausted(None) is False


if __name__ == "__main__":
    test_trial_not_exhausted_allows_invoice()
    test_trial_exhausted_blocks_invoice()
    test_check_trial_exhausted_helper()
    print("license smoke tests: 3 passed")
