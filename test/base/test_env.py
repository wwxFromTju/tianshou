import time
import pytest
import numpy as np
from tianshou.env import FrameStack, VectorEnv, SubprocVectorEnv, RayVectorEnv

if __name__ == '__main__':
    from env import MyTestEnv
else:  # pytest
    from test.base.env import MyTestEnv


def test_framestack(k=4, size=10):
    env = MyTestEnv(size=size)
    fsenv = FrameStack(env, k)
    fsenv.seed()
    obs = fsenv.reset()
    assert abs(obs - np.array([0, 0, 0, 0])).sum() == 0
    for i in range(5):
        obs, rew, done, info = fsenv.step(1)
    assert abs(obs - np.array([2, 3, 4, 5])).sum() == 0
    for i in range(10):
        obs, rew, done, info = fsenv.step(0)
    assert abs(obs - np.array([0, 0, 0, 0])).sum() == 0
    for i in range(9):
        obs, rew, done, info = fsenv.step(1)
    assert abs(obs - np.array([6, 7, 8, 9])).sum() == 0
    assert (rew, done) == (0, False)
    obs, rew, done, info = fsenv.step(1)
    assert abs(obs - np.array([7, 8, 9, 10])).sum() == 0
    assert (rew, done) == (1, True)
    with pytest.raises(ValueError):
        obs, rew, done, info = fsenv.step(0)
    # assert abs(obs - np.array([8, 9, 10, 10])).sum() == 0
    # assert (rew, done) == (0, True)
    fsenv.close()


def test_vecenv(size=10, num=8, sleep=0.001):
    verbose = __name__ == '__main__'
    env_fns = [
        lambda: MyTestEnv(size=size, sleep=sleep),
        lambda: MyTestEnv(size=size + 1, sleep=sleep),
        lambda: MyTestEnv(size=size + 2, sleep=sleep),
        lambda: MyTestEnv(size=size + 3, sleep=sleep),
        lambda: MyTestEnv(size=size + 4, sleep=sleep),
        lambda: MyTestEnv(size=size + 5, sleep=sleep),
        lambda: MyTestEnv(size=size + 6, sleep=sleep),
        lambda: MyTestEnv(size=size + 7, sleep=sleep),
    ]
    venv = [
        VectorEnv(env_fns),
        SubprocVectorEnv(env_fns),
    ]
    if verbose:
        venv.append(RayVectorEnv(env_fns))
    for v in venv:
        v.seed()
    action_list = [1] * 5 + [0] * 10 + [1] * 20
    if not verbose:
        o = [v.reset() for v in venv]
        for i, a in enumerate(action_list):
            o = []
            for v in venv:
                A, B, C, D = v.step([a] * num)
                if sum(C):
                    A = v.reset(np.where(C)[0])
                o.append([A, B, C, D])
            for i in zip(*o):
                for j in range(1, len(i)):
                    assert (i[0] == i[j]).all()
    else:
        t = [0, 0, 0]
        for i, e in enumerate(venv):
            t[i] = time.time()
            e.reset()
            for a in action_list:
                done = e.step([a] * num)[2]
                if sum(done) > 0:
                    e.reset(np.where(done)[0])
            t[i] = time.time() - t[i]
        print(f'VectorEnv: {t[0]:.6f}s')
        print(f'SubprocVectorEnv: {t[1]:.6f}s')
        print(f'RayVectorEnv: {t[2]:.6f}s')
    for v in venv:
        v.close()


if __name__ == '__main__':
    test_framestack()
    test_vecenv()
