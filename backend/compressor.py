import numpy as np
from sklearn.cluster import MiniBatchKMeans

def compress_image(img_array, k):
    """
    Compress image using K-means clustering on RGB color space
    
    Args:
        img_array: Image as numpy array (H x W x 3)
        k: Number of color clusters
    
    Returns:
        Compressed image as uint8 numpy array
    """
    
    original_shape = img_array.shape

    pixels = img_array.reshape(-1, 3)

    kmeans = MiniBatchKMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    kmeans.fit(pixels)

    compressed_pixels = kmeans.cluster_centers_[
        kmeans.labels_
    ]

    compressed_pixels = np.clip(
        compressed_pixels,
        0,
        255
    )

    compressed_img = compressed_pixels.reshape(
        original_shape
    )

    return compressed_img.astype(np.uint8)