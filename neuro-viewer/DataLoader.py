import sys
import os.path
import xml.etree.ElementTree as ET

class SlotSettings:
    def __init__(self, title, source, pos):
        self.title = title
        self.source = source.replace('\\', '/')
        self.grid_pos = pos
        if not os.path.isfile(self.source):
            raise ValueError('File "{}" was not found.'.format(self.source))

    def __repr__(self):
        return str((self.title, self.source, self.grid_pos))


class DataLoader:
    def __init__(self, source):
        tree = ET.parse(source)
        self.root = tree.getroot()

    def get_background(self):
        attrs = self.root.find('background').attrib
        if not os.path.isfile(attrs['file']):
            raise ValueError('Background file "{}" was not found.'.format(attrs['file']))

        x = int(attrs.get('shift_x', 0))
        y = int(attrs.get('shift_y', 0))
        z = int(attrs.get('shift_z', 0))
        return attrs['file'], int(attrs['crop']), (x, y, z)

    def get_slots(self):
        for slot_tag in self.root.find('slots').findall('slot'):
            attrs = slot_tag.attrib
            pos_str = attrs['pos'].split(',')
            yield SlotSettings(attrs['name'], attrs['source'], (int(pos_str[0]), int(pos_str[1])))
