import numpy as np
from qiskit_metal import Dict
from qiskit_metal.qlibrary.core import QRoute, QRoutePoint
from qiskit_metal.qlibrary.core import QComponent
from cavity_feedline import CavityFeedline
from qiskit_metal.qlibrary.qubits.transmon_cross import TransmonCross
from just_claw import TransmonClaw

class ClawCavity(QComponent):
    
    default_options = Dict(
        chip = 'main',
        cavity_options = Dict(
            coupling_type = 'capacitive',
            coupler_options = Dict(
                orientation = '180',
                coupling_length = '200um'
            ),
            cpw_options = Dict(
                total_length = '4000um',
                left_options = Dict(
                    # lead = Dict(start_straight = '50um'),
                    # meander=Dict(spacing='100um', asymmetry='0um'),
                    # snap='true',
                    # prevent_short_edges='true',
                    fillet = '49.9um',
                ),
                right_options = Dict(
                    meander=Dict(spacing='100um', asymmetry='0um'),
                    # snap='true',
                    # prevent_short_edges='true',
                    fillet = '49.9um',
                )
            )
        ),
        qubit_options = Dict(
            connection_pads=Dict(
                readout = Dict(connector_location = '90', 
                        connector_type = '0',
                    ),
            ),
            claw_cpw_length = '50um',
            orientation = '180',
            pos_y = '1500um'
        )
    )
    
    component_metadata = Dict(short_name='qubitcavity')
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
        self.make_qubit()
        self.make_cavity()
        self.make_pins()
        
    def make_qubit(self):
        p = self.p

        qubit_opts = Dict()
        self.copier(qubit_opts, p.qubit_options)
        self.qubit = TransmonClaw(self.design, "{}_xmon".format(self.name), options = qubit_opts)
        # self.add_qgeometry('poly', self.qubit.qgeometry_dict('poly'), subtract = True, chip = p.chip)

    def make_cavity(self):
        self.make_coupler()
        self.make_cpws()
        # p = self.p

        # cavity_opts = Dict()
        # self.copier(cavity_opts, p.cavity_options)
        # cavity_opts['cpw_options'].update({'pin_inputs':Dict(
        #                                     start_pin = Dict(
        #                                         component = self.qubit.name,
        #                                         pin = 'c'
        #                                     ),
        #                                     end_pin = Dict(
        #                                         component = '',
        #                                         pin = ''
        #                                     )
        #                                     )})
        # self.cavity = CavityFeedline(self.design, "{}_cavityfeedline".format(self.name), options = cavity_opts)
        # self.add_qgeometry('path', self.cavity.qgeometry_dict('path'), layer = 1, chip = p.chip)
        # self.add_qgeometry('poly', self.cavity.qgeometry_dict('poly'), layer = 1, chip = p.chip)


    # def make_pins(self):
    #     p = self.p
    #     start_dict = self.cavity.get_pin('prime_start')
    #     end_dict = self.cavity.get_pin('prime_end')
    #     self.add_pin('prime_start', start_dict['points'], start_dict['width'], chip = p.chip)
    #     self.add_pin('prime_end', end_dict['points'], end_dict['width'], chip = p.chip)

    def make_coupler(self):
        p = self.p

        temp_opts = Dict()
        self.copier(temp_opts, p.cavity_options['coupler_options'])
        # for k in p.coupler_options:
        #     temp_opts.update({k:p.cavity_options.coupler_options[k]})

        if(p.cavity_options['coupling_type'] == "capacitive"):
            from qiskit_metal.qlibrary.couplers.coupled_line_tee import CoupledLineTee
            self.coupler = CoupledLineTee(self.design, "{}_cap_coupler".format(self.name), options=temp_opts)
        elif(p.cavity_options['coupling_type'] == 'inductive'):
            from inductive_coupler import InductiveCoupler
            self.coupler = InductiveCoupler(self.design, "{}_ind_coupler".format(self.name), options=temp_opts)
        elif(p.cavity_options['coupling_type'] == 'interdigitated'):
            from qiskit_metal.qlibrary.couplers.cap_n_interdigital_tee import CapNInterdigitalTee
            self.coupler = CapNInterdigitalTee(self.design, '{}_capn_coupler'.format(self.name), options=temp_opts)
        # self.add_qgeometry('path', self.coupler.qgeometry_dict('path'), chip = p.chip)
        # self.add_qgeometry('poly', self.coupler.qgeometry_dict('poly'), chip = p.chip)

    def make_cpws(self):
        from qiskit_metal.qlibrary.tlines.meandered import RouteMeander

        p = self.p
        p.cpw_options = p.cavity_options['cpw_options']
        
        left_opts = Dict()
        left_opts.update({'total_length': (p.cpw_options.total_length if p.cavity_options['coupling_type'] == 'capacitive' else p.cpw_options.total_length/2) })
        left_opts.update({'pin_inputs':Dict(
                                            start_pin = Dict(
                                                component = '',
                                                pin = ''
                                            ),
                                            end_pin = Dict(
                                                component = '',
                                                pin = ''
                                            )
                                            )})
        left_opts['pin_inputs']['start_pin'].update({'component':self.qubit.name})
        left_opts['pin_inputs']['start_pin'].update({'pin':'readout'})

        left_opts['pin_inputs']['end_pin'].update({'component':self.coupler.name})
        left_opts['pin_inputs']['end_pin'].update({'pin':'second_end'})

        self.copier(left_opts, p.cpw_options.left_options)

        print(left_opts)

        self.LeftMeander = RouteMeander(self.design, "{}_left_cpw".format(self.name), options = left_opts)
        # self.add_qgeometry('path', self.LeftMeander.qgeometry_dict('path'), chip = p.chip)
        # self.add_qgeometry('poly', self.LeftMeander.qgeometry_dict('poly'), chip = p.chip)

        if(p.cavity_options['coupling_type'] == 'inductive'):
            right_opts = Dict()
            right_opts.update({'total_length':p.cpw_options.total_length/2})
            right_opts.update({'pin_inputs':Dict(
                                                start_pin = Dict(
                                                    component = '',
                                                    pin = ''
                                                ),
                                                end_pin = Dict(
                                                    component = '',
                                                    pin = ''
                                                )
                                                )})
            right_opts['pin_inputs']['end_pin'].update({'component':p.cpw_options.pin_inputs.end_pin.component})
            right_opts['pin_inputs']['end_pin'].update({'pin':p.cpw_options.pin_inputs.end_pin.pin})

            right_opts['pin_inputs']['start_pin'].update({'component':self.coupler.name})
            right_opts['pin_inputs']['start_pin'].update({'pin':'second_start'})

            self.copier(right_opts, p.cpw_options.right_options)

            self.RightMeander = RouteMeander(self.design, "{}_right_cpw".format(self.name), options = right_opts)
            self.add_qgeometry('path', self.RightMeander.qgeometry_dict('path'), chip = p.chip)
            # self.add_qgeometry('poly', self.RightMeander.qgeometry_dict('poly'), chip = p.chip)

        
    def make_pins(self):
        start_dict = self.coupler.get_pin('prime_start')
        end_dict = self.coupler.get_pin('prime_end')
        self.add_pin('prime_start', start_dict['points'], start_dict['width'])
        self.add_pin('prime_end', end_dict['points'], end_dict['width'])
