from PIL import Image
import numpy as np
import glob

for im_path in glob.glob('vk*.png'):
    # Load image and ensure it is 3-channel RGB...
    # ... not 1-channel greyscale, not 4-channel RGBA, not 1-channel palette
    im = Image.open(im_path).convert('RGB')

    # Make into Numpy array of RGB and get dimensions
    RGB = np.array(im)
    h, w = RGB.shape[:2]

    # Add an alpha channel, fully opaque (255)
    RGBA = np.dstack((RGB, np.zeros((h, w), dtype=np.uint8) + 255))

    # Make mask of black pixels - mask is True where image is black
    mask1 = (RGBA[:, :, 0:3] == [0, 0, 0]).all(2)
    mask2 = (RGBA[:, :, 0:3] == [255, 0, 0]).all(2)
    RGBA[mask1] = (32, 32, 32, 255)
    RGBA[mask2] = (32, 144, 192, 255)

    # Convert Numnpy array back to PIL Image and save
    Image.fromarray(RGBA).save(im_path)
    print(im_path)

for im_path in glob.glob('key_*.png'):
    # Load image and ensure it is 3-channel RGB...
    # ... not 1-channel greyscale, not 4-channel RGBA, not 1-channel palette
    im = Image.open(im_path).convert('RGB')

    # Make into Numpy array of RGB and get dimensions
    RGB = np.array(im)
    h, w = RGB.shape[:2]

    # Add an alpha channel, fully opaque (255)
    RGBA = np.dstack((RGB, np.zeros((h, w), dtype=np.uint8) + 255))

    # Make mask of black pixels - mask is True where image is black
    mask1 = (RGBA[:, :, 0:3] == [66, 67, 70]).all(2)
    mask2 = (RGBA[:, :, 0:3] == [255, 0, 0]).all(2)

    RGBA[mask1] = (32, 32, 32, 0)
    RGBA[mask2] = (32, 144, 192, 255)

    # Convert Numnpy array back to PIL Image and save
    Image.fromarray(RGBA).save(im_path)
    print(im_path)
