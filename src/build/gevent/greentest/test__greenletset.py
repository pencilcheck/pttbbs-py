import time
import greentest
import gevent
from gevent import pool

DELAY = 0.1


class Undead(object):

    def __init__(self):
        self.shot_count = 0

    def __call__(self):
        while True:
            try:
                gevent.sleep(1)
            except:
                self.shot_count += 1


class Test(greentest.TestCase):

    def test_basic(self):
        DELAY = 0.05
        s = pool.GreenletSet()
        s.spawn(gevent.sleep, DELAY)
        assert len(s) == 1, s
        s.spawn(gevent.sleep, DELAY * 2.)
        assert len(s) == 2, s
        gevent.sleep(DELAY * 3. / 2.)
        assert len(s) == 1, s
        gevent.sleep(DELAY)
        assert not s, s

    def test_waitall(self):
        s = pool.GreenletSet()
        s.spawn(gevent.sleep, DELAY)
        s.spawn(gevent.sleep, DELAY * 2)
        assert len(s) == 2, s
        start = time.time()
        s.join(raise_error=True)
        delta = time.time() - start
        assert not s, s
        assert len(s) == 0, s
        assert DELAY * 1.9 <= delta <= DELAY * 2.5, (delta, DELAY)

    def test_kill_block(self):
        s = pool.GreenletSet()
        s.spawn(gevent.sleep, DELAY)
        s.spawn(gevent.sleep, DELAY * 2)
        assert len(s) == 2, s
        start = time.time()
        s.kill(block=True)
        assert not s, s
        assert len(s) == 0, s
        delta = time.time() - start
        assert delta < DELAY * 0.8, delta

    def test_kill_noblock(self):
        s = pool.GreenletSet()
        s.spawn(gevent.sleep, DELAY)
        s.spawn(gevent.sleep, DELAY * 2)
        assert len(s) == 2, s
        s.kill(block=False)
        assert len(s) == 2, s
        gevent.sleep(0)
        assert not s, s
        assert len(s) == 0, s

    def test_kill_fires_once(self):
        u1 = Undead()
        u2 = Undead()
        p1 = gevent.spawn(u1)
        p2 = gevent.spawn(u2)

        def check(count1, count2):
            assert p1, p1
            assert p2, p2
            assert not p1.dead, p1
            assert not p2.dead, p2
            self.assertEqual(u1.shot_count, count1)
            self.assertEqual(u2.shot_count, count2)

        gevent.sleep(0.01)
        s = pool.GreenletSet([p1, p2])
        assert len(s) == 2, s
        check(0, 0)
        s.killone(p1, block=False)
        check(0, 0)
        gevent.sleep(0)
        check(1, 0)
        s.killone(p1)
        check(1, 0)
        s.killone(p1)
        check(1, 0)
        s.kill(block=False)
        s.kill(block=False)
        s.kill(block=False)
        check(1, 0)
        gevent.sleep(DELAY)
        check(1, 1)
        X = object()
        kill_result = gevent.with_timeout(DELAY, s.kill, block=True, timeout_value=X)
        assert kill_result is X, repr(kill_result)
        assert len(s) == 2, s
        check(1, 1)

    def test_killall_subclass(self):
        p1 = GreenletSubclass.spawn(lambda: 1 / 0)
        p2 = GreenletSubclass.spawn(lambda: gevent.sleep(10))
        s = pool.GreenletSet([p1, p2])
        s.kill(block=True)


class GreenletSubclass(gevent.Greenlet):
    pass


if __name__ == '__main__':
    greentest.main()
