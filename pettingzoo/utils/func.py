def save_observation(observation_dict, frame_stacking=1, reverse_colors=False):
    from os.path import isfile
    import matplotlib.pyplot as plt
    import numpy as np
    i = 0
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
            image = image[-1]

        if reverse_colors:
            image = np.array([[1-col for col in row] for row in image], dtype=np.float32)
        plt.imsave("obs_{}_{}.png".format(i, key), image, cmap=plt.cm.gray)
