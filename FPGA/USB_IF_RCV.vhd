
LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;

ENTITY USB_IF_RCV IS

PORT
	(
		-- Input ports
		RCV_CLK			: IN  STD_LOGIC;
		RCV_RESET		: IN	STD_LOGIC;																		-- Block RESET input
		RCV_RXF			: IN  STD_LOGIC;																		-- USB receive FIFO has data to be read
		RCV_ENABLE		: IN  STD_LOGIC;

		-- inout ports
		RCV_FTDI_DATA	: INOUT STD_LOGIC_VECTOR (7 downto 0);											-- FTDI data bus

		-- out ports
		RCV_RD					: OUT STD_LOGIC;																-- FTDI Read request
		RCV_RCVD_DATA			: OUT	STD_LOGIC_VECTOR (87 downto 0);									-- Data from the USB FIFO
		RCV_DATA_RCVD_FLAG 	: OUT	STD_LOGIC																-- USB Data received flag to the scheduler
--RCV_DUMMY   	  : OUT		STD_LOGIC_VECTOR (7 DOWNTO 0)
		);
END ENTITY USB_IF_RCV;	
	
ARCHITECTURE archi OF USB_IF_RCV IS

TYPE		machine_usb_rcv	IS	(check_can_receive, check_data_present, read_order, rd_to_valid_data_tempo, read_data, release_read, rd_to_rd_tempo);	--needed states
SIGNAL	state_rcv			:	machine_usb_rcv;                          																			--state machine

--SIGNAL 	rcv_rxf_prev		:	STD_LOGIC;																														-- Previous state of RCV_RXF

BEGIN

PROCESS(RCV_CLK, RCV_RESET)				 

VARIABLE	count_rd_to_valid_data	:	INTEGER	RANGE 0 TO 2	:= 0;
VARIABLE	count_rd_to_rd				:	INTEGER	RANGE 0 TO 6	:= 0;

BEGIN

IF(RCV_RESET = '0') THEN
	state_rcv 					<= check_can_receive;
	count_rd_to_valid_data 	:= 0;
	count_rd_to_rd 			:= 0;
	RCV_RD 						<= '1';
	RCV_DATA_RCVD_FLAG		<= '0';
	RCV_RCVD_DATA				<= (others => '0');
	--rcv_rxf_prev				<= '1';
	RCV_FTDI_DATA	<= (OTHERS => 'Z');
--RCV_DUMMY(7 DOWNTO 0) <= "00000000";
	
ELSE	IF(RCV_CLK'EVENT AND RCV_CLK = '1') THEN

			--rcv_rxf_prev <= RCV_RXF;											-- Log previous state of RCV_RXF
					--RCV_DUMMY(7 DOWNTO 2) <= "000000";
-- USB FTDI FIFO read state machine
			CASE state_rcv IS
				WHEN check_can_receive =>
					IF RCV_ENABLE = '1' THEN											-- Acquire 1 Byte
						state_rcv <= check_data_present;
					END IF;
				WHEN check_data_present =>
--					IF (rcv_rxf_prev = '1' AND RCV_RXF = '0') THEN		-- Data were received
					IF RCV_RXF = '0' THEN		-- Data were received					
						state_rcv <= read_order;
					ELSE
						state_rcv <= check_can_receive;
						RCV_FTDI_DATA	<= (OTHERS => 'Z');
					END IF;
					RCV_DATA_RCVD_FLAG		<= '0';
					--RCV_DUMMY(7 DOWNTO 2) <= "000001";						
				WHEN read_order =>			
					RCV_RD	<= '0';
					state_rcv		<= rd_to_valid_data_tempo;
					--RCV_DUMMY(7 DOWNTO 2) <= "000010";
				WHEN rd_to_valid_data_tempo =>			
					IF (count_rd_to_valid_data > 2) THEN
						state_rcv <= read_data;
						count_rd_to_valid_data := 0;
					ELSE
						count_rd_to_valid_data := count_rd_to_valid_data + 1;
					END IF;
					--RCV_DUMMY(7 DOWNTO 2) <= "000100";
				WHEN read_data =>
					RCV_RCVD_DATA(7 DOWNTO 0)	<=	RCV_FTDI_DATA;
					state_rcv		<=	release_read;
					--RCV_DUMMY(7 DOWNTO 2) <= "001000";
				WHEN release_read =>
					RCV_RD <= '1';
					state_rcv <= rd_to_rd_tempo;
					RCV_DATA_RCVD_FLAG		<= '1';
					--RCV_DUMMY(7 DOWNTO 2) <= "010000";
				WHEN rd_to_rd_tempo =>
					IF (count_rd_to_rd > 6) THEN
						--state_rcv <= check_data_present;
						count_rd_to_rd := 0;
						--RCV_DUMMY <= RCV_FTDI_DATA;
						state_rcv <= check_can_receive;
						RCV_FTDI_DATA	<= (OTHERS => 'Z');
					ELSE
						count_rd_to_rd := count_rd_to_rd + 1;
					END IF;
					--RCV_DUMMY(7 DOWNTO 2) <= "100000";
				WHEN OTHERS =>
					NULL;
					
			END CASE;		-- CASE state IS
	
	END IF;					-- ELSE	IF(USB_CLK'EVENT AND USB_CLK = '1') THEN
END IF;						-- IF(USB_RESET = '0') THEN

END PROCESS;
  
end archi;