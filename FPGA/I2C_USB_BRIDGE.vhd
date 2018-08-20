
library ieee;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

entity I2C_USB_BRIDGE is

port
	(
		-- Input ports
		B_CLK				: IN  	STD_LOGIC;								-- Master Clk
		B_RESET_IN		: IN  	STD_LOGIC;								-- Reset		
		B_I2C_ACQ_REQ	: IN  	STD_LOGIC;								-- 100Hz I²C acquisition request clock
		B_BUSY     		: IN    	STD_LOGIC;                    	-- I2C indicates transaction in progress
		B_DATA_RD  		: IN    	STD_LOGIC_VECTOR(7 DOWNTO 0); 	-- I2C data read from slave
		B_CHANNEL_ID	: IN    	STD_LOGIC_VECTOR(7 DOWNTO 0); 	-- Sensor Channel Id
		
		-- out ports		
		B_ENA   	 	 	: OUT    STD_LOGIC;                    	-- I2C latch in command
		B_ADDR   	  	: OUT    STD_LOGIC_VECTOR(6 DOWNTO 0); 	-- I2C address of target slave
		B_RW     	  	: OUT    STD_LOGIC;                    	-- I2C '0' is write, '1' is read
		B_DATA_WR	  	: OUT    STD_LOGIC_VECTOR(7 DOWNTO 0); 	-- I2C data to write to slave
		B_DATA   	  	: OUT		STD_LOGIC_VECTOR(159 DOWNTO 0)	-- Data to write on USB
																					
--		B_ACK_ERR 		: BUFFER STD_LOGIC                   		-- I2C flag if improper acknowledge from slave

--		B_DUMMY   	  : OUT		STD_LOGIC_VECTOR (7 DOWNTO 0)
		
		);
end entity I2C_USB_BRIDGE;	
	
architecture archi of I2C_USB_BRIDGE is

SIGNAL slave_addr				:	STD_LOGIC_VECTOR(6 DOWNTO 0)	:= "1001000";
SIGNAL busy_prev				:	STD_LOGIC;
--SIGNAL i2c_acq_requested	:	STD_LOGIC	:= '0';
--SIGNAL I2C_DATA_BUFFER	:	STD_LOGIC_VECTOR(159 DOWNTO 0)	:= (others => '0');
SIGNAL b_i2c_acq_req_prev	:	STD_LOGIC;								-- previous state of B_I2C_ACQ_REQ

BEGIN

-- PROCESS(B_CLK, B_BUSY)				 
--PROCESS(B_CLK, B_START_EXP, B_I2C_ACQ_REQ)

PROCESS(B_CLK, B_RESET_IN)				 


VARIABLE busy_cnt   			:	INTEGER		:= 0;
VARIABLE I2C_ACQ_REQUESTED :	STD_LOGIC	:= '0';
VARIABLE I2C_DATA_BUFFER	:	STD_LOGIC_VECTOR(159 DOWNTO 0)	:= (others => '0');

BEGIN

--B_RESET_N <= B_START_EXP; --old manual button reset

IF B_RESET_IN = '0' THEN
	busy_cnt				:= 0;
	I2C_ACQ_REQUESTED	:= '0';
	I2C_DATA_BUFFER	:= (others => '0');
	B_ENA					<= '0';
	B_ADDR				<= (others => '0');
	B_RW					<= '0';
	B_DATA_WR			<= (others => '0');
	B_DATA				<= (others => '0');

