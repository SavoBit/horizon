from horizon.test import helpers as test


class ConnectivityTests(test.TestCase):
    # Unit tests for connectivity.
    def test_me(self):
        self.assertTrue(1 + 1 == 2)
