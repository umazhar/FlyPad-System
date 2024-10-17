
LIBRARY	IEEE;
USE		IEEE.STD_LOGIC_1164.ALL;
USE		IEEE.STD_LOGIC_UNSIGNED.ALL;

ENTITY I2C_CH_SCHED IS

PORT
	(
		-- Input ports
		SCH_CLK						: IN	STD_LOGIC;							-- Master Clk		
		SCH_USB_DATA_SENT			: IN	STD_LOGIC;							-- 20 bytes word successfully copied to the USB FIFO
		SCH_RCVD_DATA				: IN	STD_LOGIC_VECTOR(87 DOWNTO 0);
		SCH_DATA_RCVD_FLAG		: IN	STD_LOGIC;
		-- out ports
		SCH_MASTER_RESET			: OUT	STD_LOGIC;							-- Master Reset signal
		SCH_I2C_ACQ_REQ			: OUT	STD_LOGIC;							-- 100Hz Clk for I2C Acq req
		SCH_LP_REQ					: OUT STD_LOGIC;
		SCH_SEL_EXP					: OUT	INTEGER RANGE 0 TO 63;			-- To the mux selection input
		SCH_USB_SEND_REQ			: OUT	STD_LOGIC;							-- USB Send request
		SCH_FTDI_RESET				: OUT STD_LOGIC;							-- USB FIFO Reset
		SCH_RCV_ENABLE				: OUT STD_LOGIC;
		B_DUMMY   	  : OUT		STD_LOGIC_VECTOR (7 DOWNTO 0)
		);

END ENTITY I2C_CH_SCHED;	
	
ARCHITECTURE archi OF I2C_CH_SCHED IS

TYPE		machine IS(idle, i2c_start, i2c_wait, lighting_processing, round_robin_mux, round_robin_usb_send, round_robin_usb_sent, finished);	-- state machine datatype
SIGNAL	state							:	machine;																			-- current state
SIGNAL	sch_usb_data_sent_prev	:	STD_LOGIC;																		-- previous state of SCH_USB_DATA_SENT
SIGNAL	sch_data_rcvd_flag_prev	:	STD_LOGIC;																		-- previous state of SCH_DATA_RCVD_FLAG

BEGIN

-- PROCESS(B_CLK, B_BUSY)				 
PROCESS(SCH_CLK)				 

VARIABLE reset_cnt			:	INTEGER		:= 0;
VARIABLE reset_done			:	STD_LOGIC	:= '0';

VARIABLE cnt_100Hz			:	INTEGER		:= 0;
VARIABLE cnt_latch			:	INTEGER		:= 0;

VARIABLE rd_rb_loop_cnt		:	INTEGER		:= 0;

VARIABLE usb_send_req		:	STD_LOGIC	:= '0';

VARIABLE start_i2c_acq		:	STD_LOGIC	:= '0';

VARIABLE all_words_sent		:	STD_LOGIC	:= '1';

VARIABLE inhibit_clock		:	STD_LOGIC	:= '0';

