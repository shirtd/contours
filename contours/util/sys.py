from multiprocessing import Pool
import sys, time, gc
import pickle as pkl
import numpy as np


def pmap(fun, x, *args, **kw):
    pool = Pool()
    f = partial(fun, *args, **kw)
    try:
        y = pool.map(f, x)
    except KeyboardInterrupt as e:
        print(e)
        pool.close()
        pool.join()
        sys.exit()
    pool.close()
    pool.join()
    return y

def load_dat(fname, pad=0, normalize=True):
    _, ext = os.path.splitext(fname)
    dat = np.loadtxt(fname, skiprows=6 if ext == '.asc' else 0)
    dat = dat[pad:-pad,pad:-pad] if pad > 0 else dat
    return util.stats.scale(dat) if normalize else dat
    # (dat - dat.min()) / (dat.max() - dat.min()) if normalize else dat

def load_pkl(fcache):
    sys.stdout.write('[ loading %s...' % fcache)
    sys.stdout.flush()
    t0 = time.time()
    with open(fcache, 'rb') as f:
        gc.disable()
        dat = pkl.load(f)
        gc.enable()
    print(' %0.3fs' % (time.time() - t0))
    return dat

def save_pkl(dat, fcache):
    sys.stdout.write('[ saving %s...' % fcache)
    sys.stdout.flush()
    t0 = time.time()
    with open(fcache, 'wb') as f:
        gc.disable()
        pkl.dump(dat, f)
        gc.enable()
    print(' %0.3fs' % (time.time() - t0))
