from nibabel import Nifti1Image
from nilearn.image import load_img, resample_to_img
import numpy
from scipy import stats
from nilearn import plotting


class ImgSimpleMerger:
    def __init__(self):
        self.slots = []

    def add(self, img_data):
        self.slots.append(img_data)

    def merge(self):
        merged = numpy.zeros(dtype=numpy.float, shape=self.slots[0].get_active().shape)
        for slot in self.slots:
            merged += slot.get_active()
        return merged
