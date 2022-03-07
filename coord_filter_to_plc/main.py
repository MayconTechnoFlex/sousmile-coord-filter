########################################
# imports
########################################
import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTableWidget , QTableWidgetItem, QGraphicsScene
from PyQt5.QtCore import QThreadPool, QThread, QRectF, Qt
from PyQt5.QtGui import QIcon, QPen
from ui_py.gui import Ui_MainWindow

from utils.data.plc import data_to_plc
from utils.data.comm_plc import read_tags
from utils.workers import *
from utils.qt_utils import qt_create_table
from test.test import test_file

########################################


class CoordFilter(QMainWindow):
    def __init__(self):
        super(CoordFilter, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.stackedWidget.setCurrentWidget(self.ui.main_screen)
        self.ui.lbl_screen_title.setText("Home")
        self.setWindowTitle("Coord Filter RN")

        #######################################
        # Thread
        #######################################
        self.mythread_plc = QThreadPool()
        self.mythread_test = QThreadPool()

        self.myworker_plc = Worker_PLC()
        self.myworker_test = Worker_Test()

        self.myworker_plc.signal_worker.result.connect(self.plc_routine)
        self.myworker_plc.signal_worker.error.connect(self.runnable_error_plc)  # signal when we have a plc comm error
        #####################################################################
        # Button call function to start test of filter positoins with a file
        #####################################################################
        self.myworker_test.signal_worker_test.result.connect(self.start_test)
        self.myworker_test.signal_worker_test.error.connect(self.runnable_error_test)  # signal when we have a plc comm error

        self.mythread_plc.start(self.myworker_plc)
        self.mythread_test.start(self.myworker_test)

        ######################################

        self.ui.rb_cloud_file.setChecked(True)
        self.ui.ico_cloud.setEnabled(True)
        self.ui.btn_search_file.setEnabled(False)
        self.ui.le_file_path.setEnabled(False)

        self.ui.rb_plc.setChecked(True)
        self.ui.btn_search_file_for_test.setEnabled(False)
        self.ui.le_file_for_test.setEnabled(False)
        self.ui.btn_test_file.setEnabled(False)

        self.ui.rb_cloud_file.toggled.connect(self.set_cloud_file)
        self.ui.rb_local_file.toggled.connect(self.set_local_file)

        self.ui.rb_plc.toggled.connect(self.set_file_to_plc)
        self.ui.rb_test.toggled.connect(self.set_file_to_test)

        self.ui.btn_search_file.clicked.connect(self.search_folder)

        self.ui.btn_search_file_for_test.clicked.connect(self.search_file_for_test)
        self.ui.btn_test_file.clicked.connect(self.test_routine)

        self.ui.btn_goto_home_sreen.clicked.connect(self.show_home)
        self.ui.btn_goto_config_screen.clicked.connect(self.show_config)
        ##################################
        # Variables used to test a file
        ##################################
        self.test_signal: bool = False
        self.list_pos_x: List[float] = []
        self.list_pos_y: List[float] = []
        self.list_pos_z: List[float] = []
        self.list_pos_c: List[float] = []
        self.list_pos_d: List[float] = []
        self.list_pos: List[int] = []
        self.list_pos_info: List[str] = []
        ###################################
    
    def show_config(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.config_screen)
        self.ui.lbl_screen_title.setText("Configurações")


    def show_home(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.main_screen)
        self.ui.lbl_screen_title.setText("Home")


    def set_cloud_file(self):
        self.ui.ico_cloud.setEnabled(True)
        self.ui.btn_search_file.setEnabled(False)
        self.ui.le_file_path.setEnabled(False)


    def set_local_file(self):
        self.ui.ico_cloud.setEnabled(False)
        self.ui.btn_search_file.setEnabled(True)
        self.ui.le_file_path.setEnabled(True)


    def set_file_to_plc(self):
        self.ui.btn_search_file_for_test.setEnabled(False)
        self.ui.le_file_for_test.setEnabled(False)
        self.ui.btn_test_file.setEnabled(False)


    def set_file_to_test(self):
        self.ui.btn_search_file_for_test.setEnabled(True)
        self.ui.le_file_for_test.setEnabled(True)
        self.ui.btn_test_file.setEnabled(True)

    def start_test(self):
        self.test_signal = True


    def search_folder(self):
        path_name = QFileDialog.getExistingDirectory(self, "Selecione um arquivo", os.getcwd())
        self.ui.le_file_path.setText(path_name)


    def search_file_for_test(self):
        path_file_name = QFileDialog.getOpenFileName(self, "Selecione um arquivo", os.getcwd(), "*.csv")
        self.ui.le_file_for_test.setText(path_file_name[0])


    def plc_routine(self, configpontos, data_ctrl_a1, data_ctrl_a2, data_ctrl_b1, data_ctrl_b2):
        print('- Comunicação de dados utilizando Python com CLP Rockwell')
        while True:
            if self.ui.rb_plc.isChecked():
                print("Coletando do CLP")
                ##############################################
                # Wait trigger A1
                ##############################################
                try:
                    if data_ctrl_a1['Trigger']:
                        data_to_plc('DataCtrl_A1',
                                    'CutDepthA1',
                                    'HMI.EnableLog',
                                    'HMI.NumPosMax',
                                    'ConfigPontos.DistVar',
                                    self.ui.rb_cloud_file.isEnabled(),
                                    self.ui.rb_local_file.isEnabled(),
                                    self.ui.le_file_path.text())
                except Exception as e:
                    print(f'{e} - trying to read DataCtrl_A1')
                ##############################################
                # Wait trigger A2
                ##############################################
                try:
                    if data_ctrl_a2['Trigger']:
                        data_to_plc('DataCtrl_A2',
                                    'CutDepthA2',
                                    'HMI.EnableLog',
                                    'HMI.NumPosMax',
                                    'ConfigPontos.DistVar',
                                    self.ui.rb_cloud_file.isEnabled(),
                                    self.ui.rb_local_file.isEnabled(),
                                    self.ui.le_file_path.text())
                except Exception as e:
                    print(f'{e} - trying to read DataCtrl_A2')
                ##############################################
                # Wait trigger B1
                ##############################################
                try:
                    if data_ctrl_b1['Trigger']:
                        data_to_plc('DataCtrl_B1',
                                    'CutDepthB1',
                                    'HMI.EnableLog',
                                    'HMI.NumPosMax',
                                    'ConfigPontos.DistVar',
                                    self.ui.rb_cloud_file.isEnabled(),
                                    self.ui.rb_local_file.isEnabled(),
                                    self.ui.le_file_path.text())
                except Exception as e:
                    print(f'{e} - trying to read DataCtrl_B1')
                ##############################################
                # Wait trigger B2
                ##############################################
                try:
                    if data_ctrl_b2['Trigger']:
                        data_to_plc('DataCtrl_B2',
                                    'CutDepthB2',
                                    'HMI.EnableLog',
                                    'HMI.NumPosMax',
                                    'ConfigPontos.DistVar',
                                    self.ui.rb_cloud_file.isEnabled(),
                                    self.ui.rb_local_file.isEnabled(),
                                    self.ui.le_file_path.text())
                except Exception as e:
                    print(f'{e} - trying to read DataCtrl_B2')


    def test_routine(self, signal):

        file_path: str = ''

        if self.ui.rb_test.isChecked() and len(self.ui.le_file_for_test.text()) > 0 and self.test_signal:
            #######################################
            # Limpa a tabela de posições
            #######################################
            self.ui.tbl_positions.clear()
            #######################################
            # Disable test button on the gui
            #######################################
            self.ui.btn_test_file.setEnabled(False)
            #############################################
            # Set file path from the line edit on the gui
            #############################################
            file_path = self.ui.le_file_for_test.text()
            ###############################################
            print("Inicio da execução do teste de filtros")
            ###############################################
            test_file(file_path, self.list_pos_x, self.list_pos_y, self.list_pos_z, self.list_pos_c, self.list_pos_d,
                      self.list_pos, self.list_pos_info, var_limit_d=25.0, var_limit_c=5.0, var_limit_xyz=1.5,
                      var_limit_h=0.04, var_p=0.5)
            #######################################
            custom_header_list = ["Posições", "X", "Y", "Z", "C", "D", "Info"]
            qt_create_table(self.ui.tbl_positions,
                            7,
                            len(self.list_pos),
                            custom_header_list,
                            hor_header=False,
                            ver_header=True,
                            custom_header=True)
            #######################################
            # Create grafic
            #######################################
            # Defining a scene rect of 400x200, with it's origin at 0,0.
            # If we don't set this on creation, we can set it later with .setSceneRect
            scene = QGraphicsScene(-70, -41, 140, 82)




            #######################################
            for i in range(len(self.list_pos)):
                if i > 0:
                    self.ui.tbl_positions.setItem(i, 0, QTableWidgetItem(str(self.list_pos[i])))  #.setText(str(self.list_pos[i])))
                    self.ui.tbl_positions.setItem(i, 1, QTableWidgetItem(str(self.list_pos_x[i])))  #.setText(str(self.list_pos_x[i])))
                    self.ui.tbl_positions.setItem(i, 2, QTableWidgetItem(str(self.list_pos_y[i])))  #.setText(str(self.list_pos_y[i])))
                    self.ui.tbl_positions.setItem(i, 3, QTableWidgetItem(str(self.list_pos_z[i])))  #.setText(str(self.list_pos_z[i])))
                    self.ui.tbl_positions.setItem(i, 4, QTableWidgetItem(str(self.list_pos_c[i])))  #.setText(str(self.list_pos_c[i])))
                    self.ui.tbl_positions.setItem(i, 5, QTableWidgetItem(str(self.list_pos_d[i])))  #.setText(str(self.list_pos_d[i])))
                    self.ui.tbl_positions.setItem(i, 6, QTableWidgetItem(str(self.list_pos_info[i])))  #.setText(str(self.list_pos_info[i])))
                    self.ui.tbl_positions.resizeColumnsToContents()

                    scene.addEllipse(QRectF(self.list_pos_x[i], self.list_pos_y[i], 0.2, 0.2), QPen(Qt.blue))

            self.ui.graphicsView.setScene(scene)
            self.ui.graphicsView.scale(3, 3)
            self.ui.graphicsView.show()

            #######################################
            # Enable test button on the gui
            #######################################
            self.ui.btn_test_file.setEnabled(True)
            #######################################
            # Set the test signal to False
            #######################################
            self.test_signal = False
            #######################################

        elif len(self.ui.le_file_for_test.text()) <= 0:
            print("Selecione um arquivo")
            #######################################
            # Set the test signal to False
            #######################################
            self.test_signal = False
            #######################################


    def runnable_error_plc(self):
        if self.ui.rb_plc.isChecked():
            print("Erro no worker de envio de dados para o CLP")


    def runnable_error_test(self):
        if self.ui.rb_teste.isChecked():
            print("Erro no worker para o teste de arquivo local")


    def stop_threads(self):
        print("Finalizando Threads")
        try:
            self.myworker_plc.stop()
        except Exception as e:
            print(f"{e} -> main.py - stop_threads")
        print("Threads finalizadas")




if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = CoordFilter()
    main_win.setFixedHeight(600)
    main_win.setFixedWidth(1176)
    main_win.show()
    main_win.setWindowIcon(QIcon("assets/rn.ico"))
    app.aboutToQuit.connect(main_win.stop_threads)
    sys.exit(app.exec_())





