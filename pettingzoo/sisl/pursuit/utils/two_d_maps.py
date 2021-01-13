import numpy as np

from scipy.ndimage import zoom


def rectangle_map(xs, ys, xb=0.3, yb=0.2):
    """
    Returns a 2D 'map' with a rectangle building centered in the middle
    Map is a 2D numpy array
    xb and yb are buffers for each dim representing the raio of the map to leave open on each side
    """

    rmap = np.zeros((xs, ys), dtype=np.int32)
    for i in range(xs):
        for j in range(ys):
            # are we in the rectnagle in x dim?
            if (float(i) / xs) > xb and (float(i) / xs) < (1.0 - xb):
                # are we in the rectangle in y dim?
                if (float(j) / ys) > yb and (float(j) / ys) < (1.0 - yb):
                    rmap[i, j] = -1  # -1 is building pixel flag
    return rmap


def complex_map(xs, ys):
    """
    Returns a 2D 'map' with a four different obstacles
    Map is a 2D numpy array
    """
    cmap = np.zeros((xs, ys), dtype=np.int32)
    cmap = add_rectangle(cmap, xc=0.8, yc=0.5, xl=0.1, yl=0.8)
    cmap = add_rectangle(cmap, xc=0.4, yc=0.8, xl=0.5, yl=0.2)
    cmap = add_rectangle(cmap, xc=0.5, yc=0.5, xl=0.4, yl=0.2)
    cmap = add_rectangle(cmap, xc=0.3, yc=0.1, xl=0.5, yl=0.1)
    cmap = add_rectangle(cmap, xc=0.1, yc=0.3, xl=0.1, yl=0.5)
    return cmap


def gen_map(xs, ys, n_obs, randomizer, center_bounds=[0.0, 1.0], length_bounds=[0.1, 0.5], gmap=None):
    cl, cu = center_bounds
    ll, lu = length_bounds
    if gmap is None:
        gmap = np.zeros((xs, ys), dtype=np.int32)
    for _ in range(n_obs):
        xc = randomizer.uniform(cl, cu)
        yc = randomizer.uniform(cl, cu)
        xl = randomizer.uniform(ll, lu)
        yl = randomizer.uniform(ll, lu)
        gmap = add_rectangle(gmap, xc=xc, yc=yc, xl=xl, yl=yl)
    return gmap


def multi_scale_map(xs, ys, randomizer, scales=[(3, [0.2, 0.3]), (10, [0.1, 0.2]), (30, [0.05, 0.1]), (150, [0.01, 0.05])]):
    gmap = np.zeros((xs, ys), dtype=np.int32)
    for scale in scales:
        n, lb = scale
        gmap = gen_map(xs, ys, n, randomizer, length_bounds=lb, gmap=gmap)
    return gmap


def add_rectangle(input_map, xc, yc, xl, yl):
    """
    Add a rectangle to the input map
    centered a xc, yc with dimensions xl, yl.
    Input specs are normalized wrt the map.
    """
    assert len(input_map.shape) == 2, "input_map must be a numpy matrix"

    xs, ys = input_map.shape
    xcc, ycc = int(round(xs * xc)), int(round(ys * yc))
    xll, yll = int(round(xs * xl)), int(round(ys * yl))
    if xll <= 1:
        x_lbound, x_upbound = xcc, xcc + 1
    else:
        x_lbound, x_upbound = xcc - xll / 2, xcc + xll / 2
    if yll <= 1:
        y_lbound, y_upbound = ycc, ycc + 1
    else:
        y_lbound, y_upbound = ycc - yll / 2, ycc + yll / 2

    # assert x_lbound >= 0 and x_upbound < xs, "Invalid rectangel config, x out of bounds"
    # assert y_lbound >= 0 and y_upbound < ys, "Invalid rectangel config, y out of bounds"

    x_lbound, x_upbound = np.clip([x_lbound, x_upbound], 0, xs)
    y_lbound, y_upbound = np.clip([y_lbound, y_upbound], 0, ys)

    for i in range(x_lbound, x_upbound):
        for j in range(y_lbound, y_upbound):
            input_map[j, i] = -1
    return input_map


def resize(scale, old_mats):
    new_mats = []
    for mat in old_mats:
        new_mats.append(zoom(mat, scale, order=0))
    return np.array(new_mats)


def simple_soccer_map(xs=6, ys=9):
    assert xs % 2 == 0, "xs must be even"
    smap = np.zeros((xs, ys), dtype=np.int32)
    smap[0:xs / 2 - 1, 0] = -1
    smap[xs / 2 + 1:xs, 0] = -1
    smap[0:xs / 2 - 1, ys - 1] = -1
    smap[xs / 2 + 1:xs, ys - 1] = -1
    return smap


def cross_map(xs, ys):
    pass
