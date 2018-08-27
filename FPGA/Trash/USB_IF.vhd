
library ieee;
use ieee.std_logic_1164.all;

entity USB_IF_SEND is

port
	(
		-- Input ports
		CLK			: in  std_logic;
		RXF			: in  std_logic;
		DATA	     	: in	std_LOGIC_VECTOR (31 downto 0)
		SEND     	: in	std_logic;
		-- out ports
		FTDI_DATA	: out std_logic_vector (7 downto 0);
		WR				: out std_logic;	
		ALARM			: out std_logic;
  	);
end entity USB_IF_SEND;	
	
architecture archi of USB_IF_SEND is

begin

PROCESS(CLK)				 

-- On a send short square pulse

-- Copy DATA to internal register



-- Present Byte0 on FTDI_DATA port

-- Test RXF

-- If RXF not full, activate WR line 50ns min to write the data byte in the USB FIFO

-- If RXF full, activate ALARM line and write "FULL" int the USB FIFO

-- Tempo 50ns min 



-- Present Byte1 on FTDI_DATA port

-- Test RXF

-- If RXF not full, activate WR line 50ns min to write the data byte in the USB FIFO

-- If RXF full, activate ALARM line and write "FULL" int the USB FIFO

-- Tempo 50ns min 



-- Present Byte2 on FTDI_DATA port

-- Test RXF

-- If RXF not full, activate WR line 50ns min to write the data byte in the USB FIFO

-- If RXF full, activate ALARM line and write "FULL" int the USB FIFO

-- Tempo 50ns min 



-- Present Byte3 on FTDI_DATA port

-- Test RXF

-- If RXF not full, activate WR 50ns min line to write the data byte in the USB FIFO

-- If RXF full, activate ALARM line and write "FULL" int the USB FIFO

-- Tempo 50ns min 

end PROCESS;
  
  
  
end archi;