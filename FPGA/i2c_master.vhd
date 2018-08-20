--------------------------------------------------------------------------------
--
--   FileName:		 i2c_master.vhd
--   Dependencies:	 none
--   Design Software:  Quartus II 32-bit Version 11.1 Build 173 SJ Full Version
--
--   HDL CODE IS PROVIDED "AS IS."  DIGI-KEY EXPRESSLY DISCLAIMS ANY
--   WARRANTY OF ANY KIND, WHETHER EXPRESS OR IMPLIED, INCLUDING BUT NOT
--   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
--   PARTICULAR PURPOSE, OR NON-INFRINGEMENT. IN NO EVENT SHALL DIGI-KEY
--   BE LIABLE FOR ANY INCIDENTAL, SPECIAL, INDIRECT OR CONSEQUENTIAL
--   DAMAGES, LOST PROFITS OR LOST DATA, HARM TO YOUR EQUIPMENT, COST OF
--   PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR SERVICES, ANY CLAIMS
--   BY THIRD PARTIES (INCLUDING BUT NOT LIMITED TO ANY DEFENSE THEREOF),
--   ANY CLAIMS FOR INDEMNITY OR CONTRIBUTION, OR OTHER SIMILAR COSTS.
--
--   Version History
--   Version 1.0 11/1/2012 Scott Larson
--   Version 2.0 9/12/2013 Steve Safarik
--	
--------------------------------------------------------------------------------

LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.std_logic_unsigned.all;


ENTITY i2c_master IS
	GENERIC(
		input_clk_frq : INTEGER := 50_000_000; --input clock speed from user logic in Hz
		bus_clk_frq   : INTEGER := 400_000);   --speed the i2c bus (scl) will run at in Hz
	PORT(
		clk			: IN	 STD_LOGIC;						--system clock
		reset_n		: IN	 STD_LOGIC;						--active low reset
		ena			: IN	 STD_LOGIC;						--latch in command
		addr		: IN	 STD_LOGIC_VECTOR(6 DOWNTO 0);	--address of target slave
		rw			: IN	 STD_LOGIC;						--'0' is write, '1' is read
		data_wr		: IN	 STD_LOGIC_VECTOR(7 DOWNTO 0);	--data to write to slave
		busy		: OUT	 STD_LOGIC;						--indicates transaction in progress
		data_rd		: OUT	 STD_LOGIC_VECTOR(7 DOWNTO 0);	--data read from slave
		ack_error	: BUFFER STD_LOGIC;						--flag if improper acknowledge from slave
		sda			: INOUT  STD_LOGIC := '1';				--serial data output of i2c bus
		scl			: INOUT  STD_LOGIC						--serial clock output of i2c bus
	);
END i2c_master;

ARCHITECTURE logic OF i2c_master IS
	CONSTANT divider  :  INTEGER := (input_clk_frq/bus_clk_frq)/4; --number of clocks in 1/4 cycle of scl
	TYPE machine IS(s_idle, s_start, s_command, s_ack_cmd, s_write, s_read, s_ack_wr, s_ack_rd, s_stop); --needed states
	SIGNAL  state     :  machine;						--state machine
	SIGNAL  data_clk  :  STD_LOGIC := '0';				--clock edges for sda
	SIGNAL  bus_clk   :  STD_LOGIC := '0';				--constantly running internal scl
	SIGNAL  scl_ena   :  STD_LOGIC := '0';				--enables internal scl to output
	SIGNAL  sda_int_n :  STD_LOGIC := '1';				--internal sda
	SIGNAL  sda_ena_n :  STD_LOGIC := '1';				--enables internal sda to output
	SIGNAL  addr_rw   :  STD_LOGIC_VECTOR(7 DOWNTO 0);	--latched in address and read/write
	SIGNAL  data_tx   :  STD_LOGIC_VECTOR(7 DOWNTO 0);	--latched in data to write to slave
	SIGNAL  data_rx   :  STD_LOGIC_VECTOR(7 DOWNTO 0);	--data received from slave
	SIGNAL  bit_cnt   :  INTEGER RANGE 0 TO 7 := 7;		--tracks bit number in transaction
	SIGNAL  stretch   :  STD_LOGIC := '0';				--identifies if slave is stretching scl
	
	SIGNAL  sda_delay :  STD_LOGIC_VECTOR(1 to 2) := "00"; --delayed values of sda, for clock syncing
  
