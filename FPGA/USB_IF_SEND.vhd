
LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;

ENTITY USB_IF_SEND IS

PORT
	(
		-- Input ports
		USB_CLK			: IN  STD_LOGIC;
		USB_TXE			: IN  STD_LOGIC;																		-- USB send FIFO Full
		USB_DATA	     	: IN	STD_LOGIC_VECTOR (159 downto 0);											-- Data from MUX to write on USB
		USB_SEND     	: IN	STD_LOGIC;																		-- Request USB Data send
		USB_RESET		: IN	STD_LOGIC;
		-- inout ports
		USB_FTDI_DATA	: INOUT STD_LOGIC_VECTOR (7 downto 0);											-- FTDI data bus		
		USB_WR			: OUT STD_LOGIC;																		-- FTDI Write request
--		USB_FTDI_RESET	: OUT STD_LOGIC;																		-- USB FIFO Reset
		USB_SENT     	: OUT	STD_LOGIC																		-- USB Data written
		);
END ENTITY USB_IF_SEND;	
	
ARCHITECTURE archi OF USB_IF_SEND IS

TYPE		machine	IS	(ready, present_data, WR_start_tempo, WR_end, WR_end_tempo);			--needed states
SIGNAL	state		:	machine;                          												--state machine

BEGIN

PROCESS(USB_CLK, USB_RESET)				 

VARIABLE	count_WR_start	:	INTEGER RANGE 0 TO 3;														--3 cycles tempo for WR operation
VARIABLE	count_WR_end	:	INTEGER RANGE 0 TO 3;														--3 cycles tempo for WR operation
VARIABLE	Byte_pointer	:	INTEGER RANGE 0 TO 19;														--The number of the Byte to USB transfer
VARIABLE DATA_Buffer		:	STD_LOGIC_VECTOR (7 downto 0);											--The Data buffer to USB transfer 

--test
VARIABLE test_cnt			:	INTEGER		:= 0;

BEGIN

--IF(USB_RESET = '0') THEN
--	USB_SENT 		<= '1';																						-- USB send block is free
--ELSE	IF(USB_CLK'EVENT AND USB_CLK = '1') THEN
--			IF USB_SEND = '1' THEN
--					USB_SENT <= '0';
--				IF test_cnt < 100 THEN
--					test_cnt := test_cnt + 1;
--				ELSE
--					USB_SENT <= '1';
--					test_cnt	:= 0;
--				END IF;
--			END IF;
--		END IF;
--END IF;


IF(USB_RESET = '0') THEN
	state 			<= ready;
	USB_WR			<= '0';
	count_WR_start := 0;
	count_WR_end 	:= 0;
	Byte_pointer 	:= 0;
	USB_SENT 		<= '1';																						-- USB send block is free
	USB_FTDI_DATA	<= (OTHERS => 'Z');
				
ELSE	IF(USB_CLK'EVENT AND USB_CLK = '1') THEN
	IF (USB_SEND = '1') THEN																				-- USB transmission requested
		USB_SENT <= '0';																						-- USB transmission completed flag reset
	
-- Prepare data to present to FTDI
			CASE Byte_pointer IS
				WHEN 0 =>
					DATA_Buffer := USB_DATA (7 downto 0);
				WHEN 1 =>
					DATA_Buffer := USB_DATA (15 downto 8);	
				WHEN 2 =>
					DATA_Buffer := USB_DATA (23 downto 16);
				WHEN 3 =>
					DATA_Buffer := USB_DATA (31 downto 24);
				WHEN 4 =>
					DATA_Buffer := USB_DATA (39 downto 32);
				WHEN 5 =>
					DATA_Buffer := USB_DATA (47 downto 40);	
				WHEN 6 =>
					DATA_Buffer := USB_DATA (55 downto 48);
				WHEN 7 =>
					DATA_Buffer := USB_DATA (63 downto 56);				
				WHEN 8 =>
					DATA_Buffer := USB_DATA (71 downto 64);
				WHEN 9 =>
					DATA_Buffer := USB_DATA (79 downto 72);	
				WHEN 10 =>
					DATA_Buffer := USB_DATA (87 downto 80);
				WHEN 11 =>
					DATA_Buffer := USB_DATA (95 downto 88);
				WHEN 12 =>
					DATA_Buffer := USB_DATA (103 downto 96);
				WHEN 13 =>
					DATA_Buffer := USB_DATA (111 downto 104);	
				WHEN 14 =>
					DATA_Buffer := USB_DATA (119 downto 112);
				WHEN 15 =>
					DATA_Buffer := USB_DATA (127 downto 120);
				WHEN 16 =>
					DATA_Buffer := USB_DATA (135 downto 128);
				WHEN 17 =>
					DATA_Buffer := USB_DATA (143 downto 136);	
				WHEN 18 =>
					DATA_Buffer := USB_DATA (151 downto 144);
				WHEN 19 =>
					DATA_Buffer := USB_DATA (159 downto 152);				
				WHEN OTHERS =>
					DATA_Buffer := "10111101";	
			END CASE;

			
--			if DATA_Buffer = "11111111" then
--				DATA_Buffer := "10101010";
--			end if;
--			if DATA_Buffer = "01111111" then
--				DATA_Buffer := "10101010";
--			end if;
			
			
-- USB FTDI state machine
			CASE state IS
				WHEN ready =>
					IF (USB_TXE = '0') THEN
						state <= present_data;
						count_WR_start := 0;
						count_WR_end 	:= 0;
					END IF;
				WHEN present_data =>			
					USB_WR <= '1';
					USB_FTDI_DATA <= DATA_Buffer;
					state <= WR_start_tempo;
				WHEN WR_start_tempo =>			
					IF(count_WR_start = 3) THEN
						state <= WR_end;
					ELSE
						count_WR_start := count_WR_start + 1;
					END IF;
				WHEN WR_end =>
					USB_WR	<= '0';
					state		<= WR_end_tempo;
				WHEN WR_end_tempo =>			
					IF(count_WR_end = 3) THEN
						state <= ready;
						IF Byte_pointer = 19 THEN
							Byte_pointer := 0;
							USB_FTDI_DATA <= (OTHERS => 'Z');					-- Bus in Z state
							USB_SENT <= '1';											-- USB transmission completed flag set
						ELSE
							Byte_pointer := Byte_pointer + 1;
						END IF;
					ELSE
						count_WR_end := count_WR_end + 1;
					END IF;
				WHEN OTHERS =>
					NULL;
			END CASE;			-- CASE state IS
				
		END IF;				-- IF (USB_SEND = '1') THEN
		
	END IF;					-- ELSE	IF(USB_CLK'EVENT AND USB_CLK = '1') THEN
	
END IF;						-- IF(USB_RESET = '0') THEN
END PROCESS;
  
end archi;