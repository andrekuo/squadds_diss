import numpy as np
from qiskit_metal import Dict
from qiskit_metal.qlibrary.core import QRoute, QRoutePoint
from qiskit_metal.qlibrary.core import QComponent
from cavity_feedline import CavityFeedline
from qiskit_metal.qlibrary.qubits.transmon_cross import TransmonCross
from qiskit_metal.qlibrary.tlines.straight_path import RouteStraight
import pyEPR as epr
from pyEPR.ansys import parse_units


class QubitDriveline(QComponent):
    
    default_options = Dict(
        chip = 'main',
        driveline_options = Dict(
            coupling_type = 'capacitive',
            connector_length = '50um',
            # coupler_options = Dict(
            orientation = '180',
            coupling_length = '200um'
            # )
        ),
        qubit_options = Dict(
            cross_width='20um',
            cross_length='200um',
            cross_gap='20um',
            orientation = '180',
            chip='main',
            connection_pads = Dict(
                readout = Dict(
                    connector_type='0',  # 0 = Claw type, 1 = gap type
                    claw_length='30um',
                    ground_spacing='5um',
                    claw_width='10um',
                    claw_gap='6um',
                    claw_cpw_length='0um',
                    claw_cpw_width='10um',
                    connector_location=
                    '90'  # 0 => 'west' arm, 90 => 'north' arm, 180 => 'east' arm
                ),
            ),
        )
    )
    
    component_metadata = Dict(short_name='qubitdriveline')
    """Component metadata"""

    # default_options = Dict(meander=Dict(spacing='200um', asymmetry='0um'),
    #                        snap='true',
    #                        prevent_short_edges='true')
    """Default options"""

    def copier(self, d, u):
        for k, v in u.items():
            if not isinstance(v, str) and not isinstance(v, float) and not isinstance(v, bool):
                d[k] = self.copier(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    
    def make(self):
        p = self.p
        self.make_coupler()
        self.make_qubit()
        self.make_connector()
        self.make_pins()
        
    def make_qubit(self):
        p = self.p

        qubit_opts = Dict()
        self.copier(qubit_opts, p.qubit_options)
        cplr = self.coupler

        qubit_offset = sum(parse_units([cplr.options.prime_gap, cplr.options.second_gap, cplr.options.coupling_space, cplr.options.down_length])) # adding CLT vertical height
        qubit_offset += sum(parse_units([cplr.options.prime_width, cplr.options.second_width]))/2 # part of CLT height, but need to be divided by 

        qubit_offset += parse_units(p.driveline_options.connector_length) # adding length of straight connector between xmon and CLT

        qclaw = p.qubit_options.connection_pads['readout']
        qubit_offset += sum(parse_units([qclaw.claw_gap, qclaw.claw_width, qclaw.ground_spacing, p.qubit_options.cross_gap, p.qubit_options.cross_length])) # adding xmon vertical height

        qubit_opts['pos_y'] = str(qubit_offset*1E6) + 'um'
        self.qubit = TransmonCross(self.design, "{}_xmon".format(self.name), options = qubit_opts)

    def make_coupler(self):
        p = self.p

        coupler_opts = Dict()
        self.copier(coupler_opts, p.driveline_options)#['coupler_options'])

        coupler_opts['pos_x'] = p.driveline_options['coupling_length']/2
        if(p.driveline_options['coupling_type'] == "capacitive"):
            from qiskit_metal.qlibrary.couplers.coupled_line_tee import CoupledLineTee
            self.coupler = CoupledLineTee(self.design, "{}_cap_coupler".format(self.name), options=coupler_opts)
        elif(p.driveline_options['coupling_type'] == 'inductive'):
            from inductive_coupler import InductiveCoupler
            self.coupler = InductiveCoupler(self.design, "{}_ind_coupler".format(self.name), options=coupler_opts)
        elif(p.driveline_options['coupling_type'] == 'interdigitated'):
            from qiskit_metal.qlibrary.couplers.cap_n_interdigital_tee import CapNInterdigitalTee
            self.coupler = CapNInterdigitalTee(self.design, '{}_capn_coupler'.format(self.name), options=coupler_opts)

    def make_connector(self):
        p = self.p

        connector_opts = Dict(
            pin_inputs = Dict(
                start_pin = Dict(
                    component = self.qubit.name,
                    pin = 'readout'
                ),
                end_pin = Dict(
                    component = self.coupler.name,
                    pin = 'second_end'
                )
            )
        )
        self.connector = RouteStraight(self.design, f"{self.name}.connector", options = connector_opts)
        
    def make_pins(self):
        start_dict = self.coupler.get_pin('prime_start')
        end_dict = self.coupler.get_pin('prime_end')
        self.add_pin('prime_start', start_dict['points'], start_dict['width'])
        self.add_pin('prime_end', end_dict['points'], end_dict['width'])
