#pragma once
#include <string>
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include "ftd2xx.h"
#include "QtGuiApplication4.h"
#include <QtWidgets/QApplication>
#include "Exceptions.h"
#include "Constants.h"

using namespace std;

char START_COMMAND[2] = "G";

int check_ftStatus(int ftStatus, int FTDIErrorCode) {
	/*
	Takes a FT_STATUS object as input and checks if it indicates the FTDI operation was
	successful. If not, throw the exception corresponding to FTDIErrorCode and return a
	general error code so main loop gets the signal to exit.

	@param ftstatus FTDI operation exit status
	@param FTDIErrorCode Error code corresponding to the exception to be thrown if
	operation was not successful
	@return EXIT_FAILURE or EXIT_SUCCESS to tell the main loop what to do next
	*/

	if (!FT_SUCCESS(ftStatus)) {
		try {
			throw ErrorException(FTDIErrorCode);
		}
		catch (exception& e)
		{
			QMessageBox::critical(NULL, QObject::tr("FTDI Error"), QObject::tr(e.what()));
			return EXIT_FAILURE;
		}
	}
	else {
		return EXIT_SUCCESS;
	}
}

tuple<int, FT_HANDLE> FTDI_setup() {
	// set up the FTDI
	FT_HANDLE ftHandle;
	FT_STATUS ftStatus;

	char *BufPtrs[3]; // pointer to array of 3 pointers
	char Buffer1[64]; // buffer for product description of first device found
	char Buffer2[64]; // buffer for product description of second device
	DWORD numDevs;

	// initialize the array of pointers
	BufPtrs[0] = Buffer1;
	BufPtrs[1] = Buffer2;
	BufPtrs[2] = NULL; // last entry should be NULL
	ftStatus = FT_ListDevices(BufPtrs, &numDevs, FT_LIST_ALL | FT_OPEN_BY_DESCRIPTION);
	if (check_ftStatus(ftStatus, NO_FTDI_ERROR_CODE) != EXIT_SUCCESS) {
		return make_tuple(NO_FTDI_ERROR_CODE, ftHandle);
	}

	ftStatus = FT_OpenEx("UMFT240XA", FT_OPEN_BY_DESCRIPTION, &ftHandle);
	if (check_ftStatus(ftStatus, CANNOT_OPEN_FTDI_DEVICE_ERROR_CODE) != EXIT_SUCCESS) {
		return make_tuple(CANNOT_OPEN_FTDI_DEVICE_ERROR_CODE, ftHandle);
	}

	ftStatus = FT_ResetDevice(ftHandle);
	if (check_ftStatus(ftStatus, FTDI_RESET_ERROR_CODE) != EXIT_SUCCESS) {
		return make_tuple(FTDI_RESET_ERROR_CODE, ftHandle);
	}

	FT_SetTimeouts(ftHandle, FTDI_READ_TIMEOUT, FTDI_WRITE_TIMEOUT);

	DWORD BytesWritten;
	ftStatus = FT_Write(ftHandle, START_COMMAND, sizeof(START_COMMAND), &BytesWritten);
	if (check_ftStatus(ftStatus, FTDI_WRITE_IO_ERROR_CODE) != EXIT_SUCCESS) {
		return make_tuple(FTDI_WRITE_IO_ERROR_CODE, ftHandle);
	}

	return make_tuple(EXIT_SUCCESS, ftHandle);
}