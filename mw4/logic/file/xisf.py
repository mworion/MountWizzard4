# coding: utf-8

"""
(Incomplete) XISF Encoder/Decoder (see https://pixinsight.com/xisf/).
This implementation is not endorsed nor related with PixInsight development team.
Copyright (C) 2021-2022 Sergio Díaz, sergiodiaz.eu
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, version 3 of the License.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.
You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = 0.9  # see also setup.cfg in https://packaging.python.org/en/latest/guides/single-sourcing-package-version/

import platform
import xml.etree.ElementTree as ET
import numpy as np
import lz4.block  # https://python-lz4.readthedocs.io/en/stable/lz4.block.html
import zlib  # https://docs.python.org/3/library/zlib.html
import sys
from datetime import datetime


class XISF:
    """Implements an *incomplete* (attached images only) baseline XISF Decoder and a simple baseline Encoder.
    It parses metadata from Image and Metadata XISF core elements. Image data is returned as a numpy ndarray
    (using the "channels-last" convention by default).
    What's supported:
    - Monolithic XISF files only
        - XISF blocks with attachment block locations (neither inline nor embedded block locations as required
          for a complete baseline decoder)
        - Planar pixel storage models, *however it assumes 2D images only* (with multiple channels)
        - UInt8/16/32 and Float32/64 pixel sample formats
        - Grayscale and RGB color spaces
    - Decoding:
        - multiple Image core elements from a monolithic XISF file
        - Support all standard compression codecs defined in this specification for decompression (zlib/lz4[hc]+
          byte shuffling)
    - Encoding:
        - Single image core element
        - Uncompressed data blocks only
    - "Atomic" properties only (Scalar, Strings, TimePoint)
    - Metadata and FITSKeyword core elements
    What's not supported (at least by now):
    - Read pixel data from XISF blocks with inline or embedded block locations
    - Read pixel data in the normal pixel storage models
    - Read pixel data in the planar pixel storage models other than 2D images
    - Complex, Vector, Matrix and Table properties
    - Any other not explicitly supported core elements (Resolution, Thumbnail, ICCProfile, etc.)
    Usage example:
    ```
    from xisf import XISF
    import matplotlib.pyplot as plt
    xisf = XISF("file.xisf")
    file_meta = xisf.get_file_metadata()
    file_meta
    ims_meta = xisf.get_images_metadata()
    ims_meta
    im_data = xisf.read_image(0)
    plt.imshow(im_data)
    plt.show()
    XISF.write(
        "output.xisf", im_data,
        creator_app="My script v1.0", image_metadata=ims_meta[0], xisf_metadata=file_meta,
        codec='lz4hc', shuffle=True
    )
    ```
    If the file is not huge and it contains only an image (or you're interested just in one of the
    images inside the file), there is a convenience method for reading the data and the metadata:
    ```
    from xisf import XISF
    import matplotlib.pyplot as plt
    im_data = XISF.read("file.xisf")
    plt.imshow(im_data)
    plt.show()
    ```
    The XISF format specification is available at https://pixinsight.com/doc/docs/XISF-1.0-spec/XISF-1.0-spec.html
    """

    # Static attributes
    _creator_app = f"Python {platform.python_version()}"
    _creator_module = f"XISF Python Module v{__version__} github.com/sergio-dr/xisf"
    _signature = b'XISF0100'  # Monolithic
    _headerlength_len = 4
    _reserved_len = 4
    _xml_ns = {'xisf': "http://www.pixinsight.com/xisf"}
    _xisf_attrs = {
        'xmlns': "http://www.pixinsight.com/xisf",
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'version': "1.0",
        'xsi:schemaLocation': "http://www.pixinsight.com/xisf http://pixinsight.com/xisf/xisf-1.0.xsd"
    }
    _compression_def_level = {
        'zlib': 6,
        # 1..9, default: 6 as indicated in https://docs.python.org/3/library/zlib.html
        'lz4': 0,
        # no other values, as indicated in https://python-lz4.readthedocs.io/en/stable/lz4.block.html
        'lz4hc': 9
        # 1..12, (4-9 recommended), default: 9 as indicated in https://python-lz4.readthedocs.io/en/stable/lz4.block.html
    }

    def __init__(self, fname):
        """Opens a XISF file and extract its metadata. To get the metadata and the images, see get_file_metadata(),
        get_images_metadata() and read_image().
        Args:
            fname: filename

        Returns:
            XISF object.
        """
        self._fname = fname
        self._headerlength = None
        self._xisf_header = None
        self._xisf_header_xml = None
        self._images_meta = None
        self._file_meta = None
        ET.register_namespace('', self._xml_ns['xisf'])

        self._read()

    def _read(self):
        with open(self._fname, "rb") as f:
            # Check XISF signature
            signature = f.read(len(self._signature))
            if signature != self._signature:
                raise ValueError("File doesn't have XISF signature")

            # Get header length
            self._headerlength = int.from_bytes(
                f.read(self._headerlength_len),
                byteorder='little'
            )
            # Equivalent:
            # self._headerlength = np.fromfile(f, dtype=np.uint32, count=1)[0]

            # Skip reserved field
            _ = f.read(self._reserved_len)

            # Get XISF (XML) Header
            self._xisf_header = f.read(self._headerlength)
            self._xisf_header_xml = ET.fromstring(self._xisf_header)
        self._analyze_header()

    def _analyze_header(self):
        # Analyze header to get Data Blocks position and length
        self._images_meta = []
        for image in self._xisf_header_xml.findall('xisf:Image', self._xml_ns):
            image_basic_meta = image.attrib

            # Parse and replace geometry and location with tuples,
            # parses and translates sampleFormat to numpy dtypes,
            # and extend with metadata from children entities (FITSKeywords, XISFProperties)

            #   The same FITS keyword can appear multiple times, so we have to
            #   prepare a dict of lists. Each element in the list is a dict
            #   that hold the value and the comment associated with the keyword.
            #   Not as clear as I would like.
            fits_keywords = {}
            for a in image.findall('xisf:FITSKeyword', self._xml_ns):
                fits_keywords.setdefault(a.attrib['name'], []).append({
                    'value': a.attrib['value'].strip("'").strip(" "),
                    'comment': a.attrib['comment'],
                })

            image_extended_meta = {
                'geometry': self._parse_geometry(image.attrib['geometry']),
                'location': self._parse_location(image.attrib['location']),
                'dtype': self._parse_sampleFormat(image.attrib['sampleFormat']),
                'FITSKeywords': fits_keywords,
                'XISFProperties': {p.attrib['id']: self._process_property(p)
                                   for p in
                                   image.findall('xisf:Property', self._xml_ns)
                                   }
            }
            # Also parses compression attribute if present, converting it to a tuple
            if 'compression' in image.attrib:
                image_extended_meta['compression'] = self._parse_compression(
                    image.attrib['compression'])

            # Merge basic and extended metadata in a dict
            image_meta = {**image_basic_meta, **image_extended_meta}

            # Append the image metadata to the list
            self._images_meta.append(image_meta)

        # Analyze header for file metadata
        self._file_meta = {}
        for p in self._xisf_header_xml.find('xisf:Metadata', self._xml_ns):
            self._file_meta[p.attrib['id']] = self._process_property(p)

        # TODO: rest of XISF core elements: Resolution, ICCProfile, Thumbnail, ...

    @staticmethod
    def _process_property(p):
        # TODO: map XISF types to python types
        return {**p.attrib, 'value': p.text} if p.text else p.attrib

    def get_images_metadata(self):
        """Provides the metadata of all image blocks contained in the XISF File, extracted from
        the header (<Image> core elements). To get the actual image data, see read_image().
        It outputs a dictionary m_i for each image, with the following structure:
        ```
        m_i = {
            'geometry': (width, height, channels), # only 2D images (with multiple channels) are supported
            'location': (pos, size), # used internally in read_image()
            'dtype': np.dtype('...'), # derived from sampleFormat argument
            'compression': (codec, uncompressed_size, item_size), # optional
            'key': 'value', # other <Image> attributes are simply copied
            ...,
            'FITSKeywords': { <fits_keyword>: fits_keyword_values_list, ... },
            'XISFProperties': { <xisf_property_name>: property_dict, ... }
        }
        where:
        fits_keyword_values_list = [ {'value': <value>, 'comment': <comment> }, ...]
        property_dict = {'id': <xisf_property_name>, 'type': <xisf_type>, 'value': property_value, ...}
        ```
        Returns:
            list [ m_0, m_1, ..., m_{n-1} ] where m_i is a dict as described above.

        """
        return self._images_meta

    def get_file_metadata(self):
        """Provides the metadata from the header of the XISF File (<Metadata> core elements).

        Returns:
            dictionary with one entry per property: { <xisf_property_name>: property_dict, ... }
            where:
            ```
            property_dict = {'id': <xisf_property_name>, 'type': <xisf_type>, 'value': property_value, ...}
            ```
        """
        return self._file_meta

    def get_metadata_xml(self):
        """Returns the complete XML header as a xml.etree.ElementTree.Element object.
        Returns:
            xml.etree.ElementTree.Element: complete XML XISF header
        """
        return self._xisf_header_xml

    def read_image(self, n=0, data_format='channels_last'):
        """Extracts an image from a XISF object.
        Args:
            n: index of the image to extract in the list returned by get_images_metadata()
            data_format: channels axis can be 'channels_first' or 'channels_last' (as used in
            keras/tensorflow, pyplot's imshow, etc.), 0 by default.

        Returns:
            Numpy ndarray with the image data, in the requested format (channels_first or channels_last).
        """
        try:
            meta = self._images_meta[n]
        except IndexError as e:
            if self._xisf_header is None:
                raise RuntimeError("No file loaded") from e
            elif not self._images_meta:
                raise ValueError("File does not contain image data") from e
            else:
                raise ValueError("Requested image #%d, valid range is [0..%d]" % (
                n, len(self._images_meta) - 1)) from e

        pos, size = meta[
            'location']  # Position and size of the Data Block containing the image data

        try:
            w, h, chc = meta[
                'geometry']  # Assumes *two*-dimensional images (chc=channel count)
        except ValueError as e:
            raise NotImplementedError(
                "Assumed 2D channels (width, height, channels), found %s geometry" % (
                meta['geometry'],))

        with open(self._fname, "rb") as f:
            if 'compression' in meta:
                # (codec, uncompressed-size, item-size); item-size is None if not using byte shuffling
                codec, uncompressed_size, item_size = meta['compression']
                f.seek(pos)
                im_data = f.read(size)

                if codec.startswith("lz4"):
                    im_data = lz4.block.decompress(im_data,
                                                   uncompressed_size=uncompressed_size)
                elif codec.startswith("zlib"):
                    im_data = zlib.decompress(im_data)
                else:
                    raise NotImplementedError(
                        "Unimplemented compression codec %s" % (codec,))

                if item_size:  # using byte-shuffling
                    im_data = self._unshuffle(im_data, item_size)

                im_data = np.frombuffer(im_data, dtype=meta['dtype'])

            else:
                # no compression
                f.seek(0)
                im_data = np.fromfile(f, offset=pos, dtype=meta['dtype'],
                                      count=h * w * chc)

        im_data = im_data.reshape((chc, h, w))
        return np.transpose(im_data,
                            (1, 2, 0)) if data_format == 'channels_last' else im_data

    @staticmethod
    def read(fname, n=0, image_metadata={}, xisf_metadata={}):
        """Convenience method for reading a file containing a single image.
        Args:
            fname (string): filename
            n (int, optional): index of the image to extract (in the list returned by get_images_metadata()). Defaults to 0.
            image_metadata (dict, optional): dictionary that will be updated with the metadata of the image.
            xisf_metadata (dict, optional): dictionary that will be updated with the metadata of the file.
        Returns:
            [np.ndarray]: Numpy ndarray with the image data, in the requested format (channels_first or channels_last).
        """
        xisf = XISF(fname)
        xisf_metadata.update(xisf.get_file_metadata())
        image_metadata.update(xisf.get_images_metadata()[n])
        return xisf.read_image(n)

    # if 'colorSpace' is not specified, im_data.shape[2] dictates if colorSpace is 'Gray' or 'RGB'
    # For float sample formats, bounds="0:1" is assumed
    @staticmethod
    def write(fname, im_data, creator_app=None, image_metadata={}, xisf_metadata={},
              codec=None, shuffle=False, level=None):
        """Writes an image (numpy array) to a XISF file. Compression may be requested but it only
        will be used if it actually reduces the data size.
        Args:
            fname: filename (will overwrite if existing)
            im_data: numpy ndarray with the image data
            creator_app: string for XISF:CreatorApplication file property (defaults to python version in None provided)
            image_metadata: dict with the same structure described for m_i in get_images_metadata().
              Only 'FITSKeywords' and 'XISFProperties' keys are actually written, the rest are derived from im_data.
            xisf_metadata: file metadata, dict with the same structure returned by get_file_metadata()
            codec: compression codec ('zlib', 'lz4' or 'lz4hc'), or None to disable compression
            shuffle: whether to apply byte-shuffling before compression (ignored if codec is None). Recommended
              for 'lz4' and 'lz4hc' compression algorithms.
            level: for zlib, 1..9 (default: 6); for lz4hc, 1..12 (default: 9). Higher means more compression.
        Returns:
            bytes_written: the total number of bytes written into the output file.
            codec: The codec actually used, i.e., None if compression did not reduce the data block size so
            compression was not finally used.
        """
        # Update Image metadata
        image_attrs = {}
        if im_data.shape[2] == 3 or im_data.shape[2] == 1:
            data_format = 'channels_last'
            geometry = (im_data.shape[1], im_data.shape[0], im_data.shape[2])
            channels = im_data.shape[2]
        else:
            data_format = 'channels_first'
            geometry = im_data.shape
            channels = im_data.shape[0]
        image_attrs['geometry'] = "%d:%d:%d" % geometry
        image_attrs['colorSpace'] = image_attrs.get('colorSpace',
                                                    'Gray' if channels == 1 else 'RGB')
        image_attrs['sampleFormat'] = XISF._get_sampleFormat(im_data.dtype)
        if image_attrs['sampleFormat'].startswith("Float"):
            image_attrs['bounds'] = "0:1"  # Assumed
        if sys.byteorder == 'big' and image_attrs['sampleFormat'] != 'UInt8':
            image_attrs['byteOrder'] = 'big'

        # Rearrange for data_format
        data_block = np.transpose(im_data, (
        2, 0, 1)) if data_format == 'channels_last' else im_data
        data_block = data_block.tobytes()

        uncompressed_size = im_data.size * im_data.itemsize

        # Compression
        if codec is None:
            data_size = uncompressed_size
        else:
            if shuffle:
                compressed_block = XISF._shuffle(data_block, im_data.itemsize)
                codec_str = codec + "+sh"
            else:
                compressed_block = data_block

            if codec == 'lz4hc':
                level = level if level else XISF._compression_def_level['lz4hc']
                compressed_block = lz4.block.compress(
                    compressed_block,
                    mode='high_compression',
                    compression=level,
                    store_size=False
                )
            elif codec == 'lz4':
                compressed_block = lz4.block.compress(compressed_block,
                                                      store_size=False)
            elif codec == 'zlib':
                level = level if level else XISF._compression_def_level['zlib']
                compressed_block = zlib.compress(compressed_block, level=level)
            else:
                raise NotImplementedError(
                    "Unimplemented compression codec %s" % (codec,))

            compressed_size = len(compressed_block)

            if compressed_size < uncompressed_size:
                # The ideal situation, compressing actually reduces size
                data_block, data_size = compressed_block, compressed_size

                # Add 'compression' image attribute: (codec:uncompressed-size[:item-size])
                image_attrs[
                    'compression'] = f"{codec_str}:{uncompressed_size}:{im_data.itemsize}" if shuffle else f"{codec_str}:{uncompressed_size}"

                # Add XISF:CompressionCodecs and XISF:CompressionLevel to file metadata
                xisf_metadata['XISF:CompressionCodecs'] = {
                    'id': 'XISF:CompressionCodecs',
                    'type': 'String',
                    'value': codec
                }
                xisf_metadata['XISF:CompressionLevel'] = {
                    'id': 'XISF:CompressionLevel',
                    'type': 'Int',
                    'value': level if level else XISF._compression_def_level[codec]
                }
            else:
                # If there's no gain in compressing,, just discard the compressed block
                # See https://pixinsight.com/forum.old/index.php?topic=10942.msg68043#msg68043
                # (In fact, PixInsight will show garbage image data if the data block is
                # compressed but the uncompressed size is smaller)
                codec = None
                data_size = uncompressed_size

        # Assemble location attribute, provisional until we get the data block position
        image_attrs['location'] = ':'.join(('attachment', "", str(data_size)))

        # Create file metadata
        xisf_metadata['XISF:CreationTime'] = {
            'id': 'XISF:CreationTime',
            'type': 'String',
            'value': datetime.utcnow().isoformat()
        }
        xisf_metadata['XISF:CreatorApplication'] = {
            'id': 'XISF:CreatorApplication',
            'type': 'String',
            'value': creator_app if creator_app else XISF._creator_app
        }
        xisf_metadata['XISF:CreatorModule'] = {
            'id': 'XISF:CreatorModule',
            'type': 'String',
            'value': XISF._creator_module
        }
        _OSes = {
            'linux': 'Linux',
            'win32': 'Windows',
            'cygwin': 'Windows',
            'darwin': 'macOS'
        }
        xisf_metadata['XISF:CreatorOS'] = {
            'id': 'XISF:CreatorOS',
            'type': 'String',
            'value': _OSes[sys.platform]
        }

        # Convert metadata (dict) to XML Header
        xisf_header_xml = ET.Element('xisf', XISF._xisf_attrs)

        # Image
        image_xml = ET.SubElement(xisf_header_xml, 'Image', image_attrs)

        # Auxiliary function to insert XISF properties in the XML tree
        def _insert_property(parent, property_dict):
            if property_dict['type'] == 'String':
                ET.SubElement(parent, 'Property', {
                    'id': property_dict['id'],
                    'type': property_dict['type'],
                }).text = str(property_dict['value'])
            else:
                ET.SubElement(parent, 'Property', {
                    'id': property_dict['id'],
                    'type': property_dict['type'],
                    'value': str(property_dict['value'])
                })

                #   Image XISFProperties

        for property_dict in image_metadata.get('XISFProperties', {}).values():
            _insert_property(image_xml, property_dict)

        #   Image FITSKeywords
        for keyword_name, data in image_metadata.get('FITSKeywords', {}).items():
            for entry in data:
                ET.SubElement(image_xml, 'FITSKeyword', {
                    'name': keyword_name,
                    'value': entry['value'],
                    'comment': entry['comment']
                })

        # File Metadata
        metadata_xml = ET.SubElement(xisf_header_xml, 'Metadata')
        for property_dict in xisf_metadata.values():
            _insert_property(metadata_xml, property_dict)

        # Headers combined length without attachment position in XML header
        provisional_xisf_header = ET.tostring(xisf_header_xml, encoding='utf8')
        len_wo_pos = len(XISF._signature) + XISF._headerlength_len + len(
            provisional_xisf_header) + XISF._reserved_len
        # First estimation of data block position
        provisional_pos = len_wo_pos + len(str(len_wo_pos))
        # Definitive data block position
        data_block_pos = len_wo_pos + len(str(provisional_pos))
        # Update data block position in XML Header
        image_attrs['location'] = ':'.join(
            ('attachment', str(data_block_pos), str(data_size)))
        image_xml.set('location', image_attrs['location'])

        with open(fname, "wb") as f:
            # Write XISF signature
            f.write(XISF._signature)

            xisf_header = ET.tostring(xisf_header_xml, encoding='utf8')
            headerlength = len(xisf_header)
            # Write header length
            f.write(
                headerlength.to_bytes(XISF._headerlength_len, byteorder='little'))

            # Write reserved field
            reserved_field = (0).to_bytes(XISF._reserved_len, byteorder='little')
            f.write(reserved_field)

            # Write header
            f.write(xisf_header)

            # Write data block
            assert (data_block_pos == f.tell())
            f.write(data_block)
            bytes_written = f.tell()

        return bytes_written, codec

    # Auxiliary functions to parse some metadata attributes
    # Returns image shape, e.g. (x, y, channels)
    @staticmethod
    def _parse_geometry(g):
        return tuple(map(int, g.split(':')))

    # Returns (position, size)
    @staticmethod
    def _parse_location(l):
        ll = l.split(':')
        if ll[0] != 'attachment':
            raise NotImplementedError(
                "Image location type '%s' not implemented" % (ll[0],))
        return tuple(map(int, ll[1:]))

    # Return equivalent numpy dtype
    @staticmethod
    def _parse_sampleFormat(s):
        _dtypes = {
            'UInt8': np.dtype('uint8'),
            'UInt16': np.dtype('uint16'),
            'UInt32': np.dtype('uint32'),
            'Float32': np.dtype('float32'),
            'Float64': np.dtype('float64'),
        }
        try:
            dtype = _dtypes[s]
        except:
            raise NotImplementedError("sampleFormat %s not implemented" % (s,))
        return dtype

    # Return XISF data type from numpy dtype
    @staticmethod
    def _get_sampleFormat(dtype):
        _sampleFormats = {
            'uint8': 'UInt8',
            'uint16': 'UInt16',
            'uint32': 'UInt32',
            'float32': 'Float32',
            'float64': 'Float64',
        }
        try:
            sampleFormat = _sampleFormats[str(dtype)]
        except:
            raise NotImplementedError("sampleFormat %s not implemented" % (dtype,))
        return sampleFormat

    # Returns (codec, uncompressed_size, item_size); item_size is None if not using byte shuffling
    @staticmethod
    def _parse_compression(c):
        cl = c.split(':')
        if len(cl) == 3:  # (codec+byteshuffling, uncompressed_size, shuffling_item_size)
            return (cl[0], int(cl[1]), int(cl[2]))
        else:  # (codec, uncompressed_size, None)
            return (cl[0], int(cl[1]), None)

    # Auxiliary function to implement un-byteshuffling with numpy
    @staticmethod
    def _unshuffle(d, item_size):
        a = np.frombuffer(d, dtype=np.dtype('uint8'))
        a = a.reshape((item_size, -1))
        return np.transpose(a).tobytes()

        # Auxiliary function to implement byteshuffling with numpy

    @staticmethod
    def _shuffle(d, item_size):
        a = np.frombuffer(d, dtype=np.dtype('uint8'))
        a = a.reshape((-1, item_size))
        return np.transpose(a).tobytes()