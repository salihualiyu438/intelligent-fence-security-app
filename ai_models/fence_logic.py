def is_near_fence(bbox, fence_y=350):
    x1, y1, x2, y2 = bbox
    center_y = (y1 + y2) // 2
    return center_y > fence_y
