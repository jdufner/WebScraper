import unittest
from datetime import datetime
from picturechoice.server.choice import Choice


class ChoiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_when_init_expect_answered_initialized(self):
        # arrange

        # act
        choice = Choice(datetime.now(), 'first', 'second')

        # assert
        self.assertIsNotNone(choice.answered)
