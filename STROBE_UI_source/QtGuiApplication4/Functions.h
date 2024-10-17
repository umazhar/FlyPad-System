#pragma once

int check_ftStatus(int ftStatus, int FTDIErrorCode);

tuple<int, FT_HANDLE> FTDI_setup();