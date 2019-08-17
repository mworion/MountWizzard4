# if first image, we just store the data as reference frame
if self.imageStack is None:
    CD11 = header.get('CD1_1', 0)
    CD12 = header.get('CD1_2', 0)
    self.imageStack = imageData
    self.raStack = header.get('RA', 0)
    self.decStack = header.get('DEC', 0)
    self.angleStack = angle = np.arctan2(CD12, CD11)
    self.scaleStack = CD11 / np.cos(angle)
    self.numberStack = 1
    return imageData

# now we are going to stack the results
self.numberStack += 1

if 'CTYPE1' in header:
    CD11 = header.get('CD1_1', 0)
    CD12 = header.get('CD1_2', 0)
    ra = header.get('RA', 0)
    dec = header.get('DEC', 0)
    angle = np.arctan2(CD12, CD11)
    scale = CD11 / np.cos(angle)

    # setting up the parameters for
    dx = ra - self.raStack
    dy = dec - self.decStack
    dScale = scale / self.scaleStack
    dAngle = angle - self.angleStack
    params = [dx, dy, dScale, dAngle]

    imageData = Transformation('similarity', params).fwd(np.float32(imageData))

    """
    tform = SimilarityTransform(scale=dScale,
                                    rotation=dAngle,
                                    translation=(dx, dy))
    print(dx, dy, transform.params)
    imageData = warp(np.float32(imageData),
                     inverse_map=tform.inverse(),
                     output_shape=self.imageStack.shape,
                     order=1,
                     mode='constant',
                     cval=np.median(imageData),
                     clip=False,
                     preserve_range=True)
    """