
library ieee;
use ieee.std_logic_1164.all;

entity I2C_SWITCH is
PORT
	(
		-- Input ports
		SW_CLK			: IN  STD_LOGIC;		
		SW_SW_SELECT	: IN	STD_LOGIC_VECTOR (7 DOWNTO 0);	-- I2C line switch selection
		-- Inout ports
		SW_SDA		: inout std_logic;      							-- I2C lines from internal component
		SW_SCL		: inout std_logic;      							-- I2C lines from internal component
		SW_SDA_1		: inout std_logic;      							-- I2C lines to external world
		SW_SCL_1		: inout std_logic;	
		SW_SDA_2		: inout std_logic;
		SW_SCL_2		: inout std_logic;	
		SW_SDA_3		: inout std_logic;
		SW_SCL_3		: inout std_logic;	
		SW_SDA_4		: inout std_logic;
		SW_SCL_4		: inout std_logic;
		SW_SDA_5		: inout std_logic;
		SW_SCL_5		: inout std_logic;	
		SW_SDA_6		: inout std_logic;
		SW_SCL_6		: inout std_logic;	
		SW_SDA_7		: inout std_logic;
		SW_SCL_7		: inout std_logic;	
		SW_SDA_8		: inout std_logic;
		SW_SCL_8		: inout std_logic;	
		SW_SDA_9		: inout std_logic;
		SW_SCL_9		: inout std_logic;	
		SW_SDA_10	: inout std_logic;
		SW_SCL_10	: inout std_logic		
		);
END entity I2C_SWITCH;

architecture archi of I2C_SWITCH is

begin

PROCESS(SW_CLK)				 

BEGIN

-- Input and Output Switch

end PROCESS;
  
end archi;