
"""
MAP Client Plugin - Generated from MAP Client v0.21.4
"""

__version__ = '0.1.0'
__author__ = 'Auckland Bioengineering Institute'
__stepname__ = 'Apply Fitted Coordinates'
__location__ = 'https://github.com/mapclient-plugins/mapclientplugins.applyfittedcoordinatesstep'

# import class that derives itself from the step mountpoint.
from mapclientplugins.applyfittedcoordinatesstep import step

# Import the resource file when the module is loaded,
# this enables the framework to use the step icon.
from . import resources_rc