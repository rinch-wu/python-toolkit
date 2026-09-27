import cv2
import numpy as np


class JpgReader:
    file_path = "resource_/example.img"

    @classmethod
    def get(cls):
        image = cv2.imread(cls.file_path)
        vals = len(np.unique(image))
        vals = 2 ** np.ceil(np.log2(vals))
        # 给图片添加泊松噪声
        noisy_img = np.random.poisson(image * vals) / float(vals)
        return noisy_img
