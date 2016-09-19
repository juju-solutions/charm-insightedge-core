#!/usr/bin/env python3

import unittest
import amulet


class TestDeploy(unittest.TestCase):
    """
    Trivial deployment test for Apache Hadoop Plugin.

    This charm cannot do anything useful by itself, so integration testing
    is done in the bundle.  However, becaues it's a subordinate, it requires
    a principle to confirm that it deploys.
    """

    def test_deploy(self):
        self.d = amulet.Deployment(series='trusty')
        self.d.load({
            'services': {
                'spark': {'charm': 'apache-spark'},
                'insightedge': {'charm': 'insightedge-core'},
            },
            'relations': [('spark', 'insightedge')],
        })
        self.d.setup(timeout=900)
        self.d.sentry.wait(timeout=1800)
        self.unit = self.d.sentry['insightedge'][0]


if __name__ == '__main__':
    unittest.main()
