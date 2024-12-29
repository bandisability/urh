"""
Optimized Implementation of TestProjectManager
Enhancements include improved modularity, readability, and resource utilization.
"""

import os
import random
import tempfile
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest

from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.Participant import Participant
from urh.controller.dialogs.ProjectDialog import ProjectDialog
from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh import settings


class OptimizedProjectManagerTest(QtTestCase):
    """
    Optimized test suite for ProjectManager functionalities.
    """

    def setUp(self):
        """
        Setup test environment.
        """
        super().setUp()
        project_file = get_path_for_data_file("URHProject.xml")
        if os.path.isfile(project_file):
            os.remove(project_file)

        self.form.project_manager.set_project_folder(
            get_path_for_data_file(""), ask_for_new_project=False
        )
        self.generator_frame = self.form.generator_tab_controller

    def test_load_protocol_file(self):
        """
        Test loading a protocol file.
        """
        self.form.add_protocol_file(self.get_path_for_filename("protocol_wsp.proto.xml"))
        self.assertEqual(
            len(self.form.compare_frame_controller.proto_analyzer.messages), 6
        )

    def test_save_and_load_modulators(self):
        """
        Test saving and loading modulators in a project.
        """
        self.generator_frame.modulators = [
            self._create_modulator("Mod1", amplitude=0.8, freq_hz=1337, phase_deg=90),
            self._create_modulator("Mod2", amplitude=0.6, freq_hz=500, phase_deg=45),
        ]

        self.form.save_project()
        loaded_mods = self.form.project_manager.read_modulators_from_project_file()
        self.assertEqual(len(loaded_mods), len(self.generator_frame.modulators))

        for mod, loaded_mod in zip(self.generator_frame.modulators, loaded_mods):
            self.assertEqual(mod.name, loaded_mod.name)
            self.assertEqual(mod.carrier_amplitude, loaded_mod.carrier_amplitude)
            self.assertEqual(mod.carrier_freq_hz, loaded_mod.carrier_freq_hz)
            self.assertEqual(mod.carrier_phase_deg, loaded_mod.carrier_phase_deg)

    def _create_modulator(self, name, amplitude, freq_hz, phase_deg):
        """
        Utility to create a modulator instance.
        """
        modulator = Modulator(name)
        modulator.carrier_amplitude = amplitude
        modulator.carrier_freq_hz = freq_hz
        modulator.carrier_phase_deg = phase_deg
        return modulator

    def test_close_project(self):
        """
        Test closing and reopening a project.
        """
        self.form.close_project()
        self.assertEqual(self.form.signal_tab_controller.num_frames, 0)

        self.add_signal_to_form("ask.complex")
        self.add_signal_to_form("fsk.complex")
        self.assertEqual(self.form.signal_tab_controller.num_frames, 2)

        self.form.close_project()
        self.assertEqual(self.form.signal_tab_controller.num_frames, 0)
        self.assertIsNone(self.form.project_manager.project_file)

    def test_save_and_load_participants(self):
        """
        Test saving and loading participants in a project.
        """
        temp_dir = self._create_temp_directory("participant_test")
        participants = [Participant("Alice", "A"), Participant("Bob", "B")]
        self.form.project_manager.set_project_folder(temp_dir, ask_for_new_project=False)
        self.form.project_manager.participants = participants

        self.add_signal_to_form("esaver.complex16s")
        self.add_signal_to_form("two_participants.complex16s")
        self.form.save_project()
        self.form.close_project()

        self.form.project_manager.set_project_folder(temp_dir, ask_for_new_project=False)
        self.assertEqual(len(self.form.project_manager.participants), len(participants))

    def _create_temp_directory(self, dir_name):
        """
        Create a temporary directory for testing.
        """
        temp_dir = os.path.join(tempfile.gettempdir(), "urh", dir_name)
        os.makedirs(temp_dir, exist_ok=True)
        project_file = os.path.join(temp_dir, settings.PROJECT_FILE)
        if os.path.isfile(project_file):
            os.remove(project_file)
        return temp_dir

    def test_save_and_load_with_field_types(self):
        """
        Test saving and loading field types in a project.
        """
        temp_dir = self._create_temp_directory("field_type_test")
        self.form.project_manager.set_project_folder(temp_dir, ask_for_new_project=False)

        self.add_signal_to_form("esaver.complex16s")
        field_types = self._assign_field_types_to_protocol()

        self.form.save_project()
        self.form.close_project()

        self.form.project_manager.set_project_folder(temp_dir, ask_for_new_project=False)
        loaded_field_types = [
            message.field_type for message in self.form.compare_frame_controller.active_message_type
        ]

        self.assertEqual(field_types, loaded_field_types)

    def _assign_field_types_to_protocol(self):
        """
        Assign predefined field types to a protocol.
        """
        preamble_field_type = self._get_field_type(FieldType.Function.PREAMBLE)
        sync_field_type = self._get_field_type(FieldType.Function.SYNC)
        checksum_field_type = self._get_field_type(FieldType.Function.CHECKSUM)

        self._add_protocol_label(0, 9, preamble_field_type.caption)
        self._add_protocol_label(10, 13, sync_field_type.caption)
        self._add_protocol_label(14, 16, checksum_field_type.caption)

        return [preamble_field_type, sync_field_type, checksum_field_type]

    def _get_field_type(self, function):
        """
        Get a field type by its function.
        """
        return next(
            ft
            for ft in self.form.compare_frame_controller.field_types
            if ft.function == function
        )

    def _add_protocol_label(self, start, end, label_name):
        """
        Add a protocol label to the protocol view.
        """
        self.form.compare_frame_controller.add_protocol_label(start, end, 0, 1, False)
        model = self.form.compare_frame_controller.ui.tblLabelValues.model()
        index = model.rowCount() - 1
        model.setData(model.createIndex(index, 0), label_name, role=Qt.EditRole)

    def test_project_dialog(self):
        """
        Test project dialog functionalities.
        """
        dialog = ProjectDialog(self.form.project_manager, self.form)

        frequency = 1e9
        dialog.ui.spinBoxFreq.setValue(frequency)
        self.assertEqual(dialog.freq, frequency)

        sample_rate = 10e9
        dialog.ui.spinBoxSampleRate.setValue(sample_rate)
        self.assertEqual(dialog.sample_rate, sample_rate)

        self.assertTrue(dialog.ui.btnAddParticipant.isEnabled())
        dialog.ui.btnAddParticipant.click()
        self.assertGreater(len(dialog.participants), 0)

        test_path = os.path.join(QDir.tempPath(), "test_project")
        dialog.ui.lineEdit_Path.setText(test_path)
        dialog.ui.lineEdit_Path.textEdited.emit(test_path)
        self.assertEqual(dialog.path, test_path)

        dialog.on_button_box_accepted()
        self.assertTrue(os.path.isdir(test_path))

        dialog = ProjectDialog(
            self.form.project_manager, self.form, new_project=False
        )
        self.assertEqual(dialog.ui.spinBoxFreq.value(), frequency)

if __name__ == "__main__":
    QApplication([])
    unittest.main()

