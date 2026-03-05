# from PyQt5.QtWidgets import QLabel, QWidget,QApplication,QVBoxLayout
# from PyQt5 import QtWidgets

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qtabbutton import QTabButton

import res_rc
class QPowerButton(QWidget):
    clicked = pyqtSignal()
    btn_bg_list = ['btn_bg_4.png','btn_bg_4.png','btn_bg_4.png','btn_bg_6.png','btn_bg_6.png','btn_bg_6.png','btn_bg_7.png','btn_bg_7.png','btn_bg_7.png','btn_bg_7.png','btn_bg_7.png','btn_bg_7.png']
    def __init__(self,id:str,parent=None):
        super(QPowerButton, self).__init__(parent)
        self.id = id
        self.initUI()
        
        # self.retranslateUi(QPowerButton)
    def initUI(self):
        # self.
        # -*- coding: utf-8 -*-

        ################################################################################
        ## Form generated from reading UI file 'total2hwbhLB.ui'
        ##
        ## Created by: Qt User Interface Compiler version 5.15.2
        ##
        ## WARNING! All changes made in this file will be lost when recompiling UI file!
        ################################################################################
        self.styles = {
            "open":{
                "name":' color:#6B846B;font-size: 10px;background:rbga(0,0,0,0)',
                "text":"线路通畅",
                "btn": QPixmap(':/imgs/line_open.png'),
                'state': 'font-size:22px;',
                'bg':'background:#E3F6ED;border-radius: 10px;'
            },
            "close":{
                "name":' color:#FF5863;font-size: 10px;background:rbga(0,0,0,0)',
                "text":"线路断开",
                "btn": QPixmap(':/imgs/line_close.png'),
                "state": 'font-size:22px;',
                "bg":'background:#FFE4E6;border-radius: 10px;'
            },
            "off":{
                "name":' color:#A3A3A3;font-size: 10px;background:rbga(0,0,0,0)',
                "text":"线路关闭",
                "btn": QPixmap(':/imgs/line_off.png'),
                "state": 'font-size:22px;',
                "bg":'background:#F7F5F5;border-radius: 10px;'
            }
        }
        self.resize(160,234)
        # self.setStyleSheet(styles)
        self.setObjectName(u"QPowerButton_{}".format(self.id))
        self.setContentsMargins(28, 24,44, 24)
        # print(id(self),self.id)
        self.widget = QWidget(self)  
        self.widget.setObjectName(u"widget_{}".format(self.id))
        self.widget.resize(160,234)
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0,0,0,0)
        self.line_box = QTabButton(self.widget)
        self.line_box.clicked.connect(self.mousePressEvent)
        self.line_box.setObjectName(u"line_box")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_box.sizePolicy().hasHeightForWidth())
        self.line_box.setSizePolicy(sizePolicy)
        self.line_box.setMinimumSize(QSize(150, 194))
        self.line_box.setLayoutDirection(Qt.LeftToRight)
        self.line_box.setStyleSheet(self.styles['off']['bg'])
        self.verticalLayout_20 = QVBoxLayout(self.line_box)
        self.verticalLayout_20.setSpacing(0)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.widget_2 = QWidget(self.line_box)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(0, 224))
        self.widget_2.setMaximumSize(QSize(150, 224))
        self.widget_2.setStyleSheet(self.styles['off']['bg'])
        self.verticalLayout_21 = QVBoxLayout(self.widget_2)
        self.verticalLayout_21.setSpacing(0)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(10, 0, 10, 10)
        self.horizontalWidget_4 = QWidget(self.widget_2)
        self.horizontalWidget_4.setObjectName(u"horizontalWidget_4")
        self.horizontalLayout_29 = QHBoxLayout(self.horizontalWidget_4)
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.horizontalLayout_29.setContentsMargins(1, -1, 1, 8)
        self.line_state = QLabel(self.horizontalWidget_4)
        self.line_state.setObjectName(u"line_state")
        sizePolicy.setHeightForWidth(self.line_state.sizePolicy().hasHeightForWidth())
        self.line_state.setSizePolicy(sizePolicy)
        self.line_state.setStyleSheet(self.styles['off']['name'])
        self.line_state.setText(self.styles['off']['text'])

        self.horizontalLayout_29.addWidget(self.line_state)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_29.addItem(self.horizontalSpacer_10)

        self.line_btn = QLabel(self.horizontalWidget_4)
        self.line_btn.setObjectName(u"line_btn")
        sizePolicy.setHeightForWidth(self.line_btn.sizePolicy().hasHeightForWidth())
        self.line_btn.setSizePolicy(sizePolicy)
        self.line_btn.setMinimumSize(QSize(38, 0))
        self.line_btn.setMaximumSize(QSize(38, 20))
        self.line_btn.setSizeIncrement(QSize(38, 20))
        self.line_btn.setPixmap(self.styles['off']['btn'])
        self.line_btn.setStyleSheet("")
        self.line_btn.setScaledContents(True)

        self.horizontalLayout_29.addWidget(self.line_btn)


        self.verticalLayout_21.addWidget(self.horizontalWidget_4)

        self.horizontalWidget_5 = QWidget(self.widget_2)
        self.horizontalWidget_5.setObjectName(u"horizontalWidget_5")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.horizontalWidget_5.sizePolicy().hasHeightForWidth())
        self.horizontalWidget_5.setSizePolicy(sizePolicy1)
        self.horizontalLayout_30 = QHBoxLayout(self.horizontalWidget_5)
        self.horizontalLayout_30.setSpacing(0)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.horizontalLayout_30.setContentsMargins(0, 0, 0, 0)
        self.line_icon = QLabel(self.horizontalWidget_5)
        self.line_icon.setObjectName(u"line_icon")
        self.line_icon.setMinimumSize(QSize(130, 130))
        self.line_icon.setMaximumSize(QSize(130, 130))
        bg_path = "image:url(:/imgs/{}) no-repeat 100% center; background:rgba(0,0,0,0)".format(self.btn_bg_list[self.id])
        self.line_icon.setStyleSheet(bg_path)
        self.line_icon.setScaledContents(True)
        self.line_icon.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_30.addWidget(self.line_icon)


        self.verticalLayout_21.addWidget(self.horizontalWidget_5)

        self.horizontalWidget_6 = QWidget(self.widget_2)
        self.horizontalWidget_6.setObjectName(u"horizontalWidget_6")
        self.horizontalLayout_31 = QHBoxLayout(self.horizontalWidget_6)
        self.horizontalLayout_31.setSpacing(0)
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.horizontalLayout_31.setContentsMargins(0, 0, 0, 0)
        self.line_name = QLabel(self.horizontalWidget_6)
        self.line_name.setObjectName(u"line_name")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.line_name.sizePolicy().hasHeightForWidth())
        self.line_name.setSizePolicy(sizePolicy2)
        self.line_name.setStyleSheet("")

        self.horizontalLayout_31.addWidget(self.line_name)


        self.verticalLayout_21.addWidget(self.horizontalWidget_6)


        self.verticalLayout_20.addWidget(self.widget_2)


        self.horizontalLayout.addWidget(self.line_box)


        # self.verticalLayout.addWidget(self.widget)

        
        self.retranslateUi(self)
        # self.show()
        QMetaObject.connectSlotsByName(self)
        # return self
    # setupUi

    def retranslateUi(self,row):
        row.setWindowTitle(QCoreApplication.translate("self", u"Form", None))
        self.line_box.setProperty("class", QCoreApplication.translate("self", u"line_box", None))
        # self.line_state.setText(QCoreApplication.translate("self", u"\u7ebf\u8def\u65ad\u5f00", None))
        self.line_btn.setText('')
        self.line_icon.setText("")
        self.line_name.setText(QCoreApplication.translate("self", u"\u7a7a\u8c03 A", None))
    # retranslateUi

    def changeStyles(self,state:str):
        # print('changeStyles-state',state)
        if state in ['open','close','off']:
            style_obj = self.styles[state]
            self.line_box.setStyleSheet(style_obj['bg'])
            self.line_btn.setPixmap(style_obj['btn'])
            self.line_state.setText(style_obj['text'])
            self.line_state.setStyleSheet(style_obj['name'])
            self.widget_2.setStyleSheet(style_obj['bg'])
            self.line_btn.setStyleSheet("")
            self.line_name.setStyleSheet('')

        pass
        
    def mousePressEvent(self,event=None):
        # print(22,self.id)
        self.clicked.emit()

    
# if __name__ == '__main__':
#     import sys
#     app = QApplication(sys.argv)
#     ex = QPowerButton(id='1')
#     sys.exit(app.exec_())