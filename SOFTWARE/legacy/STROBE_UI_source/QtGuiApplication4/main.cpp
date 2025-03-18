#include <iostream>
#include <string>
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include "ftd2xx.h"
#include <conio.h>
#include <thread>
#include <assert.h>
#include <deque>
#include "QtGuiApplication4.h"
#include"qcustomplot.h"
#include <QtWidgets/QApplication>
#include <cstdlib>
#include <QtCharts/QChartView>
#include <QtCharts/QLineSeries>
#include <QFile>
#include <QtOpenGL/QGLFormat>
#include <mutex>
#include "Exceptions.h"
#include "Functions.h"
#include "Constants.h"

using namespace std;

char STOP_COMMAND[2] = "S";

// operational globals
extern BOOL isRunning = false;

short int dataFrame[NUM_DATAFRAME_VALUES];
mutex dataFrameHistoryMutex;

void simulateDataListener(QFile* saveFile) {
	QTextStream saveOut(saveFile);
	while (isRunning) {
		std::this_thread::sleep_for(0.01s);
		for (int i = 0; i < NUM_DATAFRAME_VALUES; i++) {
			dataFrame[i] = rand() % MAX_CAPDAC_VALUE;
			saveOut << dataFrame[i] << "\t";
		}
		saveOut << "\n";
	}
	saveFile->close();
}

void dataListener(FT_HANDLE ftHandle, QFile* saveFile) {
	/*
	Takes as input a FTDI device handle and performs continuous read operations 
	until stop signal. At stop signal, sends 'exit' command to FTDI device.
	Saves data collected to a file in plaintext using a datastream.

	@param ftHandle FTDI device handle
	@param saveFile QFile to save data to
	*/
	QTextStream saveOut(saveFile);
	while (isRunning) {
		FT_STATUS ftStatus;
		unsigned char packet[FULL_PACKET_SIZE];
		DWORD BytesRead;
		ftStatus = FT_Read(ftHandle, packet, sizeof(packet), &BytesRead);
		assert(check_ftStatus(ftStatus, FTDI_READ_IO_ERROR_CODE) != 0); // hmm, this may not be the best way

		assert(BytesRead == FULL_PACKET_SIZE);
		for (int i = 0; i < sizeof(packet); i += BYTES_PER_ARENA)
		{
			int arenaOffset = (i / BYTES_PER_ARENA) * NUM_DATAVALS_PER_ARENA;
			// Check if device data is valid
			if (packet[i + 18] != INVALID_DEVICE_DATA)
			{
				dataFrame[arenaOffset + 0] = int((((packet[i + 1] << 8) | packet[i + 2]) >> 4));
				dataFrame[arenaOffset + 1] = int((((packet[i + 3] << 8) | packet[i + 4]) >> 4));
				dataFrame[arenaOffset + 2] = (int(packet[i + 5]) & 0b00000001) * LED_GRAPHICAL_SCALE;
				dataFrame[arenaOffset + 3] = ((int(packet[i + 5]) & 0b00000010) >> 1) * LED_GRAPHICAL_SCALE;
			}
			else {
				dataFrame[arenaOffset + 0] = -1;
				dataFrame[arenaOffset + 1] = -1;
				dataFrame[arenaOffset + 2] = -1;
				dataFrame[arenaOffset + 3] = -1;
			}
			saveOut << dataFrame[arenaOffset + 0] << "\t";
			saveOut << dataFrame[arenaOffset + 1] << "\t";
			saveOut << dataFrame[arenaOffset + 2] << "\t";
			saveOut << dataFrame[arenaOffset + 3] << "\t";
		}
		saveOut << "\n";
	}

	FT_STATUS ftStatus;
	DWORD BytesWritten;
	ftStatus = FT_Write(ftHandle, STOP_COMMAND, sizeof(STOP_COMMAND), &BytesWritten);
	assert(check_ftStatus(ftStatus, FTDI_WRITE_IO_ERROR_CODE) != 0);
}

