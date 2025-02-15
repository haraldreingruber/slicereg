from __future__ import annotations

import numpy as np
from PySide2.QtWidgets import QWidget
from vispy.scene import SceneCanvas, ViewBox, TurntableCamera, Image
from vispy.scene.events import SceneMouseEvent
from vispy.visuals.filters import ColorFilter

from slicereg.gui.view_models.slice import SliceViewDTO
from slicereg.gui.views.base import BaseQtWidget, BaseView


class SliceView(BaseQtWidget, BaseView):

    def __init__(self):
        self._canvas = SceneCanvas()

        self._viewbox = ViewBox(parent=self._canvas.scene)
        self._canvas.central_widget.add_widget(self._viewbox)

        self._viewbox.camera = TurntableCamera(
            interactive=False,
            fov=0,  # Makes it an ortho camera.
            azimuth=0,
            elevation=-90,
        )

        self._reference_slice = Image(cmap='grays', parent=self._viewbox.scene)
        self._reference_slice.attach(ColorFilter((1., .5, 0., 1.)))
        self._reference_slice.set_gl_state('additive', depth_test=False)

        self._slice = Image(cmap='grays', parent=self._viewbox.scene)
        self._slice.attach(ColorFilter((0., .5, 1., 1.)))
        self._slice.set_gl_state('additive', depth_test=False)

    def on_registration(self, model):
        def _vispy_mouse_event(event: SceneMouseEvent) -> None:
            if event.type == 'mouse_press':
                event.handled = True

            elif event.type == 'mouse_move':
                if event.press_event is None:
                    return
                x1, y1 = event.last_event.pos
                x2, y2 = event.pos
                if event.button == 1:  # Left Mouse Button
                    model.on_left_mouse_drag(x1=x1, x2=x2, y1=y1, y2=y2)
                elif event.button == 2:  # Right Mouse Button
                    model.on_right_mouse_drag(x1=x1, y1=y1, x2=x2, y2=y2)

            elif event.type == 'mouse_wheel':
                model.on_mousewheel_move(increment=int(event.delta[1]))

        self._canvas.events.mouse_press.connect(_vispy_mouse_event)
        self._canvas.events.mouse_move.connect(_vispy_mouse_event)
        self._canvas.events.mouse_release.connect(_vispy_mouse_event)
        self._canvas.events.mouse_wheel.connect(_vispy_mouse_event)

    @property
    def qt_widget(self) -> QWidget:
        return self._canvas.native

    def update(self, dto):
        dto: SliceViewDTO

        if (image := dto.section_image) is not None:
            self._slice.set_data(image)
            self._viewbox.camera.center = image.shape[1] / 2, image.shape[0] / 2, 0.
            self._viewbox.camera.scale_factor = image.shape[1]

        if (clim := dto.clim) is not None:
            self._slice.clim = clim

        if (image := dto.atlas_image) is not None:
            self._reference_slice.set_data(image)
            self._reference_slice.clim = (np.min(image), np.max(image)) if np.max(image) - np.min(image) > 0 else (0, 1)

        self._canvas.update()