BEGIN
	--generate the timing for the bus clock (bus_clk) and the data clock (data_clk)
	PROCESS(clk, reset_n)
		VARIABLE count : INTEGER RANGE 0 TO divider*4;	--timing for clock generation
	BEGIN
		IF(reset_n = '0') THEN				--reset asserted
			stretch <= '0';
			count := 0;
			state <= s_idle;				--return to initial state
			busy <= '1';					--indicate not available
			scl_ena <= '0';					--sets scl high impedance
			sda_int_n <= '1';				--sets sda high impedance
			bit_cnt <= 7;					--restarts data bit counter
			data_rd <= "00000000";			--clear data read port
			ack_error <= '0';

		ELSIF(clk'EVENT AND clk = '1') THEN
			IF(count = divider*4-1) THEN	--end of timing cycle
				count := 0;					--reset timer
			ELSIF(stretch = '0') THEN		--clock stretching from slave not detected
				count := count + 1;			--continue clock generation timing
			END IF;

			CASE count IS
				----------------------------------- first 1/4 cycle of clocking
				WHEN 0 TO divider-1 =>
					bus_clk <= '0';
					data_clk <= '0';

				----------------------------------- data_clk rising edge.
				WHEN divider =>
					CASE state IS
						WHEN s_idle =>						--idle state
							IF(ena = '1') THEN					--transaction requested
								busy <= '1';					--flag busy
								addr_rw <= addr & rw;			--collect requested slave address and command
								data_tx <= data_wr;			--collect requested data to write
								state <= s_start;				--go to start bit
							ELSE								--remain idle
								busy <= '0';					--unflag busy
								state <= s_idle;				--remain idle
							END IF;
						WHEN s_start =>						--start bit of transaction
							busy <= '1';						--resume busy if continuous mode
							scl_ena <= '1';						--enable scl output
							sda_int_n <= addr_rw(bit_cnt);		--set first address bit to bus
							state <= s_command;					--go to command
						WHEN s_command =>						--address and command byte of transaction
							IF(bit_cnt = 0) THEN				--command transmit finished
								sda_int_n <= '1';				--release sda for slave acknowledge
								bit_cnt <= 7;					--reset bit counter for "byte" states
								state <= s_ack_cmd;				--go to slave acknowledge (command)
							ELSE								--next clock cycle of command state
								bit_cnt <= bit_cnt - 1;			--keep track of transaction bits
								sda_int_n <= addr_rw(bit_cnt-1);--write address/command bit to bus
								state <= s_command;				--continue with command
							END IF;
						WHEN s_ack_cmd =>					--slave acknowledge bit (command)
							IF(addr_rw(0) = '0') THEN			--write command
								sda_int_n <= data_tx(bit_cnt);	--write first bit of data
								state <= s_write;				--go to write byte
							ELSE								--read command
								sda_int_n <= '1';				--release sda from incoming data
								state <= s_read;				--go to read byte
							END IF;
						WHEN s_write =>						--write byte of transaction
							busy <= '1';						--resume busy if continuous mode
							IF(bit_cnt = 0) THEN				--write byte transmit finished
								sda_int_n <= '1';				--release sda for slave acknowledge
								bit_cnt <= 7;					--reset bit counter for "byte" states
								state <= s_ack_wr;				--go to slave acknowledge (write)
							ELSE								--next clock cycle of write state
								bit_cnt <= bit_cnt - 1;			--keep track of transaction bits
								sda_int_n <= data_tx(bit_cnt-1);--write next bit to bus
								state <= s_write;				--continue writing
							END IF;
						WHEN s_read =>						--read byte of transaction
							busy <= '1';						--resume busy if continuous mode
							IF(bit_cnt = 0) THEN				--read byte receive finished
								IF(ena = '1' AND rw = '1') THEN	--continuing with another read
									sda_int_n <= '0';			--acknowledge the byte has been received
								ELSE							--stopping or continuing with a write
									sda_int_n <= '1';			--send a no-acknowledge (before stop or repeated start)
								END IF;
								bit_cnt <= 7;					--reset bit counter for "byte" states
								data_rd <= data_rx;				--output received data
								state <= s_ack_rd;				--go to master acknowledge
							ELSE								--next clock cycle of read state
								bit_cnt <= bit_cnt - 1;			--keep track of transaction bits
								state <= s_read;				--continue reading
							END IF;
						   
						WHEN s_ack_wr =>					--slave acknowledge bit (write)
							IF(ena = '1') THEN					--continue transaction
								busy <= '0';					--continue is accepted
								addr_rw <= addr & rw;			--collect requested slave address and command
								data_tx <= data_wr;				--collect requested data to write
								IF(rw = '1') THEN				--continue transaction with a read
									state <= s_start;			--go to repeated start
								ELSE							--continue transaction with another write
									sda_int_n <= data_wr(bit_cnt);--write first bit of data
									state <= s_write;			--go to write byte
								END IF;
							ELSE								--complete transaction
								scl_ena <= '0';					--disable scl
								state <= s_stop;				--go to stop bit
							END IF;
						   
						WHEN s_ack_rd =>					--master acknowledge bit after a read
							IF(ena = '1') THEN					--continue transaction
								busy <= '0';					--continue is accepted and data received is available on bus
								addr_rw <= addr & rw;			--collect requested slave address and command
								data_tx <= data_wr;				--collect requested data to write
								IF(rw = '0') THEN				--continue transaction with a write
								  state <= s_start;				--repeated start
								ELSE							--continue transaction with another read
								  sda_int_n <= '1';				--release sda from incoming data
								  state <= s_read;				--go to read byte
								END IF;
							ELSE								--complete transaction
								scl_ena <= '0';					--disable scl
								state <= s_stop;				--go to stop bit
							END IF;
						WHEN s_stop =>						--stop bit of transaction
						   busy <= '0';							--unflag busy
						   state <= s_idle;						--go to ready state
					END CASE;	
				  
				----------------------------------- second 1/4 cycle of clocking
				WHEN divider+1 TO divider*2-1 =>
					bus_clk <= '0';
					data_clk <= '1';

				----------------------------------- third 1/4 cycle of clocking
				WHEN divider*2 TO divider*3-1 =>
					bus_clk <= 'Z';							--release scl
					IF(scl = '0') THEN						--detect if slave is stretching clock
						stretch <= '1';
					ELSE
						stretch <= '0';
					END IF;
					data_clk <= '1';
					 
				----------------------------------- data_clk falling edge.
				WHEN divider*3 =>
					CASE state IS
						WHEN s_start =>						--starting new transaction
							ack_error <= '0';				--reset acknowledge error flag
						WHEN s_ack_cmd =>					--receiving slave acknowledge (command)
							ack_error <= sda OR ack_error;	--set error output if no-acknowledge
						WHEN s_read =>						--receiving slave data
							data_rx(bit_cnt) <= sda;		--receive current slave data bit
						WHEN s_ack_wr =>					--receiving slave acknowledge (write)
							ack_error <= sda OR ack_error;	--set error output if no-acknowledge
						WHEN OTHERS =>
							NULL;
					END CASE;
				  
				----------------------------------- last 1/4 cycle of clocking
				WHEN OTHERS =>
					bus_clk <= 'Z';
					data_clk <= '0';
			END CASE;
		END IF;
	END PROCESS;

  
	--set sda output
	WITH state SELECT
		sda_ena_n <=  data_clk WHEN s_start,		--generate start condition
					  NOT data_clk WHEN s_stop,		--generate stop condition
					  sda_int_n WHEN OTHERS;		--set to internal sda signal
		
	--set scl and sda outputs
	scl <= bus_clk WHEN scl_ena = '1' ELSE 'Z';
	sda <= '0' WHEN sda_ena_n = '0' ELSE 'Z';
  
END logic;
