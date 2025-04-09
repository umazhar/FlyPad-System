#pragma once
#include <QtWidgets/QMainWindow>
#include "ui_QtGuiApplication4.h"
#include <QtWidgets>
#include <QtCharts/QChartView>
#include <QtCharts/QLineSeries>
#include <QtCharts/QVXYModelMapper>

class QtGuiApplication4 : public QMainWindow
{
	Q_OBJECT

public:
	QtGuiApplication4(QWidget *parent = Q_NULLPTR);
	QPushButton *stopButton;
	QPushButton *saveLocation;
	QFile *saveFile;
	public slots:
		void quitSlot();
		void saveToFile();
private:
	Ui::QtGuiApplication4Class ui;
};
