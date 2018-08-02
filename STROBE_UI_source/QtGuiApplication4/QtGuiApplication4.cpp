#include "QtGuiApplication4.h"
#include <QtWidgets>
#include <QtWidgets/QApplication>
#include <QtCharts/QChartView>
#include <QtCharts/QLineSeries>
#include <QtCharts/QVXYModelMapper>

extern BOOL isRunning;

QtGuiApplication4::QtGuiApplication4(QWidget *parent)
	: QMainWindow(parent)
{
	ui.setupUi(this);
	stopButton = new QPushButton("STOP", this);
	stopButton->setGeometry(QRect(QPoint(10, 10), QSize(100, 50)));
	connect(stopButton, SIGNAL(clicked()), this, SLOT(quitSlot()));

	saveLocation = new QPushButton("Save location", this);
	saveLocation->setGeometry(QRect(QPoint(10, 10), QSize(100, 50)));
	saveLocation->setToolTip(tr("Set location to save data"));
	connect(saveLocation, SIGNAL(clicked()), this, SLOT(saveToFile()));
}

void QtGuiApplication4::saveToFile()
{
	QString fileName = QFileDialog::getSaveFileName(this,
		tr("Save Data"), "",
		tr("Text Files (*.txt);;All Files (*)"));
	if (fileName.isEmpty())
		throw;
	else {

		saveFile = new QFile(fileName);
		if (!saveFile->open(QIODevice::WriteOnly)) {
			QMessageBox::information(this, tr("Unable to open file"),
				saveFile->errorString());
			throw;
		}
	}
	isRunning = true;
}

void QtGuiApplication4::quitSlot()
{
	if (isRunning != false) {
		isRunning = false;
	}
	else {
		//do something
	}
}