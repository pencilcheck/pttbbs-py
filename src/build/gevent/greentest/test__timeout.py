import greentest
import gevent
DELAY = 0.01


class TestDirectRaise(greentest.TestCase):
    switch_expected = False

    def test_direct_raise_class(self):
        try:
            raise gevent.Timeout
        except gevent.Timeout, t:
            assert not t.pending, repr(t)

    def test_direct_raise_instance(self):
        timeout = gevent.Timeout()
        try:
            raise timeout
        except gevent.Timeout, t:
            assert timeout is t, (timeout, t)
            assert not t.pending, repr(t)


class Test(greentest.TestCase):

    def test_with_timeout(self):
        self.assertRaises(gevent.Timeout, gevent.with_timeout, DELAY, gevent.sleep, DELAY * 2)
        X = object()
        r = gevent.with_timeout(DELAY, gevent.sleep, DELAY * 2, timeout_value=X)
        assert r is X, (r, X)
        r = gevent.with_timeout(DELAY * 2, gevent.sleep, DELAY, timeout_value=X)
        assert r is None, r


if __name__ == '__main__':
    greentest.main()
