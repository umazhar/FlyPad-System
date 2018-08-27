
LIBRARY ieee;
USE IEEE.STD_LOGIC_1164.ALL;
USE IEEE.STD_LOGIC_UNSIGNED.ALL;

ENTITY I2C_BLOCK_MUX IS

PORT
	(
		-- Input ports
		M_SEL_EXP		: IN  	INTEGER RANGE 0 TO 15;				-- Selection input
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
							M_DATA_I2C_15 WHEN 15;
end archi;