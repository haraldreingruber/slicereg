from __future__ import annotations

from dataclasses import field, dataclass
from typing import List, Tuple, Optional

from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QComboBox, QLineEdit, QHBoxLayout, QLabel

from slicereg.commands.utils import Signal
from slicereg.gui.app_model import AppModel
from slicereg.gui.views.base import BaseQtWidget, BaseView
from slicereg.gui.views.slider import LabelledSliderWidget
from vendor.napari_qrange_slider.qt_range_slider import QHRangeSlider


class SidebarView(BaseQtWidget, BaseView):

    def __init__(self):
        BaseView.__init__(self)

        self.widget = QWidget()

        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        # Load atlas controls
        load_atlas_layout = QHBoxLayout()
        load_atlas_layout.addWidget(QLabel(text='Res (μm):'))

        self.resolution_textbox = QLineEdit()
        load_atlas_layout.addWidget(self.resolution_textbox)

        self.load_atlas_from_file_button = QPushButton("Load Atlas File")
        load_atlas_layout.addWidget(self.load_atlas_from_file_button)

        layout.addLayout(load_atlas_layout)

        self.update_bgatlas_button = QPushButton("Update Brainglobe Atlases")
        layout.addWidget(self.update_bgatlas_button)

        self.list_atlas_dropdown = QComboBox()
        layout.addWidget(self.list_atlas_dropdown)

        self.load_atlas_button = QPushButton("Load Atlas")
        layout.addWidget(self.load_atlas_button)

        # Load Section Buttons
        self.load_image_putton = QPushButton("Load Section")
        layout.addWidget(self.load_image_putton)

        self.quick_load_section_button = QPushButton("Quick Load Section")
        layout.addWidget(self.quick_load_section_button)

        # Scale Sliders (Set Section Resolution)
        self.resample_widget = LabelledSliderWidget(min=15, max=200, label="Resample")
        layout.addLayout(self.resample_widget.layout)

        self.resolution_widget = LabelledSliderWidget(min=1, max=100, label="Resolution")
        layout.addLayout(self.resolution_widget.layout)

        # Movement Sliders
        self.x_slider = LabelledSliderWidget(min=-10000, max=10000, label='x')
        layout.addLayout(self.x_slider.layout)

        self.y_slider = LabelledSliderWidget(min=-10000, max=10000, label='y')
        layout.addLayout(self.y_slider.layout)

        self.z_slider = LabelledSliderWidget(min=-10000, max=10000, label='z')
        layout.addLayout(self.z_slider.layout)

        self.rotx_slider = LabelledSliderWidget(min=-180, max=180, label='rotx')
        layout.addLayout(self.rotx_slider.layout)

        self.roty_slider = LabelledSliderWidget(min=-180, max=180, label='roty')
        layout.addLayout(self.roty_slider.layout)

        self.rotz_slider = LabelledSliderWidget(min=-180, max=180, label='rotz')
        layout.addLayout(self.rotz_slider.layout)

        # Quick-rotation buttons
        buttons_layout = QHBoxLayout()

        self.coronal_button = QPushButton("Coronal")
        buttons_layout.addWidget(self.coronal_button)

        self.sagittal_button = QPushButton("Sagittal")
        buttons_layout.addWidget(self.sagittal_button)

        self.axial_button = QPushButton("Axial")
        buttons_layout.addWidget(self.axial_button)

        layout.addLayout(buttons_layout)

        # clim sliders
        self.slice_clim_slider = QHRangeSlider(initial_values=(0., 1.), data_range=(0., 1.), step_size=0.01)
        layout.addWidget(self.slice_clim_slider)

        self.volume_slice_clim_slider = QHRangeSlider(initial_values=(0., 1.), data_range=(0., 1.), step_size=0.01)
        layout.addWidget(self.volume_slice_clim_slider)

    def on_registration(self, model):
        def show_load_image_dialog():
            filename, filetype = QFileDialog.getOpenFileName(
                parent=self.qt_widget,
                caption="Load Image",
                dir="../../../data/RA_10X_scans/MeA",
                filter="OME-TIFF (*.ome.tiff)"
            )
            if not filename:
                return
            model.submit_load_section_from_file(filename=filename)

        def show_load_atlas_dialog():
            filename, filetype = QFileDialog.getOpenFileName(
                parent=self.qt_widget,
                caption="Load Atlas from File",
                dir="..",
                filter="Image Files (*.tif *.tiff *.nii)"
            )
            if not filename:
                return
            model.submit_load_atlas_from_file(filename=filename)

        self.resolution_textbox.textEdited.connect(model.update_resolution_textbox)
        self.load_atlas_from_file_button.clicked.connect(show_load_atlas_dialog)
        self.update_bgatlas_button.clicked.connect(model.click_update_bgatlas_list_button)
        self.list_atlas_dropdown.currentTextChanged.connect(model.change_bgatlas_selection_dropdown)
        self.load_atlas_button.clicked.connect(model.click_load_bgatlas_button)
        self.load_image_putton.clicked.connect(show_load_image_dialog)
        self.quick_load_section_button.clicked.connect(model.click_quick_load_section_button)
        self.resample_widget.connect(model.slide_resample_slider)
        self.resolution_widget.connect(model.slide_resolution_slider)
        self.x_slider.connect(model.change_x_slider)
        self.y_slider.connect(model.change_y_slider)
        self.z_slider.connect(model.change_z_slider)
        self.rotx_slider.connect(model.change_rotx_slider)
        self.roty_slider.connect(model.change_roty_slider)
        self.rotz_slider.connect(model.change_rotz_slider)
        self.coronal_button.clicked.connect(model.click_coronal_button)
        self.sagittal_button.clicked.connect(model.click_sagittal_button)
        self.axial_button.clicked.connect(model.click_axial_button)
        self.slice_clim_slider.valuesChanged.connect(model.move_clim_slice_slider)
        self.volume_slice_clim_slider.valuesChanged.connect(model.move_clim_volume_slider)

    @property
    def qt_widget(self) -> QWidget:
        return self.widget

    def update(self, **kwargs) -> None:
        if (bgatlas_names := kwargs.get('bgatlas_names')) is not None:
            self.list_atlas_dropdown.clear()
            self.list_atlas_dropdown.addItems(bgatlas_names)


