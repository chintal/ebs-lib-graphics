

import os
import argparse
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
    _length_pointer = 2
    _length_size = 2
    _length_palette_marker = _length_pointer
    _length_image_format = 1
    _length_header = (2 * _length_size +
                      _length_palette_marker +
                      _length_image_format)

    _supported_encodings = [None]

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
        if self._indexed is False and self._encoding is not None:
            return self.encoded_bpp
        raise NotImplementedError

    @property
    def encoded_bpp(self):
        return self._encoded_bpp()

    def _encoded_bpp(self):
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
        if self._encoding == 'RLC':
            return 'IMAGE_ENCODING_RLC'
        raise NotImplementedError

    def _get_smallest_encoding(self):
        smenc = None
        minsize = None
        for enc in self._supported_encodings:
            self._encoding = enc
            if minsize is None:
                smenc = enc
                minsize = self.packed_size
            else:
                if self.packed_size < minsize:
                    minsize = self.packed_size
                    smenc = enc
        self._encoding = smenc

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

    @property
    def packed_size(self):
        return self._packed_size()

    def _packed_size(self):
        size = sum(sum(1 for _ in l) for l in self.lines)
        return self._length_header + size

    def generate(self, outpath, incdir=None):
        stage = {
            'image': self,
            'libversion': __version__,
            'classname': self.__class__.__name__,
        }
        with open(os.path.join(outpath, self.name + '.c'), 'w') as f:
            f.write(jinja2_env.get_template('image.c').render(**stage))
        with open(os.path.join(outpath, self.name + '.h'), 'w') as f:
            f.write(jinja2_env.get_template('image.h').render(**stage))
        if incdir:
            outpath = incdir
            if not os.path.exists(incdir):
                os.makedirs(incdir)
        with open(os.path.join(outpath, self.name + '.h'), 'w') as f:
            f.write(jinja2_env.get_template('image.h').render(**stage))


class FormatMonochrome(GraphicsImageFormatBase):
    _supported_encodings = [None, 'RLC']

    def __init__(self, source, encoding=None):
        super(FormatMonochrome, self).__init__(source, 1, False, encoding)
        self._img = self._img.convert('1')
        if self._encoding == 'AUTO':
            self._get_smallest_encoding()

    def _line_generator(self):
        for line in self.source_lines:
            yield self._byte_generator(line)

    def _byte_generator(self, line):
        if self.encoding == 'IMAGE_ENCODING_RAW':
            return self._byte_generator_raw(line)
        if self.encoding == 'IMAGE_ENCODING_RLC':
            return self._byte_generator_rlc(line)

    def _byte_generator_raw(self, line):
        if self._state.get('lend', 0):
            acc = self._state['lacc']
            for bit in range(self._state['lend'], 8):
                acc = acc << 1 | next(line)
            yield acc
        while True:
            acc = 0
            for bit in range(8):
                try:
                    acc = acc << 1 | (1 if next(line) else 0)
                except StopIteration:
                    self._state['lend'] = bit
                    self._state['lacc'] = acc
                    return
            yield acc

    def _encoded_bpp(self):
        if self._encoding == 'RLC':
            return self._rlc_encoded_bpp()
        raise NotImplementedError

    def _rlc_encoded_bpp(self):
        return 8

    def _rlc_byte(self, bit, runlength):
        # Bit goes in LSB. We're going to expect to rely on RLC if speed
        # becomes an issue. This should be revisited at some point.
        return runlength * 2 + bit

    def _byte_generator_rlc(self, line):
        lastrun = self._state.get('lastrun', 0)
        lastbit = self._state.get('lastbit', None)
        while True:
            try:
                nextbit = (1 if next(line) else 0)
                if lastbit is None:
                    lastbit = nextbit
                    lastrun = 1
                if nextbit == lastbit:
                    lastrun += 1
                    if lastrun == 0x7f:
                        yield self._rlc_byte(lastbit, lastrun)
                        lastrun = 0
                else:
                    yield self._rlc_byte(lastbit, lastrun)
                    lastbit = nextbit
                    lastrun = 1
            except StopIteration:
                self._state['lastrun'] = lastrun
                self._state['lastbit'] = lastbit
                return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input image file to convert")
    parser.add_argument('-o', '--output', help="Path to the desired output folder")
    parser.add_argument('--incdir', help="Path to additionally copy the generated "
                                         "headers to, if different from -o")
    parser.add_argument('-f', '--format', help="Format of the generated image")
    parser.add_argument('-e', '--encoding', help="Encoding / compression to use")
    args = parser.parse_args()

    if args.encoding == 'NONE':
        args.encoding = None
    converter = globals()['Format{0}'.format(args.format)](args.input, encoding=args.encoding)
    converter.generate(args.output, incdir=args.incdir)
    print("Generated C encoded image using {0} with {1}."
          "".format(converter.__class__.__name__, converter.encoding))
    print("Estimated output size : {0} bytes".format(converter.packed_size))


if __name__ == '__main__':
    main()
