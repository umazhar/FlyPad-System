#pragma once
#include <iostream>
#include <exception>
#include "Constants.h"

using namespace std;

class ErrorException: public exception {
	private:	
		int errorCode;
	public:
		ErrorException(int myErrorCode) {
			errorCode = myErrorCode;
		}
		virtual const char* what() const throw()
		{
			if (errorCode == NO_FTDI_ERROR_CODE) { return "Could not find any FTDI devices to connect to"; }
			else if (errorCode == CANNOT_OPEN_FTDI_DEVICE_ERROR_CODE) { return "Could not open FTDI device for read/write IO"; }
			else if (errorCode == FTDI_RESET_ERROR_CODE) { return "Reset operation to FTDI failed"; }
			else if (errorCode == CANNOT_OPEN_FTDI_DEVICE_ERROR_CODE) { return "Reset operation to FTDI failed"; }
			else if (errorCode == FTDI_WRITE_IO_ERROR_CODE) { return "Write operation from FTDI failed"; }
			else if (errorCode == FTDI_READ_IO_ERROR_CODE) { return "Read operation from FTDI failed"; }
			else { return "Unknown exception"; }
		}
};