import matplotlib.pyplot as plt
import numpy as np
import cv2


def segmentation_split(img, min_std=0.05, min_size=2):
    seg_res = np.zeros(img.shape, dtype='int16')
    index = 1
    m_res = np.zeros(img.shape)

    def split(img, from_x, to_x, from_y, to_y):
        nonlocal index

        segment = img[from_x: to_x+1, from_y: to_y+1]
        mean = np.mean(segment)
        std = np.std(segment)

        if std > min_std and to_x - from_x + 1 >= min_size and to_y - from_y > min_size:
            split_x = (from_x + to_x)//2
            split_y = (from_y + to_y)//2

            split(img, from_x, split_x, from_y, split_y)
            split(img, split_x+1, to_x, from_y, split_y)
            split(img, from_x, split_x, split_y+1, to_y)
            split(img, split_x+1, to_x, split_y+1, to_y)
        else:
            seg_res[from_x: to_x+1, from_y:to_y+1] = index
            index += 1
            m_res[from_x: to_x+1, from_y:to_y+1] = mean

    split(img, 0, img.shape[0]-1, 0, img.shape[1]-1)

    return seg_res, m_res


def segmentation_merge(seg_res, m_res):
    seg_res = seg_res.copy()
    m_res = m_res.copy()
    max_index = np.max(seg_res)

    i = 1
    while i <= max_index:
        segment = (seg_res == i).astype('uint8')

        if not np.any(segment):
            i += 1
            continue

        x, y = np.nonzero(segment)
        first = x[0], y[0]

        dilated = cv2.dilate(
            segment, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        frame = dilated - segment

        non_zero_seg = seg_res[np.nonzero(frame.astype('bool'))]
        neigh_segments = np.unique(non_zero_seg)

        merged = False

        for neigh_idx in neigh_segments:

            neigh_segment = (seg_res == neigh_idx)
            if not np.any(seg_res[neigh_segment]):
                continue

            x_neigh, y_neigh = np.nonzero(neigh_segment)
            first_neigh = x_neigh[0], y_neigh[0]

            if np.abs(m_res[first_neigh[0], first_neigh[1]] - m_res[first[0], first[1]]) < 5:
                seg_res[neigh_segment] = i
                merged = True

        if not merged:
            i += 1

    return seg_res


def segmentation(image, min_std=0.05, min_split_size=8, min_area=100):
    seg_res, m_res = segmentation_split(image, min_std, min_split_size)
    print('split')
    seg_res = segmentation_merge(seg_res, m_res)
    print('merged')

    unique = np.unique(seg_res)
    for idx in unique:
        mask = seg_res == idx
        area = np.sum(mask)
        if area < min_area:
            seg_res[mask] = 0

    unique = np.unique(seg_res)
    for i, idx in enumerate(unique):
        mask = seg_res == idx
        seg_res[mask] = i

    segments = []
    for idx in unique:
        mask = seg_res == idx
        segment = np.zeros(image.shape, dtype='uint8')
        segment[mask] = image[mask]
        segments.append(segment)

    return segments

image = cv2.cvtColor(cv2.imread('license_plates/plate_2.jpg', cv2.CV_32F), cv2.COLOR_BGR2GRAY)
segments = segmentation(image)
print(segments)
for segment in segments:
    plt.imshow(segment)
    plt.show()