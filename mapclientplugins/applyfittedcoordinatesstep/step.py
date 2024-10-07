
"""
MAP Client Plugin Step
"""
import json
import os

from PySide6 import QtGui
from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.utils.zinc.mesh import undefine_field
from cmlibs.zinc.context import Context

from mapclient.mountpoints.workflowstep import WorkflowStepMountPoint
from mapclientplugins.applyfittedcoordinatesstep.configuredialog import ConfigureDialog


class ApplyFittedCoordinatesStep(WorkflowStepMountPoint):
    """
    Skeleton step which is intended to be a helpful starting point
    for new steps.
    """

    def __init__(self, location):
        super(ApplyFittedCoordinatesStep, self).__init__('Apply Fitted Coordinates', location)
        self._configured = False  # A step cannot be executed until it has been configured.
        self._category = 'Fitting'
        # Add any other initialisation code here:
        self._icon = QtGui.QImage(':/applyfittedcoordinatesstep/images/fitting.png')
        # Ports:
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#uses',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location'))
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#uses',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location'))
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#provides',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location'))
        # Port data:
        self._portData0 = None  # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location
        self._portData1 = None  # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location

        # Config:
        self._config = {
            'identifier': '',
        }

        self._context = None

    def execute(self):
        """
        Add your code here that will kick off the execution of the step.
        Make sure you call the _doneExecution() method when finished.  This method
        may be connected up to a button in a widget for example.
        """
        # Put your execute step code here before calling the '_doneExecution' method.
        self._prepare_local_output_directory()
        self._create_merged_mesh()
        self._write_output()
        self._doneExecution()

    def _output_exf_file(self):
        return os.path.join(self._local_output_directory(), "merged_mesh.exf")

    def _write_output(self):
        region = self._context.getDefaultRegion()
        region.writeFile(self._output_exf_file())

    def _create_merged_mesh(self):
        self._context = Context("merge")
        region = self._context.getDefaultRegion()
        region.readFile(self._portData0)
        region.readFile(self._portData1)

        fm = region.getFieldmodule()
        with ChangeManager(fm):
            coordinate_field = fm.findFieldByName("coordinates").castFiniteElement()
            coordinate_field.setName("original coordinates")
            undefine_field(coordinate_field)
            coordinate_field.setManaged(False)

        fitted_coordinate_field = fm.findFieldByName("fitted coordinates")
        fitted_coordinate_field.setName("coordinates")

    def _local_output_directory(self):
        return os.path.join(self._location, self._config["identifier"] + "_output")

    def _prepare_local_output_directory(self):
        output_directory = self._local_output_directory()
        if not os.path.isdir(output_directory):
            os.mkdir(output_directory)

    def setPortData(self, index, dataIn):
        """
        Add your code here that will set the appropriate objects for this step.
        The index is the index of the port in the port list.  If there is only one
        uses port for this step then the index can be ignored.

        :param index: Index of the port to return.
        :param dataIn: The data to set for the port at the given index.
        """
        if index == 0:
            self._portData0 = dataIn  # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location
        elif index == 1:
            self._portData1 = dataIn  # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location

    def getPortData(self, index):
        """
        Add your code here that will return the appropriate objects for this step.
        The index is the index of the port in the port list.  If there is only one
        provides port for this step then the index can be ignored.

        :param index: Index of the port to return.
        """
        return self._output_exf_file()  # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location

    def configure(self):
        """
        This function will be called when the configure icon on the step is
        clicked.  It is appropriate to display a configuration dialog at this
        time.  If the conditions for the configuration of this step are complete
        then set:
            self._configured = True
        """
        dlg = ConfigureDialog(self._main_window)
        dlg.identifierOccursCount = self._identifierOccursCount
        dlg.setConfig(self._config)
        dlg.validate()
        dlg.setModal(True)

        if dlg.exec_():
            self._config = dlg.getConfig()

        self._configured = dlg.validate()
        self._configuredObserver()

    def getIdentifier(self):
        """
        The identifier is a string that must be unique within a workflow.
        """
        return self._config['identifier']

    def setIdentifier(self, identifier):
        """
        The framework will set the identifier for this step when it is loaded.
        """
        self._config['identifier'] = identifier

    def serialize(self):
        """
        Add code to serialize this step to string.  This method should
        implement the opposite of 'deserialize'.
        """
        return json.dumps(self._config, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def deserialize(self, string):
        """
        Add code to deserialize this step from string.  This method should
        implement the opposite of 'serialize'.

        :param string: JSON representation of the configuration in a string.
        """
        self._config.update(json.loads(string))

        d = ConfigureDialog()
        d.identifierOccursCount = self._identifierOccursCount
        d.setConfig(self._config)
        self._configured = d.validate()
