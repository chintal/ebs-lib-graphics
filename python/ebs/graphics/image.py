

import os
from PIL import Image
from jinja2 import Environment, FileSystemLoader
from . import __version__

jinja2_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates/')),
    trim_blocks=True,
    keep_trailing_newline=True,
    lstrip_blocks=False,
)


class GraphicsImageFormatBase(object):
    def __init__(self, source, bpp, indexed=False, encoding=None):
        self._img = Image.open(source)
        self._source = source
        self._bpp = bpp
        self._indexed = indexed
        self._encoding = encoding
        self._state = {}

    @property
    def source(self):
        return os.path.basename(self._source)

    @property
    def name(self):
        return os.path.splitext(self.source)[0]

    @property
    def bpp(self):
        if self._indexed is False and self._encoding is None:
            return self._bpp
        raise NotImplementedError

    @property
    def palette(self):
        if self._indexed is False:
            return 'NULL'
        raise NotImplementedError

    @property
    def encoding(self):
        if self._encoding is None:
            return 'IMAGE_ENCODING_RAW'
        raise NotImplementedError

    @property
    def pixeltype(self):
        if self._indexed is False:
            return 'IMAGE_PIXELTYPE_RAW'
        raise NotImplementedError

    @property
    def size_x(self):
        return self._img.size[0]

    @property
    def size_y(self):
        return self._img.size[1]
    
    @property
    def source_lines(self):
        return self._source_line_generator()

    def _source_line_generator(self):
        for lineno in range(self.size_y):
            yield self._source_byte_generator(lineno)

    def _source_byte_generator(self, lineno):
        for bno in range(self.size_x):
            yield self._img.getpixel((bno, lineno))

    @property
    def lines(self):
        return self._line_generator()

    def _line_generator(self):
        raise NotImplementedError

    def generate(self, outpath):
        stage = {
            'image': self,
            'libversion': __version__,
            'classname': self.__class__.__name__,
        }
        with open(os.path.join(outpath, self.name + '.c'), 'w') as f:
            f.write(jinja2_env.get_template('image.c').render(**stage))
        with open(os.path.join(outpath, self.name + '.h'), 'w') as f:
            f.write(jinja2_env.get_template('image.h').render(**stage))


class FormatMonochrome(GraphicsImageFormatBase):
    def __init__(self, source, encoding=None):
        super(FormatMonochrome, self).__init__(source, 1, False, encoding)

    def _line_generator(self):
        for line in self.source_lines:
            yield self._byte_generator(line)

    def _byte_generator(self, line):
        if self._state.get('lend', 0):
            acc = self._state['lacc']
            for bit in range(self._state['lend'], 8):
                acc = acc << 1 | next(line)
            yield acc
        while True:
            acc = 0
            for bit in range(8):
                try:
                    acc = acc << 1 | next(line)
                except StopIteration:
                    self._state['lend'] = bit
                    self._state['lacc'] = acc
                    return
            yield acc


if __name__ == '__main__':
    fm = FormatMonochrome('python/example/lena_96px_1bpp_c.bmp')
    fm.generate('python/example')
