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
    
    default_options = Dict(
        # wavelength = '...', # acceptable inputs ['quarter', 'half']
        
        coupling_type = 'capacitive',
        coupler_options = Dict(
                           prime_width='10um',
                           prime_gap='6um',
                           second_width='10um',
                           second_gap='6um',
                           coupling_space='3um',
                           coupling_length='100um',
                           down_length='100um',
                           fillet='25um',
                           mirror=False,
                           open_termination=True,
                        ),
        cpw_options = Dict(
                            total_length='3000um',
                            pin_inputs = Dict(
                                start_pin = Dict(
                                    component = None,
                                    pin = None
                                ),
                                end_pin = Dict(
                                    component = None,
                                    pin = None
                                ),
                            ),
                            left_opts = Dict(meander=Dict(spacing='200um', asymmetry='0um'),
                                                snap='true',
                                                prevent_short_edges='true'),
                            right_opts = Dict(meander=Dict(spacing='200um', asymmetry='0um'),
                                                snap='true',
                                                prevent_short_edges='true')
                        ),
        # total_length = '3000um',
        # fillet = '50um',
        # coupling = dict(
        #     coupling_type = 'capacitive', # acceptable inputs ['capacitive', 'inductive']
        #     coupling_length = '100um',
        #     coupling_space = '3um',
        #     open_termination=True,
        #     fillet='25um',
        #     down_length='100um'
        # ),
        # cavity = dict(
        #     trace_width = '10um',
        #     trace_gap = '6um',
        #     spacing = '200um',
        #     fillet = '50um'
        # ),
        # feedline = dict(
        #     trace_width = '10um',
        #     trace_gap = '6um'
        # ),
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
        # cpw_options = Dict(),
        mirror=False
    )
    
    component_metadata = Dict(short_name='cpw')
    """Component metadata"""

    # default_options = Dict(meander=Dict(spacing='200um', asymmetry='0um'),
    #                        snap='true',
    #                        prevent_short_edges='true')
    """Default options"""
    # coupler = None

    def make(self):
        p = self.p
        self.make_coupler()

        # self.make_pin(self, p.wavelength)
        self.make_cpws()

        # self.add_pin()

    def make_coupler(self):
        p = self.p

        temp_opts = Dict()
        for k in p.coupler_options:
            temp_opts.update({k:p.coupler_options[k]})

        if(p.coupling_type == "capacitive"):
            from qiskit_metal.qlibrary.couplers.coupled_line_tee import CoupledLineTee
            self.coupler = CoupledLineTee(self.design, "{}_cap_coupler".format(self.name), options=temp_opts)
        elif(p.coupling_type == 'inductive'):
            from inductive_coupler import InductiveCoupler
            self.coupler = InductiveCoupler(self.design, "{}_ind_coupler".format(self.name), options=temp_opts)

        # # p = coupler_options
        # p = self.p

        # prime_cpw_length = p.coupling.coupling_length * 2
        # second_flip = 1
        # if p.mirror:
        #     second_flip = -1

        # #Primary CPW
        # prime_cpw = draw.LineString([[-prime_cpw_length / 2, 0],
        #                              [prime_cpw_length / 2, 0]])

        # #Secondary CPW
        # second_down_length = p.coupling.down_length
        # second_y = -p.feedline.trace_width / 2 - p.feedline.trace_gap - p.coupling.coupling_space - p.cavity.trace_gap - p.cavity.trace_width / 2

        # LS_arr = ([[second_flip * (-p.coupling.coupling_length / 2), second_y - second_down_length]] if (p.coupling.coupling_type == "inductive") else []) + [[second_flip * (-p.coupling.coupling_length / 2), second_y],
        #      [second_flip * (p.coupling.coupling_length / 2), second_y],
        #      [
        #          second_flip * (p.coupling.coupling_length / 2),
        #          second_y - second_down_length
        #      ]]

        # second_cpw = draw.LineString(LS_arr)

        # if(p.coupling.coupling_type == "capacitive"):
        #     second_termination = 0
        #     if p.coupling.open_termination:
        #         second_termination = p.cavity.trace_gap

        #     second_cpw_etch = draw.LineString(
        #         [[
        #             second_flip * (-p.coupling.coupling_length / 2 - second_termination),
        #             second_y
        #         ], [second_flip * (p.coupling.coupling_length / 2), second_y],
        #         [
        #             second_flip * (p.coupling.coupling_length / 2),
        #             second_y - second_down_length
        #         ]])

        # #Rotate and Translate
        # items_arr = [prime_cpw, second_cpw] + [second_cpw_etch] if (p.coupling.coupling_type == "capacitive") else []
        # c_items = items_arr
        # c_items = draw.rotate(c_items, p.orientation, origin=(0, 0))
        # c_items = draw.translate(c_items, p.pos_x, p.pos_y)
        # items_arr = c_items

        # #Add to qgeometry tables
        # self.add_qgeometry('path', {'prime_cpw': prime_cpw},
        #                    width=p.feedline.trace_width)
        # self.add_qgeometry('path', {'prime_cpw_sub': prime_cpw},
        #                    width=p.feedline.trace_width + 2 * p.feedline.trace_gap,
        #                    subtract=True)
        # self.add_qgeometry('path', {'second_cpw': second_cpw},
        #                    width=p.cavity.trace_width,
        #                    fillet=p.coupling.fillet)
        # self.add_qgeometry('path', {'second_cpw_sub': second_cpw_etch if (p.coupling.coupling_type == "capacitive") else second_cpw},
        #                    width=p.cavity.trace_width + 2 * p.cavity.trace_gap,
        #                    subtract=True,
        #                    fillet=p.coupling.fillet)
        

        # #Add pins
        # prime_pin_list = prime_cpw.coords
        # second_pin_list = second_cpw.coords

        # self.add_pin('prime_start',
        #              points=np.array(prime_pin_list[::-1]),
        #              width=p.feedline.trace_width,
        #              input_as_norm=True)
        # self.add_pin('prime_end',
        #              points=np.array(prime_pin_list),
        #              width=p.feedline.trace_width,
        #              input_as_norm=True)


    # def make_pin(self, wavelength):
    #     if (wavelength == "quarter"):
    #         import OpenToGround
    #         ....
    #     elif (wavelength == "half"):
    #         import ShortToGround
    #         ...

    def make_cpws(self):
        from qiskit_metal.qlibrary.tlines.meandered import RouteMeander

        print("#############################")
        print(self.coupler.name)

        p = self.p
        
        left_opts = Dict()
        for k in p.cpw_options.left_opts:
            left_opts.update({k:p.cpw_options.left_opts[k]})
        left_opts.update({'total_length': (p.cpw_options.total_length if p.coupling_type == 'capacitive' else p.cpw_options.total_length/2) })
        left_opts['pin_inputs']['end_pin'].update({'component':self.coupler.name})
        left_opts['pin_inputs']['end_pin'].update({'pin':'second_end'})
        

        if(p.coupling_type == 'inductive'):
            right_opts = Dict()
            for k in p.cpw_options.right_opts:
                right_opts.update({k:p.cpw_options.right_opts[k]})
            right_opts.update({'total_length':p.cpw_options.total_length/2})
            right_opts['pin_inputs']['start_pin'].update({'component':self.coupler.name})
            right_opts['pin_inputs']['start_pin'].update({'pin':'second_start'})

            RightMeander = RouteMeander(self.design, "{}_right_cpw".format(self.name), options = right_opts)

        LeftMeander = RouteMeander(self.design, "{}_left_cpw".format(self.name), options = left_opts)