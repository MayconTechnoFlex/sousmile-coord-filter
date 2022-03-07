from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from typing import List


def qt_create_table(widget: QTableWidget,
                    num_col: int,
                    num_row: int,
                    custom_header_list: List[str],
                    hor_header: bool = False,
                    ver_header: bool = True,
                    custom_header: bool = False):
    """
    Function to create a table

    :param widget: QTableWidget used on the program
    :param num_col: Number of column that you want on the table
    :param num_row: Number of rows that you want on the table
    :param hor_header: Visibility on the horizontal header
    :param ver_header: Visibility of the vertical header
    :param custom_header: If you want a custom header on the row number 0
    :param custom_header_list: The list of strings you want on the custom header
    :return:
    """

    ##################################################
    # Create a table
    ##################################################
    widget.setColumnCount(num_col)
    widget.setRowCount(num_row)
    widget.horizontalHeader().setVisible(hor_header)
    widget.verticalHeader().setVisible(ver_header)
    ##################################################

    if custom_header:
        for i in range(len(custom_header_list)):
            widget.setItem(0, i, QTableWidgetItem(custom_header_list[i]))
