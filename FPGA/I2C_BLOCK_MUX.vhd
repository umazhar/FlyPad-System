
LIBRARY ieee;
USE IEEE.STD_LOGIC_1164.ALL;
USE IEEE.STD_LOGIC_UNSIGNED.ALL;

ENTITY I2C_BLOCK_MUX IS

PORT
	(
		-- Input ports
		M_SEL_EXP		: IN  	INTEGER RANGE 0 TO 31;				-- Selection input
		M_DATA_I2C_0	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_1	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_2	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_3	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_4	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_5	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_6	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_7	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_8	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_9	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_10	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_11	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_12	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_13	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_14	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_15	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_16	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_17	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_18	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_19	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_20	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_21	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_22	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_23	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_24	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_25	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_26	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_27	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_28	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_29	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_30	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x
		M_DATA_I2C_31	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	-- 20 bytes data input bus from I2C block x

		-- out ports		
		M_DATA_OUT		: OUT    STD_LOGIC_VECTOR(159 DOWNTO 0)	-- 20 bytes data output bus to USB component
		);
END ENTITY I2C_BLOCK_MUX;	
	
ARCHITECTURE archi OF I2C_BLOCK_MUX IS

BEGIN

	WITH M_SEL_EXP SELECT
		M_DATA_OUT <= 	M_DATA_I2C_0 WHEN 0,
							M_DATA_I2C_1 WHEN 1,
							M_DATA_I2C_2 WHEN 2,
							M_DATA_I2C_3 WHEN 3,
							M_DATA_I2C_4 WHEN 4,
							M_DATA_I2C_5 WHEN 5,
							M_DATA_I2C_6 WHEN 6,
							M_DATA_I2C_7 WHEN 7,
							M_DATA_I2C_8 WHEN 8,
							M_DATA_I2C_9 WHEN 9,
							M_DATA_I2C_10 WHEN 10,
							M_DATA_I2C_11 WHEN 11,
							M_DATA_I2C_12 WHEN 12,
							M_DATA_I2C_13 WHEN 13,
							M_DATA_I2C_14 WHEN 14,
							M_DATA_I2C_15 WHEN 15,
							M_DATA_I2C_16 WHEN 16,
							M_DATA_I2C_17 WHEN 17,
							M_DATA_I2C_18 WHEN 18,
							M_DATA_I2C_19 WHEN 19,
							M_DATA_I2C_20 WHEN 20,
							M_DATA_I2C_21 WHEN 21,
							M_DATA_I2C_22 WHEN 22,
							M_DATA_I2C_23 WHEN 23,
							M_DATA_I2C_24 WHEN 24,
							M_DATA_I2C_25 WHEN 25,
							M_DATA_I2C_26 WHEN 26,
							M_DATA_I2C_27 WHEN 27,
							M_DATA_I2C_28 WHEN 28,
							M_DATA_I2C_29 WHEN 29,
							M_DATA_I2C_30 WHEN 30,
							M_DATA_I2C_31 WHEN 31;
  
end archi;