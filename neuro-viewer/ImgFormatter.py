from nibabel import Nifti1Image
from nilearn.image import load_img, resample_to_img
import numpy
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
from math import fabs, isnan, ceil, floor


def reorient(img):
    img = numpy.rot90(img, 1, (1, 2))
    img = numpy.rot90(img, 3)
    img = numpy.rot90(img, 3, (1, 2))
    return img

def fov(shape, size, shift_xyz):
    def calc(dk, sk):
        assert(size <= dk)
        k1, k2 = floor((dk - size) / 2) + sk, dk - ceil((dk - size) / 2) + sk
        assert(k1 >= 0)
        assert(k2 < dk)
        return k1, k2

    x1, x2 = calc(shape[0], shift_xyz[0])
    y1, y2 = calc(shape[1], shift_xyz[1])
    z1, z2 = calc(shape[2], shift_xyz[2])

    return x1, x2, y1, y2, z1, z2


def create_reg_template(mod_template_filename, crop_size, shift_xyz):
    mod_template = load_img(mod_template_filename)
    x1, x2, y1, y2, z1, z2 = fov(mod_template.get_data().shape, crop_size, shift_xyz)
    final_template = reorient(mod_template.get_data()[x1:x2, y1:y2, z1:z2])
    final_template[final_template == 0] = numpy.max(final_template)
    norm_template = matplotlib.colors.Normalize(vmin=0, vmax=numpy.nanmax(final_template), clip=True)
    return cm.gray(norm_template(final_template))


def get_glass_template(mode):
    if mode == 'z':
        view = rgb_template[37, ::-1, ::-1, :]
    elif mode == 'y':
        view = rgb_template[:, 55, ::-1, :]
    elif mode == 'x':
        view = rgb_template[:, :, 50, :]
    return view


def resample(nifti_image, mod_template_filename, crop_size, shift_xyz):
    img_temp = resample_to_img(nifti_image, load_img(mod_template_filename))
    x1, x2, y1, y2, z1, z2 = fov(img_temp.get_data().shape, crop_size, shift_xyz)
    return reorient(img_temp.get_data()[x1:x2, y1:y2, z1:z2])


class ImgFormatter:
    def __init__(self, img, title, tiv, rgb_template):
        self.img = img
        self.title = title
        self.tiv = tiv
        self.rgb_template = rgb_template
        self.scaled = None
        self.colored = None
        self.im = None
        self.tmin = None
        self.tmax = None
        self.last_view = None
        self.coverage = -1

    def reset_img(self, img):
        self.img = img
        self.scale2(self.tmin, self.tmax)

    def get_val(self, x, y):
        return self.last_view[x, y]

    def get_raw_data(self):
        return numpy.copy(self.img)

    def get_active(self):
        return (~numpy.isnan(self.scaled)).astype(numpy.float64)

    @staticmethod
    def scale(img, tmin, tmax):
        vmin = numpy.nanmin(img)
        vmax = numpy.nanmax(img)

        img[numpy.logical_and(img > tmin, img < tmax)] = numpy.nan
        img[img < 0] -= tmin
        img[img > 0] -= tmax
        img[img < 0] = img[img < 0] / (fabs(vmin) + tmin)
        img[img > 0] = img[img > 0] / (vmax - tmax)
        return img

    @staticmethod
    def color(img, template, schema):
        assert img.shape == template.shape[0:-1]
        norm_tmap = matplotlib.colors.Normalize(vmin=-1, vmax=1, clip=True)
        rgb_tmap = schema(norm_tmap(img))  # 0.12, nejdrazsi funkce zrejme
        # rgb_tmap[...,3] = 0.3
        use_tmap_ind = numpy.logical_not(numpy.logical_or(numpy.isnan(img), img == 0))

        colored = numpy.copy(template)  # 0.04
        colored[use_tmap_ind, :] = rgb_tmap[use_tmap_ind, :]  # 0.07
        return colored

    def scale2(self, tmin, tmax):
        self.tmin = tmin
        self.tmax = tmax

        self.scaled = self.scale(self.get_raw_data(), tmin, tmax)  # zobrazuje se v glass view a pro merger
        self.colored = self.color(self.scaled, self.rgb_template, cm.seismic)  # zobrazuje se ve slice view
        self.coverage = numpy.count_nonzero(~numpy.isnan(self.scaled)) / self.tiv

    @staticmethod
    def reorient(img):
        return reorient(img)

    def get_view_slice(self, img, mode, slice):
        if mode == 'z':
            view = img[slice, ::-1, ::-1, :]
        elif mode == 'y':
            view = img[:, slice, ::-1, :]
        elif mode == 'x':
            view = img[:, :, slice, :]
        return view

    def get_view_sum(self, img, mode):
        if mode == 'z':
            view = img[:, ::-1, ::-1]
        elif mode == 'y':
            view = img[:, :, ::-1]
        elif mode == 'x':
            view = img[:, :, :]
        modes = {'z': 0, 'y': 1, 'x': 2}
        self.last_view = numpy.nanmax(numpy.abs(view), modes[mode])
        return self.color(self.last_view, get_glass_template(mode), cm.autumn)

    def plot_slice(self, ax, mode, slice):
        view = self.get_view_slice(self.colored, mode, slice)

        if not self.im:
            self.im = ax.imshow(view, animated=True)
            return True
        else:
            self.im.set_array(view)
            return False

    def plot_glass(self, ax, mode):
        view = self.get_view_sum(self.scaled, mode)

        if not self.im:
            self.im = ax.imshow(view, animated=True, interpolation='bilinear')
            ax.text(0, 5, self.title, fontsize=10)
            return True
        else:
            self.im.set_array(view)
            return False
