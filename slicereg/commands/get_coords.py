from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from slicereg.commands.base import BaseSectionRepo
from slicereg.commands.utils import Signal
from slicereg.models.registration import Registration
from slicereg.repos.atlas_repo import AtlasRepo


class ImageCoord(NamedTuple):
    i: int
    j: int

class AtlasCoord(NamedTuple):
    x: float
    y: float
    z: float

@dataclass
class GetPixelRegistrationDataCommand:
    _repo: BaseSectionRepo
    _atlas_repo: AtlasRepo
    coord_data_requested: Signal = Signal()

    def __call__(self, i: int, j: int):
        sections = self._repo.sections
        if not sections:
            return
        section = sections[0]
        x, y, z = section.map_ij_to_xyz(i=i, j=j)
        self.coord_data_requested.emit(image_coords=ImageCoord(i=i, j=j), atlas_coords=AtlasCoord(x=x, y=y, z=z))
