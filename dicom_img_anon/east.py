from typing import Final, Tuple

import cv2
import numpy as np
from numpy import ndarray

Box = Tuple[int, int, int, int]


CHECKPOINT_PATH = "dicom_img_anon/checkpoints/east_text_detection.pb"


class EAST:
    SCORES_LAYER_NAME: Final[str] = "feature_fusion/Conv_7/Sigmoid"
    GEOMETRY_LAYER_NAME: Final[str] = "feature_fusion/concat_3"
    FEATURE_MAP_DECIMATION: Final[float] = 4.0

    def __init__(self, checkpoint: str, width: int = 1024, height: int = 1024, confidence: float = 0.2) -> None:
        self.net = cv2.dnn.readNet(checkpoint)
        self.confidence = confidence
        self.w = width
        self.h = height

    def __call__(self, image: ndarray):
        image = image.copy()
        (w_original, h_original) = image.shape[:2]
        w_scale = w_original / self.w
        h_scale = h_original / self.h
        self.net.setInput(self.convert_to_blob(cv2.resize(image, (self.w, self.h))))
        scores, geos = self.net.forward([EAST.SCORES_LAYER_NAME, EAST.GEOMETRY_LAYER_NAME])
        boxes = list(self.get_boxes(scores, geos, self.confidence))
        return [self.scale_box(box, w_scale, h_scale) for box in boxes]

    def convert_to_blob(self, image: ndarray, scale: float = 1.0, rgb_means=(123.68, 116.78, 103.94)) -> ndarray:
        return cv2.dnn.blobFromImage(image, scale, (self.w, self.h), rgb_means, swapRB=False, crop=False)

    @staticmethod
    def scale_box(box: Box, h_scale: float, w_scale: float) -> Box:
        return tuple(int(coord * adjustment) for coord, adjustment in zip(box, [w_scale, h_scale] * 2))

    @staticmethod
    def get_boxes(scores, geos, confidence_threshold):
        batch_size, features, rows, cols = scores.shape
        assert batch_size == 1, "This EAST wrapper was not written for batch_size > 1."

        for y in range(0, rows):
            row_scores = scores[0, 0, y]
            row_geos = geos[0, :, y].swapaxes(0, 1)  # 5xN -> Nx5

            for x, (score, (c0, c1, c2, c3, angle)) in enumerate(zip(row_scores, row_geos)):
                if score > confidence_threshold:
                    offset_x, offset_y = (x * EAST.FEATURE_MAP_DECIMATION, y * EAST.FEATURE_MAP_DECIMATION)
                    cos, sin = np.cos(angle), np.sin(angle)

                    h = c0 + c2
                    w = c1 + c3

                    x1 = int(offset_x + (cos * c1) + (sin * c2))
                    y1 = int(offset_y - (sin * c1) + (cos * c2))
                    x0 = int(x1 - w)
                    y0 = int(y1 - h)

                    yield x0, y0, x1, y1


def blackout_pixels(image: ndarray, box: Box) -> ndarray:
    x0, y0, x1, y1 = box
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            image[y, x] *= 0
    return image