int main(int argc, char **argv) {
	/*
	Main has 3 primary tasks:
		* set up the UI
		* set up the FTDI device (acquisition, sending a start signal, etc)
		* begin the data collection thread
		* control the UI (pull data from data collection thread and continuously 
		update the plots)
	*/

	// set up the UI
	QApplication a(argc, argv);
	QtGuiApplication4 w;

	// lol disable the x button to avoid having to re-implement the closeEvents() function
	w.setWindowFlags(Qt::WindowTitleHint | Qt::WindowMinimizeButtonHint);

	QWidget *widget = new QWidget();
	QGridLayout *GridLayout = new QGridLayout;
	w.setWindowTitle("STROBE: Sip-TRiggered Optogenetic Behavior Enclosure");

	QCustomPlot *customPlotArray = new QCustomPlot[NUM_ARENAS];
	for (int arenaIndex = 0; arenaIndex < NUM_ARENAS; arenaIndex++) {
		customPlotArray[arenaIndex].yAxis->setRange(0, MAX_CAPDAC_VALUE);
		customPlotArray[arenaIndex].setOpenGl(true);
		for (int internalDatavalIndex = 0; internalDatavalIndex < NUM_DATAVALS_PER_ARENA; 
			internalDatavalIndex++) {
			customPlotArray[arenaIndex].addGraph();
			if (internalDatavalIndex % 2 == 0) {
				customPlotArray[arenaIndex].graph(internalDatavalIndex)->setPen(QPen(Qt::red));
			}
			else {
				customPlotArray[arenaIndex].graph(internalDatavalIndex)->setPen(QPen(Qt::blue));
			}
		}

		GridLayout->addWidget(&customPlotArray[arenaIndex], int(arenaIndex / 
			NUM_ARENAS_PER_GUI_ROW), arenaIndex % NUM_ARENAS_PER_GUI_ROW);
	}

	// add buttons
	QVBoxLayout *ButtonLayout = new QVBoxLayout;
	ButtonLayout->addWidget(w.stopButton);
	ButtonLayout->addWidget(w.saveLocation);
	QWidget *cellWidget = new QWidget();
	cellWidget->setLayout(ButtonLayout);
	GridLayout->addWidget(cellWidget);
	
	// add text
	QGridLayout *textLogoLayout = new QGridLayout;
	QLabel *textLabel = new QLabel(QObject::tr("STROBE: Sip-TRiggered Optogenetic\nBehavior Enclosure\n\nDeveloped by Rachel Chan,\nHan Zhang (UBC ENPH)\nIn collaboration with\nthe Gordon Lab (UBC Zoology)"));
	textLogoLayout->addWidget(textLabel, 0, 1, 1, 2);
	/*
	QLabel ENPHLabLogoLabel;
	QPixmap ENPHPixmap("./Resources/ENPHLogo.png");
	ENPHLabLogoLabel.setPixmap(ENPHPixmap.scaledToWidth(120)
	);
	textLogoLayout->addWidget(&ENPHLabLogoLabel,1,1, Qt::AlignTop);	

	QLabel GordonLabLogoLabel;
	QPixmap GordonLabPixmap;
	GordonLabPixmap.load("./Resources/GordonLabLogo.png");
	GordonLabLogoLabel.setPixmap(GordonLabPixmap.scaledToHeight(90));
	textLogoLayout->addWidget(&GordonLabLogoLabel,1,2, Qt::AlignTop);
		*/

	QWidget *textLogoCellWidget = new QWidget();
	textLogoCellWidget->setLayout(textLogoLayout);
	GridLayout->addWidget(textLogoCellWidget);

	GridLayout->setSpacing(0);
	GridLayout->setMargin(0);
	widget->setLayout(GridLayout);
	w.setCentralWidget(widget);
	w.showMaximized();

	while (!isRunning) {
		qApp->processEvents();
	}

	int ftStatus;
	FT_HANDLE ftHandle;
	tie(ftStatus, ftHandle) = FTDI_setup();
	if (ftStatus != EXIT_SUCCESS) { // check that our FTDI returned a successful exit status
		return ftStatus;
	}

	// begin threads
//	thread dataThread(simulateDataListener, w.saveFile);
	thread dataThread(dataListener, ftHandle, w.saveFile);

	// update plots until stop
	int historicValCounter;
	historicValCounter = 0;
	while (isRunning) {
		for (int arenaIndex = 0; arenaIndex < NUM_ARENAS; arenaIndex++) {
			for (int internalDatavalIndex = 0; internalDatavalIndex < NUM_DATAVALS_PER_ARENA; 
				internalDatavalIndex++) {
				customPlotArray[arenaIndex].graph(internalDatavalIndex)->addData(
					historicValCounter,	
					dataFrame[arenaIndex * NUM_DATAVALS_PER_ARENA + internalDatavalIndex]);
				customPlotArray[arenaIndex].graph(internalDatavalIndex)->data()->removeBefore(
					historicValCounter - NUM_HISTORIC_VALUES);
			}
			customPlotArray[arenaIndex].xAxis->setRange(historicValCounter, 
				NUM_HISTORIC_VALUES, Qt::AlignRight);
			customPlotArray[arenaIndex].replot();
		}
		historicValCounter++;
		qApp->processEvents();
	}
	dataThread.join();
	delete[] customPlotArray;
	return EXIT_SUCCESS;
}