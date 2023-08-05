from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np

class InductiveCoupler(QComponent):
    """Generates a four pin (+) structure comprised of a primary two pin CPW
    transmission line, and a secondary two pin neighboring CPW transmission
    line that is inductively coupled to the primary. Such a structure
    can be used, as an example, for generating CPW resonator hangars
    off of a transmission line.

    Inherits QComponent class.

    ::

        +-------------------------+
            -------------------
            |                 |
            |                 |
            |                 |
            |                 |
            +                 +
    """
    default_options = dict(prime_width='10um',
                            prime_gap='6um',
                            second_width='10um',
                            second_gap='6um',
                            coupling_space='3um',
                            coupling_length='100um',
                            down_length='100um',
                            fillet='25um',
                            mirror=False,
                            # open_termination=True
    )

    def make(self):
        """Build the component."""
        p = self.p

        prime_cpw_length = p.coupling_length * 2
        second_flip = 1
        if p.mirror:
            second_flip = -1

        #Primary CPW
        prime_cpw = draw.LineString([[-prime_cpw_length / 2, 0],
                                     [prime_cpw_length / 2, 0]])

        #Secondary CPW
        second_down_length = p.down_length
        second_y = -p.prime_width / 2 - p.prime_gap - p.coupling_space - p.second_gap - p.second_width / 2
        second_cpw = draw.LineString(
            [[
                 second_flip * (-p.coupling_length / 2),
                 second_y - second_down_length
             ],
             [second_flip * (-p.coupling_length / 2), second_y],
             [second_flip * (p.coupling_length / 2), second_y],
             [
                 second_flip * (p.coupling_length / 2),
                 second_y - second_down_length
             ]])

        # second_termination = 0
        # if p.open_termination:
        #     second_termination = p.second_gap

        # second_cpw_etch = draw.LineString(
        #     [[
        #         second_flip * (-p.coupling_length / 2 - second_termination),
        #         second_y
        #     ], [second_flip * (p.coupling_length / 2), second_y],
        #      [
        #          second_flip * (p.coupling_length / 2),
        #          second_y - second_down_length
        #      ]])

        #Rotate and Translate
        c_items = [prime_cpw, second_cpw]
        c_items = draw.rotate(c_items, p.orientation, origin=(0, 0))
        c_items = draw.translate(c_items, p.pos_x, p.pos_y)
        [prime_cpw, second_cpw] = c_items

        #Add to qgeometry tables
        self.add_qgeometry('path', {'prime_cpw': prime_cpw},
                           width=p.prime_width)
        self.add_qgeometry('path', {'prime_cpw_sub': prime_cpw},
                           width=p.prime_width + 2 * p.prime_gap,
                           subtract=True)
        self.add_qgeometry('path', {'second_cpw': second_cpw},
                           width=p.second_width,
                           fillet=p.fillet)
        self.add_qgeometry('path', {'second_cpw_sub': second_cpw},
                           width=p.second_width + 2 * p.second_gap,
                           subtract=True,
                           fillet=p.fillet)

        #Add pins
        prime_pin_list = prime_cpw.coords
        second_pin_list = second_cpw.coords

        self.add_pin('prime_start',
                     points=np.array(prime_pin_list[::-1]),
                     width=p.prime_width,
                     input_as_norm=True)
        self.add_pin('prime_end',
                     points=np.array(prime_pin_list),
                     width=p.prime_width,
                     input_as_norm=True)
        self.add_pin('second_start',
                     points=np.array(second_pin_list[-3::-1]),
                     width=p.second_width,
                     input_as_norm=True)
        self.add_pin('second_end',
                     points=np.array(second_pin_list[2:]),
                     width=p.second_width,
                     input_as_norm=True)
    