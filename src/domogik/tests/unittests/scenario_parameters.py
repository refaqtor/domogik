# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Unit tests.

Implements
==========

- ScenarioCronParameterTest

@author: Maxence Dunnewind <maxence@dunnewind.net>
@copyright: (C) 2013 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import unittest
import logging
import datetime

from domogik.common.scenario.parameters.cron import CronParameter
from domogik.common.cron import CronExpression


class ScenarioCronParameterTest(unittest.TestCase):
    """ Test CronParameter
    """

    def setUp(self):
        """ Create a Cron Parameter object
        """
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
        self._obj = CronParameter(log=logging)
        self._triggered = False

    def tearDown(self):
        """ Destroy cron object
        """
        del self._obj
        self._triggered = False

    def triggered(self, payload=None):
        """ Called when the trigger is called """
        self._trigger = True

    def test_fill_with_data(self):
        """ TEst fill method
        """
        parameters = {"cron": "*/5 * * * *"}
        self._obj.fill(params=parameters)
        self.assertTrue(self._obj.expr.__str__() == CronExpression(parameters["cron"]).__str__(),
                        "Cron Expression not correctly setup")

    def test_fill_with_empty_data(self):
        """ TEst fill method with no cron expression
        """
        # Test without cron expression
        parameters = {}
        self._obj.fill(params=parameters)
        self.assertTrue(self._obj.expr is None, "CronParameter expr should be empty")

    def test_evaluate_should_run(self):
        """ Setup a cron object which should run every minute
        """
        parameters = {"cron": "* * * * *"}
        self._obj.fill(params=parameters)
        self.assertTrue(self._obj.evaluate())

    def test_evaluate_should_not_run(self):
        """ Setup a cron object which should run in 10 minutes
        from now and ensure it does not evaluate to True
        """

        now = datetime.datetime.now()
        minute = (now.minute + 10) % 60
        parameters = {"cron": "%s * * * *" % minute }
        self._obj.fill(params=parameters)
        self.assertFalse(self._obj.evaluate())

if __name__ == "__main__":
    unittest.main()