@dataclass(unsafe_hash=True)
class SidebarViewModel:
    _model: AppModel = field(hash=False)
    selected_bgatlas: Optional[str] = None
    loadatlas_resolution: Optional[int] = None
    updated: Signal = field(default_factory=Signal)

    def __post_init__(self):
        self._model.updated.connect(self.update)

    def update(self, **kwargs):
        print(self.__class__.__name__, f"updated {kwargs}")
        self.updated.emit(**kwargs)

    @property
    def clim_2d(self) -> Tuple[float, float]:
        return self._model.clim_2d

    @property
    def clim_3d(self) -> Tuple[float, float]:
        return self._model.clim_3d

    @property
    def bgatlas_names(self) -> List[str]:
        return self._model.bgatlas_names

    def click_coronal_button(self):
        self._model.update_section(rx=0, ry=0, rz=-90)

    def click_sagittal_button(self):
        self._model.update_section(rx=90, ry=0, rz=-90)

    def click_axial_button(self):
        self._model.update_section(rx=0, ry=90, rz=-90)

    def move_clim_slice_slider(self, values: Tuple[int, int]):
        self._model.clim_2d = values

    def move_clim_volume_slider(self, values: Tuple[int, int]):
        self._model.clim_3d = values

    def click_quick_load_section_button(self):
        self._model.load_section("data/RA_10X_scans/MeA/S1_07032020.ome.tiff")

    def slide_resample_slider(self, val: int):
        self._model.resample_section(val)

    def slide_resolution_slider(self, val: int):
        self._model.update_section(res=val)

    def click_update_bgatlas_list_button(self):
        self._model.list_bgatlases()

    def submit_load_atlas_from_file(self, filename: str):
        if self.loadatlas_resolution is None:
            return
        self._model.load_atlas_from_file(filename=filename, resolution_um=self.loadatlas_resolution)

    def click_load_bgatlas_button(self):
        print(f"Loading Atlas: {self.selected_bgatlas}")
        self._model.load_bgatlas(name=self.selected_bgatlas)

    def change_bgatlas_selection_dropdown(self, text: str):
        self.selected_bgatlas = text

    def submit_load_section_from_file(self, filename: str):
        self._model.load_section(filename=filename)

    def change_x_slider(self, value: int):
        self._model.update_section(x=value)

    def change_y_slider(self, value: int):
        self._model.update_section(y=value)

    def change_z_slider(self, value: int):
        self._model.update_section(z=value)

    def change_rotx_slider(self, value: int):
        self._model.update_section(rx=value)

    def change_roty_slider(self, value: int):
        self._model.update_section(ry=value)

    def change_rotz_slider(self, value: int):
        self._model.update_section(rz=value)

    def update_resolution_textbox(self, text: str):
        self.loadatlas_resolution = int(text)
