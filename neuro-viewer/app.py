import sys

import warnings
warnings.filterwarnings('ignore', message='invalid value encountered in less')
warnings.filterwarnings('ignore', message='invalid value encountered in greater')
warnings.filterwarnings('ignore', message='invalid value encountered in true_divide')
warnings.filterwarnings('ignore', message='Fetchers from the nilearn.datasets module will be updated')

from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow
from threading import Thread

import os
import nibabel
import numpy
import time

from math import fabs, floor, isnan

from DataLoader import *
from ImgMerger import ImgSimpleMerger
from ImgFormatter import ImgFormatter, resample, create_reg_template


def ti():
    return time.time()


def tp(start_time, name=''):
    pass
    # print('{} elapsed in {} s'.format(name, ti() - start_time))


class Workspace:
    def __init__(self, crop_size):
        self.slots = []
        self.current_slide = 0
        self.slider_size = crop_size
        self.mode = 's:z'
        self.show_colorbar = False
        self.merger = ImgSimpleMerger()
        self.buffer = False
        self.running = False

    def redraw(self):
        for slot in self.slots:
            slot.redraw()

    def process_merge(self):
        self.slots[-1].img.reset_img(self.merger.merge())
        self.slots[-1].redraw()
        self.finished()

    def start(self):
        self.running = True
        p = Thread(target=self.process_merge, args=())
        p.start()

    def finished(self):
        self.running = False
        self.run()

    def run(self):
        if not self.running and self.buffer:
            self.buffer = False
            self.start()

    def update_merge(self):
        if self.slots and self.slots[-1].name == 'Merge':
            self.buffer = True
            self.run()


class Slot:
    def __init__(self, workspace, name, pos, img, rgb_template):
        self.workspace = workspace
        self.name = name
        self.pos = pos
        self.img = ImgFormatter(img, self.name, rgb_template)
        self.max = max(numpy.nanmax(img), numpy.abs(numpy.nanmin(img)))

        self.running = False
        self.buffer = []

        self.ax = None
        self.scale(0.5 * self.max, True, True)
        self.gui = {}

    def scale(self, thres, show_plus, show_minus):
        self.thres = thres
        neg_thres = -thres if show_minus else -self.max
        pos_thres = thres if show_plus else self.max
        self.buffer = [(neg_thres, pos_thres)]
        self.run()

    def process_scale(self, k):
        self.img.scale2(k[0], k[1])
        self.finished()

    def start(self, k):
        self.running = True
        p = Thread(target=self.process_scale, args=(k,))
        p.start()

    def finished(self):
        if self.ax:
            self.redraw()
        self.running = False
        self.run()

    def run(self):
        if not self.running and self.buffer:
            self.start(self.buffer.pop())
        # self.workspace.update_merge()

    def get_active(self):
        return self.img.get_active()

    def redraw(self):
        ax = self.ax
        modes_parts = workspace.mode.split(':')
        should_redraw = None
        if modes_parts[0] == 's':
            should_redraw = self.img.plot_slice(ax, modes_parts[1], workspace.current_slide)
        elif modes_parts[0] == 'g':
            should_redraw = self.img.plot_glass(ax, modes_parts[1])
        else:
            raise ValueError('Invalid mode')
        if should_redraw:
            self.gui['canvas'].draw()
        else:
            self.gui['canvas'].draw_idle()

    def mouse_move(self, event):
        return None
        if event.xdata is not None:
            iX, iY = floor(event.xdata), floor(event.ydata)
            # print(self.img.get_val(iX, iY))
            val = self.img.get_val(iY, iX)
            if not isnan(val):
                txt = '{0:.5f}'.format(val)
            else:
                txt = '-'
            self.workspace.val_label.setText(txt)
        else:
            self.workspace.val_label.setText('Value')

    def set_gui(self, figure, canvas):
        self.gui['figure'] = figure
        self.gui['canvas'] = canvas
        self.ax = self.gui['figure'].add_subplot(111)  # position=[0., 0., 1., 1.]
        self.gui['figure'].subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        self.ax.axis('off')


if __name__ == '__main__':

    if len(sys.argv) > 1:
        config_filename = sys.argv[1]
        if not os.path.isfile(config_filename):
            raise ValueError('Configuration file {} was not found.'.format(config_filename))
    else:
        raise ValueError('Provide configuration file in first cmd parameter please.')

    loader = DataLoader(config_filename)
    mod_template_filename, crop_size, shift_xyz = loader.get_background()
    rgb_template = create_reg_template(mod_template_filename, crop_size, shift_xyz)
    src_img = nibabel.load(mod_template_filename)

    workspace = Workspace(crop_size)
    for slot_loader in loader.get_slots():
        src_img = nibabel.load(slot_loader.source)
        src = resample(src_img, mod_template_filename, crop_size, shift_xyz)
        slot = Slot(workspace, slot_loader.title, slot_loader.grid_pos, src, rgb_template)
        workspace.slots.append(slot)
        workspace.merger.add(slot)
        print('Loaded {}'.format(slot_loader.title))

    workspace.slots.append(Slot(workspace, 'Merge', (3, 2), workspace.merger.merge(), rgb_template))
    workspace.slots[-1].max = len(workspace.slots) - 1

    def run():
        app = QApplication(sys.argv)
        Gui = MainWindow(workspace)
        sys.exit(app.exec_())

    run()
