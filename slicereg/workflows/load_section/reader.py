import tifffile
import xmltodict
from numpy import uint16

from slicereg.workflows.load_section.workflow import BaseSectionReader, SliceImageData
from slicereg.models.section import Section


class OmeTiffReader(BaseSectionReader):

    def read(self, filename: str) -> SliceImageData:
        f = tifffile.TiffFile(filename)
        image = f.asarray()
        assert image.ndim == 3
        assert image.dtype == uint16

        metadata = xmltodict.parse(f.ome_metadata)
        pix_mdata = metadata['OME']['Image']['Pixels']
        res_x, res_y = pix_mdata['@PhysicalSizeX'], pix_mdata['@PhysicalSizeY']
        assert res_x == res_y, \
            "Pixels are not square"

        return SliceImageData(channels=image, pixel_resolution_um=float(res_x))
