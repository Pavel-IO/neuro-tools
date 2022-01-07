import sys
import os.path as path
import xml.etree.ElementTree as ET

class SlotSettings:
    def __init__(self, title, source, pos):
        self.title = title
        self.source = source.replace('\\', '/')
        self.grid_pos = pos
        if not path.isfile(self.source):
            raise ValueError('File "{}" was not found.'.format(self.source))

    def __repr__(self):
        return str((self.title, self.source, self.grid_pos))


class DataLoader:
    def __init__(self, source):
        self.source_dir = path.dirname(source)
        tree = ET.parse(source)
        self.root = tree.getroot()

    def get_grid_size(self):
        return int(self.root.attrib.get('rows', 2)), int(self.root.attrib.get('cols', 3))

    def get_background(self):
        attrs = self.root.find('background').attrib
        background_path = attrs['file'] if path.isabs(attrs['file']) else path.join(self.source_dir, attrs['file'])
        if not path.isfile(background_path):
            raise ValueError('Background file "{}" was not found.'.format(attrs['file']))

        x = int(attrs.get('shift_x', 0))
        y = int(attrs.get('shift_y', 0))
        z = int(attrs.get('shift_z', 0))
        return background_path, int(attrs['crop']), (x, y, z)

    def get_slots(self):
        for slot_tag in self.root.find('slots').findall('slot'):
            attrs = slot_tag.attrib
            pos_str = attrs['pos'].split(',')
            slot_path = attrs['source'] if path.isabs(attrs['source']) else path.join(self.source_dir, attrs['source'])
            yield SlotSettings(attrs['name'], slot_path.replace('\\', '/'), (int(pos_str[0]), int(pos_str[1])))

    def get_tiv(self):
        return int(self.root.find('background').attrib['tiv'])
