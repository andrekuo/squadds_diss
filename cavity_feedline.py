from typing import List, Tuple, Union

from numpy.linalg import norm

import numpy as np
from qiskit_metal import Dict
from qiskit_metal.toolbox_metal.parsing import is_true
from qiskit_metal.qlibrary.core import QRoute, QRoutePoint
from qiskit_metal.toolbox_metal import math_and_overrides as mao
from qiskit_metal.toolbox_metal.exceptions import QiskitMetalDesignError

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np

from qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround


class CavityFeedline(QComponent):
    
    default_settings = dict(
        # wavelength = '...', # acceptable inputs ['quarter', 'half']
        total_length = '3000um',
        fillet = '50um',
        coupling = dict(
            coupling_type = 'capacitive', # acceptable inputs ['capacitive', 'inductive']
            coupling_length = '100um',
            coupling_space = '3um',
        ),
        cavity = dict(
            trace_width = '10um',
            trace_gap = '6um'
        ),
        feedline = dict(
            trace_width = '10um',
            trace_gap = '6um'
        ),
        # pin_options = dict(
        #     start = dict(
        #         component = 'component name',
        #         pin = ''
        #     ),
        #     start = dict(
        #         component = None, # if None, use wavelength (so either open or shorted to ground)
        #         pin = None
        #     )
        # )
    )
    
    component_metadata = Dict(short_name='cpw')
    """Component metadata"""

    default_options = Dict(meander=Dict(spacing='200um', asymmetry='0um'),
                           snap='true',
                           prevent_short_edges='true')
    """Default options"""

    def make(self):
        p = self.p

        print("############################")
        coupler_opts = dict(
                           prime_width=p.feedline.trace_width,
                           prime_gap=p.feedline.trace_gap,
                           second_width=p.cavity.trace_width,
                           second_gap=p.cavity.trace_gap,
                           coupling_space=p.coupling.coupling_space,
                           coupling_length=p.coupling.coupling_length
                        )
        print(coupler_opts)
        self.make_coupler(self, coupler_opts)
        # self.make_pin(self, p.wavelength)
        # self.make_cpws(self, p.wavelength, p.cavity)

    def make_coupler(self, coupler_options):
        p = self.p
        from qiskit_metal.qlibrary.couplers.coupled_line_tee import CoupledLineTee
        CoupledLineTee(self.design, "{p.name}_coupler", options=coupler_options)

    # def make_pin(self, wavelength):
    #     if (wavelength == "quarter"):
    #         import OpenToGround
    #         ....
    #     elif (wavelength == "half"):
    #         import ShortToGround
    #         ...

    # def make_cpws(self, p.wavelength, p.cavity):
    #     import RouteMeander
    #     LeftMeander = RouteMeander(design, ....)
    #     RightMeander = RouteMeander(design, ....)