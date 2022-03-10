import time, traceback, sys
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from pycomm3.exceptions import CommError
from utils.data.comm_plc import read_tags, read_multiple


sleep_time = 0.8
stop_time = 0.2


class WorkerParent:
    """Class for shared functions of the workers"""
    def __init__(self):
        self.running = True

    def stop(self):
        """Stops thread"""
        self.running = False
        time.sleep(stop_time)


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:

    error
        tuple (exctype, value, traceback.format_exc() )
    result
        object data returned from processing, anything
    """
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    result_multiples = pyqtSignal(object, object, object, object, object, object)


class Worker_PLC(QRunnable, WorkerParent):
    """
    Worker thread for multiple signals
    """

    def __init__(self, *args):
        super(Worker_PLC, self).__init__()
        self.running = True
        self.signal_worker = WorkerSignals()

    @pyqtSlot()
    def run(self):
        while self.running:
            try:
                tag_list = ['ConfigPontos', 'DataCtrl_A1', 'DataCtrl_A2', 'DataCtrl_B1', 'DataCtrl_B2', 'HMI']

                tags = read_multiple(tag_list)
                config_pontos = tags[0][1]
                data_ctrl_a1 = tags[1][1]
                data_ctrl_a2 = tags[2][1]
                data_ctrl_b1 = tags[3][1]
                data_ctrl_b2 = tags[4][1]
                HMI = tags[5][1]

                if type(config_pontos) == CommError\
                    or type(data_ctrl_a1) == CommError\
                    or type(data_ctrl_a2) == CommError\
                    or type(data_ctrl_b1) == CommError\
                    or type(data_ctrl_b2) == CommError:
                    traceback.print_exc()
                    exctype, value = sys.exc_info()[:2]
                    self.signal_worker.error.emit((exctype, value, traceback.format_exc()))
                    raise Exception("connection failed")
                else:
                    self.signal_worker.result_multiples.emit(config_pontos,
                                                             data_ctrl_a1,
                                                             data_ctrl_a2,
                                                             data_ctrl_b1,
                                                             data_ctrl_b2,
                                                             HMI)
            except Exception as e:
                print(f'{e} Worker - workers.py')
                time.sleep(3)
            time.sleep(sleep_time)


class Worker_Test(QRunnable, WorkerParent):
    """
    Worker thread for multiple signals
    """

    def __init__(self, *args):
        super(Worker_Test, self).__init__()
        self.running = True
        self.signal_worker_test = WorkerSignals()

    @pyqtSlot()
    def run(self):
        while self.running:
            self.signal_worker_test.result.emit(True)
            time.sleep(sleep_time)