ELSE IF(B_CLK'EVENT AND B_CLK = '1') THEN

--	-- Latch data acquisition request
--	--IF(B_I2C_ACQ_REQ'EVENT AND B_I2C_ACQ_REQ = '1') THEN
--	IF B_I2C_ACQ_REQ = '1' THEN
--		CASE I2C_ACQ_REQUESTED IS
--			WHEN '0' =>
--				I2C_ACQ_REQUESTED := '1';
--				B_DATA <= I2C_DATA_BUFFER;									-- Latch data acquired on the previous request
--			WHEN '1' =>
--				I2C_DATA_BUFFER(151 DOWNTO 144) := "00111111";		-- Signaling an error by using a code the sensor cannot produce
--			WHEN OTHERS => NULL;
--		END CASE;
--	END IF;																		-- End if B_I2C_ACQ_REQ 100Hz I²C req


	b_i2c_acq_req_prev <= B_I2C_ACQ_REQ;								-- Log previous state of B_I2C_ACQ_REQ
	IF (b_i2c_acq_req_prev = '0' AND B_I2C_ACQ_REQ = '1') THEN	-- Latch B_I2C_ACQ_REQ rising edge
		CASE I2C_ACQ_REQUESTED IS
			WHEN '0' =>
				I2C_ACQ_REQUESTED := '1';
			WHEN '1' =>
				I2C_DATA_BUFFER	:= (others => '0');
				busy_cnt				:= 0;
				I2C_DATA_BUFFER(151 DOWNTO 144) := "00111111";		-- Signaling an error by using a code the sensor cannot produce
			WHEN OTHERS => NULL;
		END CASE;

		I2C_DATA_BUFFER(159 DOWNTO 152) := B_CHANNEL_ID;
		
		  
	-- Frame shifts detection
		IF I2C_DATA_BUFFER(151 DOWNTO 150) /= "11" THEN
			I2C_DATA_BUFFER(151 DOWNTO 144) := "00111111";
		END IF;
		IF I2C_DATA_BUFFER(143 DOWNTO 142) /= "11" THEN
			I2C_DATA_BUFFER(151 DOWNTO 144) := "00111111";
		END IF;		
				
		
		B_DATA <= I2C_DATA_BUFFER;									-- Latch data acquired on the previous request
		I2C_DATA_BUFFER	:= (others => '0');					-- Reset Buffer
--		I2C_DATA_BUFFER(159 DOWNTO 152) := "10011001";
--		I2C_DATA_BUFFER(151 DOWNTO 144) := "10011001";
--		I2C_DATA_BUFFER(143 DOWNTO 136) := "10011001";
--		I2C_DATA_BUFFER(135 DOWNTO 128) := "10011001";
--		I2C_DATA_BUFFER(127 DOWNTO 120) := "10011001";
--		I2C_DATA_BUFFER(119 DOWNTO 112) := "10011001";
--		I2C_DATA_BUFFER(111 DOWNTO 104) := "10011001";
--		I2C_DATA_BUFFER(103 DOWNTO 96) := "10011001";
--		I2C_DATA_BUFFER(95 DOWNTO 88) := "10011001";
--		I2C_DATA_BUFFER(87 DOWNTO 80) := "10011001";
--		I2C_DATA_BUFFER(79 DOWNTO 72) := "10011001";
--		I2C_DATA_BUFFER(71 DOWNTO 64) := "10011001";
--		I2C_DATA_BUFFER(63 DOWNTO 56) := "10011001";
--		I2C_DATA_BUFFER(55 DOWNTO 48) := "10011001";
--		I2C_DATA_BUFFER(47 DOWNTO 40) := "10011001";	
--		I2C_DATA_BUFFER(39 DOWNTO 32) := "10011001";
--		I2C_DATA_BUFFER(31 DOWNTO 24) := "10011001";
--		I2C_DATA_BUFFER(23 DOWNTO 16) := "10011001";
--		I2C_DATA_BUFFER(15 DOWNTO 8) := "10011001";	
--		I2C_DATA_BUFFER(7 DOWNTO 0) := "10011001";
		I2C_DATA_BUFFER(159 DOWNTO 152) := B_CHANNEL_ID;
	END IF;
	
IF I2C_ACQ_REQUESTED = '1' THEN
--	B_DUMMY <= "00000000";

	--B_RESET_N <= B_START_EXP;
	--B_RESET_N <= '0';

	--I²C Busy counter management
		busy_prev <= B_BUSY;									--capture the value of the previous i2c busy signal
		IF(busy_prev = '0' AND B_BUSY = '1') THEN		--i2c busy just went high
			busy_cnt := busy_cnt + 1;							--counts the times busy has gone from low to high during transaction
		END IF;

--		  B_DUMMY(7) <= B_BUSY; --red probe
--		  B_DUMMY(6) <= busy_prev; --green probe
 
--I²C Communications State Machine 
CASE busy_cnt IS											--busy_cnt keeps track of which command we are on
	WHEN 0 =>												--no command latched in yet
--		B_RESET_N <= '1';
		IF I2C_ACQ_REQUESTED = '1' THEN
			B_ENA <= '1';									--initiate the transaction
--			B_NEW_DATA_RDY <= '0';						--reset the Data Rdy Flag
		END IF;
      B_ADDR <= slave_addr;							--set the address of the slave
      B_RW <= '0';										--command 1 is a write
      B_DATA_WR <= "00000000";						--data to be written (register address)

--		  B_DUMMY <= "10000000";
		
	WHEN 1 =>												--1st busy high: command 1 latched, okay to issue command 2
      B_RW <= '1';										--command 2 is a read
	WHEN 2 =>												--2nd busy high: command 2 latched, okay to issue command 3
      B_RW <= '1';										--command 3 is a read
      IF(B_BUSY = '0') THEN							--indicates data read in command 2 is ready
        I2C_DATA_BUFFER(7 DOWNTO 0) := B_DATA_RD;			--retrieve data from command 2
      END IF;		  
   WHEN 3 =>												--3rd busy high: command 3 latched, okay to issue command 4
      B_RW <= '1';
      IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(15 DOWNTO 8) := B_DATA_RD;
      END IF;		  
   WHEN 4 =>                               	   --4th busy high: command 4 latched, ready to stop
      B_RW <= '1';
		IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(23 DOWNTO 16) := B_DATA_RD;
      END IF;		  
   WHEN 5 =>                                	 	--4th busy high: command 4 latched, ready to stop
      B_RW <= '1';
		IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(31 DOWNTO 24) := B_DATA_RD;		  
      END IF;		  
	WHEN 6 =>												--2nd busy high: command 2 latched, okay to issue command 3
      B_RW <= '1';										--command 3 is a read
      IF(B_BUSY = '0') THEN							--indicates data read in command 2 is ready
        I2C_DATA_BUFFER(39 DOWNTO 32) := B_DATA_RD;			--retrieve data from command 2
      END IF;		  
   WHEN 7 =>												--3rd busy high: command 3 latched, okay to issue command 4
      B_RW <= '1';
      IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(47 DOWNTO 40) := B_DATA_RD;
      END IF;		  
   WHEN 8 =>                               	   --4th busy high: command 4 latched, ready to stop
      B_RW <= '1';
		IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(55 DOWNTO 48) := B_DATA_RD;
      END IF;		  
   WHEN 9 =>                                	 	--4th busy high: command 4 latched, ready to stop
      B_RW <= '1';
		IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(63 DOWNTO 56) := B_DATA_RD;		  
      END IF;
	WHEN 10 =>												--2nd busy high: command 2 latched, okay to issue command 3
      B_RW <= '1';										--command 3 is a read
      IF(B_BUSY = '0') THEN							--indicates data read in command 2 is ready
        I2C_DATA_BUFFER(71 DOWNTO 64) := B_DATA_RD;			--retrieve data from command 2
      END IF;		  
   WHEN 11 =>												--3rd busy high: command 3 latched, okay to issue command 4
      B_RW <= '1';
      IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(79 DOWNTO 72) := B_DATA_RD;
      END IF;		  
   WHEN 12 =>                               	   --4th busy high: command 4 latched, ready to stop
      B_RW <= '1';
		IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(87 DOWNTO 80) := B_DATA_RD;
      END IF;		  
   WHEN 13 =>                                	 	--4th busy high: command 4 latched, ready to stop
      B_RW <= '1';
		IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(95 DOWNTO 88) := B_DATA_RD;		  
      END IF;		
	WHEN 14 =>												--2nd busy high: command 2 latched, okay to issue command 3
      B_RW <= '1';										--command 3 is a read
      IF(B_BUSY = '0') THEN							--indicates data read in command 2 is ready
        I2C_DATA_BUFFER(103 DOWNTO 96) := B_DATA_RD;			--retrieve data from command 2
      END IF;		  
   WHEN 15 =>												--3rd busy high: command 3 latched, okay to issue command 4
      B_RW <= '1';
      IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(111 DOWNTO 104) := B_DATA_RD;
      END IF;		  
   WHEN 16 =>                               	   --4th busy high: command 4 latched, ready to stop
      B_RW <= '1';
		IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(119 DOWNTO 112) := B_DATA_RD;
      END IF;		  
   WHEN 17 =>                                	 	--4th busy high: command 4 latched, ready to stop
      B_RW <= '1';
		IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(127 DOWNTO 120) := B_DATA_RD;		  
      END IF;
   WHEN 18 =>                                	 	--4th busy high: command 4 latched, ready to stop
      B_RW <= '1';
		IF(B_BUSY = '0') THEN
        I2C_DATA_BUFFER(135 DOWNTO 128) := B_DATA_RD;		  
      END IF;
   WHEN 19 =>                                	 	--4th busy high: command 4 latched, ready to stop
      B_RW <= '1';
		IF(B_BUSY = '0') THEN
			I2C_DATA_BUFFER(143 DOWNTO 136) := B_DATA_RD;		  
      END IF;
   WHEN 20 =>                                  	--4th busy high: command 4 latched, ready to stop
      B_ENA <= '0';
      IF(B_BUSY = '0') THEN
			I2C_DATA_BUFFER(151 DOWNTO 144) := B_DATA_RD;			
			busy_cnt := 0;									-- Reset busy_cnt for next transaction
			I2C_ACQ_REQUESTED := '0';					-- Clear Flag
		END IF;

--		B_DUMMY <= "01000000";
	WHEN OTHERS => NULL;
	END CASE;

END IF;														-- End IF I2C_ACQ_REQUESTED = '1' THEN
END IF;														-- End if clk event etc
END IF;														-- End IF B_RESET_IN = '0' THEN

end PROCESS;

--blabla
  
end archi;