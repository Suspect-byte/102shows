"""
Color Cycle Template
(c) 2015 Martin Erzberger, modified 2016 by Simon Leiner

This class is the basis of all color cycles, such as rainbow or theater chase.
A specific color cycle must subclass this template, and implement at least the
'update' method.
"""

import time
import logging as log
from lightshows.templates.base import *
from lightshows.utilities import verifyparameters as verify


class ColorCycle(Lightshow):
    def init_parameters(self):
        self.pause_sec = None
        self.num_steps_per_cycle = None
        self.num_cycles = None
        self.order = 'rgb'  # this should not be changed!

    def set_parameter(self, param_name: str, value):
        if param_name == "pause_sec":
            verify.not_negative_numeric(value, param_name)
            self.pause_sec = value
        elif param_name == "num_steps_per_cycle":
            verify.positive_integer(value, param_name)
            self.num_steps_per_cycle = value
        elif param_name == "num_cycles":
            verify.positive_integer(value, param_name)
            self.num_cycles = value
        else:
            raise InvalidParameters.unknown(param_name)

    def check_runnable(self):
        if not self.pause_sec:
            raise InvalidParameters("Missing parameter \"pause_sec\"!")
        if not self.num_steps_per_cycle:
            raise InvalidParameters("Missing parameter \"num_steps_per_cycle\"!")
        if not self.num_cycles:
            raise InvalidParameters("Missing parameter \"num_cycles\"!")

    """
    void init()
    This method is called to initialize a color program.
    """

    @abstractmethod
    def init(self):
        # The default does nothing. A particular subclass could setup variables, or
        # even light the strip in an initial color.
        pass

    """
    void shutdown()
    This method is called at the end, when the light program should terminate
    """

    def shutdown(self, strip):
        # The default does nothing
        log.debug('Shutdown not implemented')

    """
    void update()
    This method paints one subcycle. It must be implemented
    currentStep: This goes from zero to numStepsPerCycle-1, and then back to zero. It is up to the subclass to define
                 what is done in one cycle. One cycle could be one pass through the rainbow. Or it could
                 be one pixel wandering through the entire strip (so for this case, the numStepsPerCycle should be
                 equal to numLEDs).
    currentCycle: Starts with zero, and goes up by one whenever a full cycle has completed.
    """

    @abstractmethod
    def update(self, current_step: int, current_cycle: int):
        raise NotImplementedError("Please implement the update() method")

    def cleanup(self):
        self.shutdown(self.strip)
        self.strip.clearStrip()
        log.debug('Strip cleared')
        self.strip.cleanup()
        log.debug('SPI closed')

    """
    Start the actual work
    """

    def run(self):
        try:
            self.init(self.strip)  # Call the subclasses init method
            self.strip.show()
            currentCycle = 0
            while True:  # Loop forever (no 'for' here due to the possibility of infinite loops)
                for currentStep in range(self.num_steps_per_cycle):
                    needRepaint = self.update(currentStep, currentCycle)  # Call the subclasses update method
                    if needRepaint:
                        self.strip.show()  # Display, only if required
                    time.sleep(self.pause_sec)  # Pause until the next step
                currentCycle += 1
                if self.num_cycles != -1 and currentCycle >= self.num_cycles:
                    break
            # Finished, cleanup everything
            self.cleanup()

        except KeyboardInterrupt:  # Ctrl-C can halt the light program
            log.debug('Interrupted...')
            self.cleanup()