BEGIN

	IF(SCH_CLK'EVENT AND SCH_CLK = '1') THEN
-- Reset generation
		IF reset_done = '0' THEN
			SCH_MASTER_RESET	<= '0';
			SCH_FTDI_RESET		<=	'0';
			state 				<= finished;
			cnt_100Hz			:= 0;
			cnt_latch			:= 0;
			rd_rb_loop_cnt		:= 0;
			SCH_USB_SEND_REQ	<=	'0';
			usb_send_req		:= '0';
			SCH_I2C_ACQ_REQ	<= '0';
			SCH_LP_REQ			<= '0';
			start_i2c_acq		:= '0';
			SCH_SEL_EXP			<= 0;
			all_words_sent		:= '1';
			inhibit_clock		:=	'1';
			SCH_RCV_ENABLE		<= '0';
			IF reset_cnt < 10000 THEN
				reset_cnt := reset_cnt + 1;
			ELSE
				SCH_MASTER_RESET	<= '1';
				SCH_FTDI_RESET		<=	'1';
				reset_done			:= '1';
				reset_cnt			:= 0;
			END IF;
		ELSE	-- Reset has been done
			sch_usb_data_sent_prev	<= SCH_USB_DATA_SENT;							-- Log previous state of SCH_USB_DATA_SENT
			sch_data_rcvd_flag_prev	<= SCH_DATA_RCVD_FLAG;							-- Log previous state of SCH_DATA_RCVD_FLAG
			
			IF inhibit_clock = '0' THEN
				-- 100Hz SCH_I2C_ACQ_REQ generation
				IF cnt_100Hz < 500000 THEN
					cnt_100Hz := cnt_100Hz + 1;
				ELSE
					cnt_100Hz	:= 0;
					state			<= idle;
				END IF;
			END IF;

--B_DUMMY(0) <= all_words_sent;
--B_DUMMY(1) <= start_i2c_acq;

-- USB Transmission and channel round robin management			
			CASE state IS
				WHEN idle =>									-- USB overflow management
					SCH_RCV_ENABLE		<= '0';				-- Disable USB receive block
					IF	all_words_sent = '1' THEN
						state <= i2c_start;
					ELSE
						-- USB overflow !! => Go in RESET
						reset_done := '0';
					END IF;
				WHEN i2c_start =>
						SCH_I2C_ACQ_REQ	<= '1';
						start_i2c_acq		:= '1';
						state					<= i2c_wait;
						all_words_sent := '0';
				WHEN i2c_wait =>
					-- 1µs tempo for bridge data latching completion
					IF cnt_latch < 50 THEN
						cnt_latch	:= cnt_latch + 1;
					ELSE
						cnt_latch	:= 0;
						state			<= lighting_processing;
					END IF;
				WHEN lighting_processing =>
					-- 1µs tempo for bridge data latching completion
					SCH_I2C_ACQ_REQ	<= '0';
					start_i2c_acq 		:= '0';
					SCH_LP_REQ <= '1';
					IF cnt_latch < 50 THEN --is 50 cycles enough?
						cnt_latch	:= cnt_latch + 1;
					ELSE
						cnt_latch	:= 0;
						state			<= round_robin_mux;
					END IF;
				WHEN round_robin_mux =>
					SCH_LP_REQ <= '0';
					SCH_SEL_EXP			<=	rd_rb_loop_cnt;								-- Position the mux on the channel
					IF rd_rb_loop_cnt	<	16 THEN
						rd_rb_loop_cnt	:=	rd_rb_loop_cnt + 1;							-- Increase channel loop counter
						state <= round_robin_usb_send;
					ELSE
						rd_rb_loop_cnt	:=	0;													-- Last channel sent, exit the state machine
						state				<=	finished;
						all_words_sent := '1';
					END IF;
					-- Ajouter tempo ici si besoin ie si pb dans les data de chaque channel
				WHEN round_robin_usb_send =>
					SCH_USB_SEND_REQ	<=	'1';												-- Request USB sending
					usb_send_req		:= '1';
					IF (sch_usb_data_sent_prev = '0' AND SCH_USB_DATA_SENT = '1') THEN	-- Data were sent
						state <= round_robin_usb_sent;
						--B_DUMMY(0) <= '0';
						--B_DUMMY(1) <= '1';
					END IF;
				WHEN round_robin_usb_sent =>
					state <= round_robin_mux;												-- Select next I2C block data or exit if sent all I2C block data
					--state <= i2c_wait;
					SCH_USB_SEND_REQ	<=	'0';												-- Reset USB sending
					usb_send_req		:= '0';
				WHEN finished	=>
					-- Check now if data received on the USB FIFO
					SCH_RCV_ENABLE		<= '1';					-- Enable USB receive block, results will be read at the next 100Hz clock cycle
					B_DUMMY <= SCH_RCVD_DATA(7 DOWNTO 0);
					--	IF (sch_data_rcvd_flag_prev = '0' AND SCH_DATA_RCVD_FLAG = '1') THEN
									--B_DUMMY <= SCH_RCVD_DATA(7 DOWNTO 0);
									--B_DUMMY(0) <= '1';
							CASE SCH_RCVD_DATA(7 DOWNTO 0) IS
								WHEN "01000111" =>				-- Go command
									inhibit_clock := '0';
									--B_DUMMY(0) <= '1';
								WHEN "01010011" =>				-- Stop command
									inhibit_clock := '1';
									--B_DUMMY(0) <= '0';
								--WHEN "01000011" =>				-- Command command
									-- inhibit_clock = '1';
									-- Process parameters here
									-- Call I2C send function in I2C_USB_BRIDGE
								WHEN OTHERS =>
									NULL;
							END CASE;
						--END IF;
						
				WHEN OTHERS =>
					NULL;
			END CASE;		
			
		END IF;	-- IF reset_done = '0' THEN
	END IF;		-- IF(SCH_CLK'EVENT AND SCH_CLK = '1') THEN
	
END PROCESS;

END archi;