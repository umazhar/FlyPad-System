/********************************************************************************
** Form generated from reading UI file 'QtGuiApplication4.ui'
**
** Created by: Qt User Interface Compiler version 5.8.0
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_QTGUIAPPLICATION4_H
#define UI_QTGUIAPPLICATION4_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QToolBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_QtGuiApplication4Class
{
public:
    QMenuBar *menuBar;
    QToolBar *mainToolBar;
    QWidget *centralWidget;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *QtGuiApplication4Class)
    {
        if (QtGuiApplication4Class->objectName().isEmpty())
            QtGuiApplication4Class->setObjectName(QStringLiteral("QtGuiApplication4Class"));
        QtGuiApplication4Class->resize(600, 400);
        menuBar = new QMenuBar(QtGuiApplication4Class);
        menuBar->setObjectName(QStringLiteral("menuBar"));
        QtGuiApplication4Class->setMenuBar(menuBar);
        mainToolBar = new QToolBar(QtGuiApplication4Class);
        mainToolBar->setObjectName(QStringLiteral("mainToolBar"));
        QtGuiApplication4Class->addToolBar(mainToolBar);
        centralWidget = new QWidget(QtGuiApplication4Class);
        centralWidget->setObjectName(QStringLiteral("centralWidget"));
        QtGuiApplication4Class->setCentralWidget(centralWidget);
        statusBar = new QStatusBar(QtGuiApplication4Class);
        statusBar->setObjectName(QStringLiteral("statusBar"));
        QtGuiApplication4Class->setStatusBar(statusBar);

        retranslateUi(QtGuiApplication4Class);

        QMetaObject::connectSlotsByName(QtGuiApplication4Class);
    } // setupUi

    void retranslateUi(QMainWindow *QtGuiApplication4Class)
    {
        QtGuiApplication4Class->setWindowTitle(QApplication::translate("QtGuiApplication4Class", "QtGuiApplication4", Q_NULLPTR));
    } // retranslateUi

};

namespace Ui {
    class QtGuiApplication4Class: public Ui_QtGuiApplication4Class {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_QTGUIAPPLICATION4_H
