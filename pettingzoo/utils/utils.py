def save_image_observation(observation, frame_stacking=1, pre_fs_ndim=None, reverse_colors=False):
    '''
    saves observations that are images

    Parameters
    ----------
    observation : numpy array or dict of numpy arrays
        Input observation(s).
    frame_stacking : int, optional
        Number of stacked image frames. The default is 1.
    pre_fs_ndim : numpy shape (tuple), optional
        Shape of the observation pre-frame_stacking. The default is None.
    reverse_colors : Boolean, optional
        Input True if you want better contrast. The default is False.

    Raises
    ------
    ValueError
        Raises exception when input is not an image.

    Returns
    -------
    None.

    '''
    from os.path import isfile
    import matplotlib.pyplot as plt
    import numpy as np
    i = 0
    observation_dict = observation
    if not isinstance(observation, dict):
        observation_dict = {0: observation}

    for key in observation_dict.keys():
        # check if file already exists
        while isfile("obs_{}_{}.png".format(i, key)):
            i += 1
        # remove the extra dimension, if present
        image = np.squeeze(observation_dict[key])
        if image.ndim < 2:
            raise ValueError("Image should be at least 2-dimensional. It is {}".format(image.ndim))
        # image is range [0, 1] - float32. Else, use np.divide

        if frame_stacking > 1:
            # pick the last frame (most recent)
            if pre_fs_ndim == 2:
                image = image[-1]
            elif pre_fs_ndim == 3:
                third_dim = int(image.shape[-1] / frame_stacking)
                image = image[:, :, -third_dim:]
        if reverse_colors:
            image = np.array([[1 - col for col in row] for row in image], dtype=np.float32)
        plt.imsave("obs_{}_{}.png".format(i, key), image, cmap=plt.cm.gray)
