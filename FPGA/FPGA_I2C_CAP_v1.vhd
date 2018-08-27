-- Top Level Component

LIBRARY	IEEE;
USE		IEEE.STD_LOGIC_1164.ALL;

ENTITY FPGA_I2C_CAP_v1 IS
GENERIC(
  sys_clk_frq : INTEGER   := 50_000_000;				--system clock speed in Hz
  i2c_scl_frq : INTEGER   := 400_000);					--speed the i2c bus (scl) will run at in Hz

port
	(
		-- INPUT ports
		CLK			: IN  	STD_LOGIC;					-- Master Clk
		FTDI_TXE		: IN  	STD_LOGIC;
		FTDI_RXF		: IN  	STD_LOGIC;
		
		-- INOUT ports
		SDA_0			: INOUT STD_LOGIC;
		SCL_0			: INOUT STD_LOGIC;
		SDA_1			: INOUT STD_LOGIC;
		SCL_1			: INOUT STD_LOGIC;
		SDA_2			: INOUT STD_LOGIC;
		SCL_2			: INOUT STD_LOGIC;
		SDA_3			: INOUT STD_LOGIC;
		SCL_3			: INOUT STD_LOGIC;
		SDA_4			: INOUT STD_LOGIC;
		SCL_4			: INOUT STD_LOGIC;
		SDA_5			: INOUT STD_LOGIC;
		SCL_5			: INOUT STD_LOGIC;
		SDA_6			: INOUT STD_LOGIC;
		SCL_6			: INOUT STD_LOGIC;
		SDA_7			: INOUT STD_LOGIC;
		SCL_7			: INOUT STD_LOGIC;
		SDA_8			: INOUT STD_LOGIC;
		SCL_8			: INOUT STD_LOGIC;
		SDA_9			: INOUT STD_LOGIC;
		SCL_9			: INOUT STD_LOGIC;
		SDA_10		: INOUT STD_LOGIC;
		SCL_10		: INOUT STD_LOGIC;
		SDA_11		: INOUT STD_LOGIC;
		SCL_11		: INOUT STD_LOGIC;
		SDA_12		: INOUT STD_LOGIC;
		SCL_12		: INOUT STD_LOGIC;
		SDA_13		: INOUT STD_LOGIC;
		SCL_13		: INOUT STD_LOGIC;
		SDA_14		: INOUT STD_LOGIC;
		SCL_14		: INOUT STD_LOGIC;
		SDA_15		: INOUT STD_LOGIC;
		SCL_15		: INOUT STD_LOGIC;
		
		LED1_0		: OUT STD_LOGIC;
		LED2_0		: OUT STD_LOGIC;
		LED1_1		: OUT STD_LOGIC;
		LED2_1		: OUT STD_LOGIC;
		LED1_2		: OUT STD_LOGIC;
		LED2_2		: OUT STD_LOGIC;
		LED1_3		: OUT STD_LOGIC;
		LED2_3		: OUT STD_LOGIC;
		LED1_4		: OUT STD_LOGIC;
		LED2_4		: OUT STD_LOGIC;
		LED1_5		: OUT STD_LOGIC;
		LED2_5		: OUT STD_LOGIC;
		LED1_6		: OUT STD_LOGIC;
		LED2_6		: OUT STD_LOGIC;
		LED1_7		: OUT STD_LOGIC;
		LED2_7		: OUT STD_LOGIC;
		LED1_8		: OUT STD_LOGIC;
		LED2_8		: OUT STD_LOGIC;
		LED1_9		: OUT STD_LOGIC;
		LED2_9		: OUT STD_LOGIC;
		LED1_10		: OUT STD_LOGIC;
		LED2_10		: OUT STD_LOGIC;
		LED1_11		: OUT STD_LOGIC;
		LED2_11		: OUT STD_LOGIC;
		LED1_12		: OUT STD_LOGIC;
		LED2_12		: OUT STD_LOGIC;
		LED1_13		: OUT STD_LOGIC;
		LED2_13		: OUT STD_LOGIC;
		LED1_14		: OUT STD_LOGIC;
		LED2_14		: OUT STD_LOGIC;
		LED1_15		: OUT STD_LOGIC;
		LED2_15		: OUT STD_LOGIC;
		
		-- OUTPUT ports
		FTDI_RESET	: OUT		STD_LOGIC;		
		FTDI_WR		: OUT		STD_LOGIC;
		FTDI_RD		: OUT		STD_LOGIC;		
		FTDI_DATA	: INOUT	STD_LOGIC_VECTOR (7 downto 0);
		DUMMY			: OUT		STD_LOGIC_VECTOR (7 DOWNTO 0)
	);
end entity FPGA_I2C_CAP_v1;	
	
architecture behav_v1 of FPGA_I2C_CAP_v1 is

-- i2c_master
SIGNAL	S_ENA_0    	 	: STD_LOGIC:='0';
SIGNAL	S_ADDR_0   	 	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_0     	 	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_0	 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_0   		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_0 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_0 	: STD_LOGIC:='0';
SIGNAL	S_ENA_1    	 	: STD_LOGIC:='0';
SIGNAL	S_ADDR_1   	 	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_1     	 	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_1	 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_1   		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_1 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_1 	: STD_LOGIC:='0';
SIGNAL	S_ENA_2    	 	: STD_LOGIC:='0';
SIGNAL	S_ADDR_2   	 	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_2     	 	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_2	 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_2   		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_2 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_2 	: STD_LOGIC:='0';
SIGNAL	S_ENA_3    	 	: STD_LOGIC:='0';
SIGNAL	S_ADDR_3   	 	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_3     	 	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_3	 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_3   		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_3 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_3 	: STD_LOGIC:='0';
SIGNAL	S_ENA_4    	 	: STD_LOGIC:='0';
SIGNAL	S_ADDR_4   	 	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_4     	 	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_4	 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_4   		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_4 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_4 	: STD_LOGIC:='0';
SIGNAL	S_ENA_5    	 	: STD_LOGIC:='0';
SIGNAL	S_ADDR_5   	 	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_5     	 	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_5	 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_5   		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_5 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_5 	: STD_LOGIC:='0';
SIGNAL	S_ENA_6    	 	: STD_LOGIC:='0';
SIGNAL	S_ADDR_6   	 	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_6     	 	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_6	 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_6   		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_6 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_6 	: STD_LOGIC:='0';
SIGNAL	S_ENA_7    	 	: STD_LOGIC:='0';
SIGNAL	S_ADDR_7   	 	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_7     	 	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_7	 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_7   		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_7 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_7 	: STD_LOGIC:='0';
SIGNAL	S_ENA_8    	 	: STD_LOGIC:='0';
SIGNAL	S_ADDR_8   	 	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_8     	 	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_8	 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_8   		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_8 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_8 	: STD_LOGIC:='0';
SIGNAL	S_ENA_9    	 	: STD_LOGIC:='0';
SIGNAL	S_ADDR_9   	 	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_9     	 	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_9	 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_9   		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_9 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_9 	: STD_LOGIC:='0';
SIGNAL	S_ENA_10   	 	: STD_LOGIC:='0';
SIGNAL	S_ADDR_10  	 	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_10    	 	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_10 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_10   	: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_10	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_10 : STD_LOGIC:='0';
SIGNAL	S_ENA_11    	: STD_LOGIC:='0';
SIGNAL	S_ADDR_11   	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_11     	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_11	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_11   	: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_11 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_11 : STD_LOGIC:='0';
SIGNAL	S_ENA_12    	: STD_LOGIC:='0';
SIGNAL	S_ADDR_12   	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_12     	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_12	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_12   	: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_12 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_12 : STD_LOGIC:='0';
SIGNAL	S_ENA_13    	: STD_LOGIC:='0';
SIGNAL	S_ADDR_13   	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_13     	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_13	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_13   	: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_13 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_13 : STD_LOGIC:='0';
SIGNAL	S_ENA_14    	: STD_LOGIC:='0';
SIGNAL	S_ADDR_14   	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_14     	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_14	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_14   	: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_14 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_14 : STD_LOGIC:='0';
SIGNAL	S_ENA_15    	: STD_LOGIC:='0';
SIGNAL	S_ADDR_15   	: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_15     	: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_15	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_15   	: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_15 	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_15 : STD_LOGIC:='0';
SIGNAL	S_ENA_16			: STD_LOGIC:='0';
SIGNAL	S_ADDR_16		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_16			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_16	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_16		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_16	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_16	: STD_LOGIC:='0';
SIGNAL	S_ENA_17			: STD_LOGIC:='0';
SIGNAL	S_ADDR_17		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_17			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_17	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_17		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_17	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_17	: STD_LOGIC:='0';
SIGNAL	S_ENA_18			: STD_LOGIC:='0';
SIGNAL	S_ADDR_18		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_18			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_18	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_18		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_18	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_18	: STD_LOGIC:='0';
SIGNAL	S_ENA_19			: STD_LOGIC:='0';
SIGNAL	S_ADDR_19		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_19			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_19	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_19		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_19	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_19	: STD_LOGIC:='0';
SIGNAL	S_ENA_20			: STD_LOGIC:='0';
SIGNAL	S_ADDR_20		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_20			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_20	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_20		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_20	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_20	: STD_LOGIC:='0';
SIGNAL	S_ENA_21			: STD_LOGIC:='0';
SIGNAL	S_ADDR_21		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_21			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_21	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_21		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_21	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_21	: STD_LOGIC:='0';
SIGNAL	S_ENA_22			: STD_LOGIC:='0';
SIGNAL	S_ADDR_22		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_22			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_22	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_22		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_22	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_22	: STD_LOGIC:='0';
SIGNAL	S_ENA_23			: STD_LOGIC:='0';
SIGNAL	S_ADDR_23		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_23			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_23	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_23		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_23	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_23	: STD_LOGIC:='0';
SIGNAL	S_ENA_24			: STD_LOGIC:='0';
SIGNAL	S_ADDR_24		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_24			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_24	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_24		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_24	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_24	: STD_LOGIC:='0';
SIGNAL	S_ENA_25			: STD_LOGIC:='0';
SIGNAL	S_ADDR_25		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_25			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_25	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_25		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_25	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_25	: STD_LOGIC:='0';
SIGNAL	S_ENA_26			: STD_LOGIC:='0';
SIGNAL	S_ADDR_26		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_26			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_26	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_26		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_26	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_26	: STD_LOGIC:='0';
SIGNAL	S_ENA_27			: STD_LOGIC:='0';
SIGNAL	S_ADDR_27		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_27			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_27	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_27		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_27	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_27	: STD_LOGIC:='0';
SIGNAL	S_ENA_28			: STD_LOGIC:='0';
SIGNAL	S_ADDR_28		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_28			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_28	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_28		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_28	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_28	: STD_LOGIC:='0';
SIGNAL	S_ENA_29			: STD_LOGIC:='0';
SIGNAL	S_ADDR_29		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_29			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_29	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_29		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_29	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_29	: STD_LOGIC:='0';
SIGNAL	S_ENA_30			: STD_LOGIC:='0';
SIGNAL	S_ADDR_30		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_30			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_30	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_30		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_30	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_30	: STD_LOGIC:='0';
SIGNAL	S_ENA_31			: STD_LOGIC:='0';
SIGNAL	S_ADDR_31		: STD_LOGIC_VECTOR(6 DOWNTO 0):=(others=>'0');
SIGNAL	S_RW_31			: STD_LOGIC:='0';
SIGNAL	S_DATA_WR_31	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_BUSY_31		: STD_LOGIC:='0';
SIGNAL	S_DATA_RD_31	: STD_LOGIC_VECTOR(7 DOWNTO 0):=(others=>'0');
SIGNAL	S_ACK_ERROR_31	: STD_LOGIC:='0';

-- I2C_BLOCK_MUX
SIGNAL	S_SEL_EXP		: INTEGER RANGE 0 TO 63	:= 0;

SIGNAL	S_DATA_I2C_0	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_1	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_2	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_3	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_4	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_5	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_6	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_7	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_8	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_9	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_10	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_11	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_12	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_13	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_14	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_15	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_16	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_17	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_18	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_19	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_20	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_21	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_22	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_23	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_24	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_25	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_26	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_27	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_28	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_29	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_30	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_I2C_31	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');

SIGNAL	LP_DATA_0	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_1	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_2	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_3	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_4	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_5	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_6	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_7	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_8	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_9	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_10	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_11	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_12	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_13	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_14	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_15	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_16	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_17	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_18	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_19	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_20	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_21	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_22	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_23	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_24	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_25	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_26	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_27	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_28	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_29	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_30	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_31	: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');
SIGNAL	LP_DATA_OUT		: STD_LOGIC_VECTOR(159 DOWNTO 0):=(others=>'0');


-- I2C_CH_SCHED
SIGNAL	S_USB_DATA_SENT		: STD_LOGIC := '0';
SIGNAL	S_MASTER_RESET			: STD_LOGIC := '0';
SIGNAL	S_I2C_ACQ_REQ			: STD_LOGIC := '0';
SIGNAL	S_I2C_LP_REQ			: STD_LOGIC	:=	'0';
SIGNAL	S_USB_SEND_REQ			: STD_LOGIC := '0';
SIGNAL	S_RCVD_DATA				: STD_LOGIC_VECTOR(87 DOWNTO 0):=(others=>'0');
SIGNAL	S_DATA_RCVD_FLAG		: STD_LOGIC := '0';
SIGNAL	S_RCV_ENABLE			: STD_LOGIC := '0';

-- USB_IF_SEND
-- None left

-- I2C_USB_BRIDGE
-- None left

--declare i2c master component
COMPONENT i2c_master
   GENERIC(
      input_clk : INTEGER;  --input clock speed from user logic in Hz
      bus_clk   : INTEGER); --speed the i2c bus (scl) will run at in Hz
	PORT(
      clk       : IN     STD_LOGIC;                    --system clock
      reset_n   : IN     STD_LOGIC;                    --active low reset
      ena       : IN     STD_LOGIC;                    --latch in command
      addr      : IN     STD_LOGIC_VECTOR(6 DOWNTO 0); --address of target slave
      rw        : IN     STD_LOGIC;                    --'0' is write, '1' is read
      data_wr   : IN     STD_LOGIC_VECTOR(7 DOWNTO 0); --data to write to slave
      busy      : OUT    STD_LOGIC;                    --indicates transaction in progress
      data_rd   : OUT    STD_LOGIC_VECTOR(7 DOWNTO 0); --data read from slave
      ack_error : BUFFER STD_LOGIC;                    --flag if improper acknowledge from slave
      sda       : INOUT  STD_LOGIC;                    --serial data OUTput of i2c bus
      scl       : INOUT  STD_LOGIC);                   --serial clock OUTput of i2c bus
END COMPONENT i2c_master;

--declare the lighting control component
COMPONENT LIGHTING_CONTROL
PORT
	(
				-- Input ports
		INPUT_SIGNAL	: IN    	STD_LOGIC_VECTOR(159 DOWNTO 0);	--arbitrary input vector...
		LP_I2C_LP_REQ	:	IN		STD_LOGIC;
		-- Output ports
		LIGHTING_VAL_1	:	OUT	STD_LOGIC;
		LIGHTING_VAL_2	:	OUT	STD_LOGIC;
		OUTPUT_SIGNAL	: OUT		STD_LOGIC_VECTOR(159 DOWNTO 0)
	);
END COMPONENT LIGHTING_CONTROL;

--declare I2C_BLOCK_MUX component
COMPONENT I2C_BLOCK_MUX
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
		-- OUT ports		
		M_DATA_OUT		: OUT    STD_LOGIC_VECTOR(159 DOWNTO 0)	-- 20 bytes data OUTput bus to USB component
		);
END COMPONENT I2C_BLOCK_MUX;

COMPONENT I2C_CH_SCHED IS
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
END COMPONENT I2C_CH_SCHED;	

--declare USB IF send component
COMPONENT USB_IF_SEND
PORT
	(
		-- Input ports
		USB_CLK			: IN  STD_LOGIC;
		USB_TXE			: IN  STD_LOGIC;																		-- USB send FIFO Full
		USB_DATA	     	: IN	STD_LOGIC_VECTOR (159 downto 0);											-- Data from bridge to write on USB
		USB_SEND     	: IN	STD_LOGIC;																		-- Request USB Data send
		USB_RESET		: IN	STD_LOGIC;
		-- inout ports
		USB_FTDI_DATA	: INOUT STD_LOGIC_VECTOR (7 downto 0);											-- Data to pass to FTDI
		-- out ports		
		USB_WR			: OUT STD_LOGIC;																		-- FTDI Write request
		USB_SENT     	: OUT	STD_LOGIC
		);
END COMPONENT USB_IF_SEND;	

--declare USB IF receive component
COMPONENT USB_IF_RCV
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
--B_DUMMY   	  : OUT		STD_LOGIC_VECTOR (7 DOWNTO 0);
		RCV_DATA_RCVD_FLAG 	: OUT	STD_LOGIC																-- USB Data received flag to the scheduler
		);
END COMPONENT USB_IF_RCV;

--declare USB I2C bridge component
COMPONENT I2C_USB_BRIDGE
PORT
	(
		-- Input ports
		B_CLK				: IN  	STD_LOGIC;								-- Master Clk
		B_RESET_IN		: IN  	STD_LOGIC;								-- Reset		
		B_I2C_ACQ_REQ	: IN  	STD_LOGIC;								-- 100Hz IÂ²C acquisition request clock		
		B_BUSY     		: IN    	STD_LOGIC;                    	-- I2C indicates transaction in progress
		B_DATA_RD 	 	: IN    	STD_LOGIC_VECTOR(7 DOWNTO 0); 	-- I2C data read from slave
		B_CHANNEL_ID	: IN    	STD_LOGIC_VECTOR(7 DOWNTO 0); 	-- Sensor Channel Id		
		
		-- OUT ports		
		B_ENA   	  	: OUT    STD_LOGIC;              	      	-- I2C latch in command
		B_ADDR     	: OUT    STD_LOGIC_VECTOR(6 DOWNTO 0);	 		-- I2C address of target slave
		B_RW       	: OUT    STD_LOGIC;                    		-- I2C '0' is write, '1' is read
		B_DATA_WR  	: OUT    STD_LOGIC_VECTOR(7 DOWNTO 0); 		-- I2C data to write to slave
		B_DATA     	: OUT		STD_LOGIC_VECTOR (159 downto 0);		-- Data to write on USB
		B_ACK_ERR 	: BUFFER STD_LOGIC                    			-- I2C flag if improper acknowledge from slave
		);
END COMPONENT I2C_USB_BRIDGE;	  

BEGIN

--instantiate i2c_master
i2c_master_0:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_0,
					addr			=> S_ADDR_0,
					rw 			=> S_RW_0,
					data_wr		=> S_DATA_WR_0,
					busy			=> S_BUSY_0,
					data_rd		=> S_DATA_RD_0,
					ack_error	=> S_ACK_ERROR_0,
					sda			=> SDA_0,
					scl			=> SCL_0);

i2c_master_1:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_1,
					addr			=> S_ADDR_1,
					rw 			=> S_RW_1,
					data_wr		=> S_DATA_WR_1,
					busy			=> S_BUSY_1,
					data_rd		=> S_DATA_RD_1,
					ack_error	=> S_ACK_ERROR_1,
					sda			=> SDA_1,
					scl			=> SCL_1);

i2c_master_2:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_2,
					addr			=> S_ADDR_2,
					rw 			=> S_RW_2,
					data_wr		=> S_DATA_WR_2,
					busy			=> S_BUSY_2,
					data_rd		=> S_DATA_RD_2,
					ack_error	=> S_ACK_ERROR_2,
					sda			=> SDA_2,
					scl			=> SCL_2);

i2c_master_3:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_3,
					addr			=> S_ADDR_3,
					rw 			=> S_RW_3,
					data_wr		=> S_DATA_WR_3,
					busy			=> S_BUSY_3,
					data_rd		=> S_DATA_RD_3,
					ack_error	=> S_ACK_ERROR_3,
					sda			=> SDA_3,
					scl			=> SCL_3);
					
i2c_master_4:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_4,
					addr			=> S_ADDR_4,
					rw 			=> S_RW_4,
					data_wr		=> S_DATA_WR_4,
					busy			=> S_BUSY_4,
					data_rd		=> S_DATA_RD_4,
					ack_error	=> S_ACK_ERROR_4,
					sda			=> SDA_4,
					scl			=> SCL_4);

i2c_master_5:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_5,
					addr			=> S_ADDR_5,
					rw 			=> S_RW_5,
					data_wr		=> S_DATA_WR_5,
					busy			=> S_BUSY_5,
					data_rd		=> S_DATA_RD_5,
					ack_error	=> S_ACK_ERROR_5,
					sda			=> SDA_5,
					scl			=> SCL_5);

i2c_master_6:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_6,
					addr			=> S_ADDR_6,
					rw 			=> S_RW_6,
					data_wr		=> S_DATA_WR_6,
					busy			=> S_BUSY_6,
					data_rd		=> S_DATA_RD_6,
					ack_error	=> S_ACK_ERROR_6,
					sda			=> SDA_6,
					scl			=> SCL_6);

i2c_master_7:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_7,
					addr			=> S_ADDR_7,
					rw 			=> S_RW_7,
					data_wr		=> S_DATA_WR_7,
					busy			=> S_BUSY_7,
					data_rd		=> S_DATA_RD_7,
					ack_error	=> S_ACK_ERROR_7,
					sda			=> SDA_7,
					scl			=> SCL_7);

i2c_master_8:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_8,
					addr			=> S_ADDR_8,
					rw 			=> S_RW_8,
					data_wr		=> S_DATA_WR_8,
					busy			=> S_BUSY_8,
					data_rd		=> S_DATA_RD_8,
					ack_error	=> S_ACK_ERROR_8,
					sda			=> SDA_8,
					scl			=> SCL_8);

i2c_master_9:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_9,
					addr			=> S_ADDR_9,
					rw 			=> S_RW_9,
					data_wr		=> S_DATA_WR_9,
					busy			=> S_BUSY_9,
					data_rd		=> S_DATA_RD_9,
					ack_error	=> S_ACK_ERROR_9,
					sda			=> SDA_9,
					scl			=> SCL_9);

i2c_master_10:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_10,
					addr			=> S_ADDR_10,
					rw 			=> S_RW_10,
					data_wr		=> S_DATA_WR_10,
					busy			=> S_BUSY_10,
					data_rd		=> S_DATA_RD_10,
					ack_error	=> S_ACK_ERROR_10,
					sda			=> SDA_10,
					scl			=> SCL_10);

i2c_master_11:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_11,
					addr			=> S_ADDR_11,
					rw 			=> S_RW_11,
					data_wr		=> S_DATA_WR_11,
					busy			=> S_BUSY_11,
					data_rd		=> S_DATA_RD_11,
					ack_error	=> S_ACK_ERROR_11,
					sda			=> SDA_11,
					scl			=> SCL_11);
					
i2c_master_12:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_12,
					addr			=> S_ADDR_12,
					rw 			=> S_RW_12,
					data_wr		=> S_DATA_WR_12,
					busy			=> S_BUSY_12,
					data_rd		=> S_DATA_RD_12,
					ack_error	=> S_ACK_ERROR_12,
					sda			=> SDA_12,
					scl			=> SCL_12);

i2c_master_13:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_13,
					addr			=> S_ADDR_13,
					rw 			=> S_RW_13,
					data_wr		=> S_DATA_WR_13,
					busy			=> S_BUSY_13,
					data_rd		=> S_DATA_RD_13,
					ack_error	=> S_ACK_ERROR_13,
					sda			=> SDA_13,
					scl			=> SCL_13);

i2c_master_14:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_14,
					addr			=> S_ADDR_14,
					rw 			=> S_RW_14,
					data_wr		=> S_DATA_WR_14,
					busy			=> S_BUSY_14,
					data_rd		=> S_DATA_RD_14,
					ack_error	=> S_ACK_ERROR_14,
					sda			=> SDA_14,
					scl			=> SCL_14);

i2c_master_15:	i2c_master
	GENERIC MAP(input_clk	=> sys_clk_frq,
					bus_clk		=> i2c_scl_frq)
						
	PORT MAP(	clk			=> CLK,
					reset_n		=> S_MASTER_RESET,
					ena			=> S_ENA_15,
					addr			=> S_ADDR_15,
					rw 			=> S_RW_15,
					data_wr		=> S_DATA_WR_15,
					busy			=> S_BUSY_15,
					data_rd		=> S_DATA_RD_15,
					ack_error	=> S_ACK_ERROR_15,
					sda			=> SDA_15,
					scl			=> SCL_15);

--instantiate I2C_USB_BRIDGE
I2C_USB_BRIDGE_0:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_0,
					B_DATA_RD 		=> S_DATA_RD_0,
					B_CHANNEL_ID	=> "00010000",
					B_ENA 			=> S_ENA_0,
					B_ADDR	 		=> S_ADDR_0,
					B_RW 				=> S_RW_0,
					B_DATA_WR	 	=> S_DATA_WR_0,
					B_DATA 			=> S_DATA_I2C_0,
					B_ACK_ERR		=> S_ACK_ERROR_0);
					
I2C_USB_BRIDGE_1:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_1,
					B_DATA_RD 		=> S_DATA_RD_1,
					B_CHANNEL_ID	=> "00010001",
					B_ENA 			=> S_ENA_1,
					B_ADDR	 		=> S_ADDR_1,
					B_RW 				=> S_RW_1,
					B_DATA_WR	 	=> S_DATA_WR_1,
					B_DATA 			=> S_DATA_I2C_1,
					B_ACK_ERR		=> S_ACK_ERROR_1);
					
I2C_USB_BRIDGE_2:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_2,
					B_DATA_RD 		=> S_DATA_RD_2,
					B_CHANNEL_ID	=> "00010010",
					B_ENA 			=> S_ENA_2,
					B_ADDR	 		=> S_ADDR_2,
					B_RW 				=> S_RW_2,
					B_DATA_WR	 	=> S_DATA_WR_2,
					B_DATA 			=> S_DATA_I2C_2,
					B_ACK_ERR		=> S_ACK_ERROR_2);

I2C_USB_BRIDGE_3:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_3,
					B_DATA_RD 		=> S_DATA_RD_3,
					B_CHANNEL_ID	=> "00010011",
					B_ENA 			=> S_ENA_3,
					B_ADDR	 		=> S_ADDR_3,
					B_RW 				=> S_RW_3,
					B_DATA_WR	 	=> S_DATA_WR_3,
					B_DATA 			=> S_DATA_I2C_3,
					B_ACK_ERR		=> S_ACK_ERROR_3);

I2C_USB_BRIDGE_4:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_4,
					B_DATA_RD 		=> S_DATA_RD_4,
					B_CHANNEL_ID	=> "00010100",
					B_ENA 			=> S_ENA_4,
					B_ADDR	 		=> S_ADDR_4,
					B_RW 				=> S_RW_4,
					B_DATA_WR	 	=> S_DATA_WR_4,
					B_DATA 			=> S_DATA_I2C_4,
					B_ACK_ERR		=> S_ACK_ERROR_4);
					
I2C_USB_BRIDGE_5:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_5,
					B_DATA_RD 		=> S_DATA_RD_5,
					B_CHANNEL_ID	=> "00010101",
					B_ENA 			=> S_ENA_5,
					B_ADDR	 		=> S_ADDR_5,
					B_RW 				=> S_RW_5,
					B_DATA_WR	 	=> S_DATA_WR_5,
					B_DATA 			=> S_DATA_I2C_5,
					B_ACK_ERR		=> S_ACK_ERROR_5);
					
I2C_USB_BRIDGE_6:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_6,
					B_DATA_RD 		=> S_DATA_RD_6,
					B_CHANNEL_ID	=> "00010110",
					B_ENA 			=> S_ENA_6,
					B_ADDR	 		=> S_ADDR_6,
					B_RW 				=> S_RW_6,
					B_DATA_WR	 	=> S_DATA_WR_6,
					B_DATA 			=> S_DATA_I2C_6,
					B_ACK_ERR		=> S_ACK_ERROR_6);

I2C_USB_BRIDGE_7:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_7,
					B_DATA_RD 		=> S_DATA_RD_7,
					B_CHANNEL_ID	=> "00010111",
					B_ENA 			=> S_ENA_7,
					B_ADDR	 		=> S_ADDR_7,
					B_RW 				=> S_RW_7,
					B_DATA_WR	 	=> S_DATA_WR_7,
					B_DATA 			=> S_DATA_I2C_7,
					B_ACK_ERR		=> S_ACK_ERROR_7);
					
I2C_USB_BRIDGE_8:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_8,
					B_DATA_RD 		=> S_DATA_RD_8,
					B_CHANNEL_ID	=> "00011000",
					B_ENA 			=> S_ENA_8,
					B_ADDR	 		=> S_ADDR_8,
					B_RW 				=> S_RW_8,
					B_DATA_WR	 	=> S_DATA_WR_8,
					B_DATA 			=> S_DATA_I2C_8,
					B_ACK_ERR		=> S_ACK_ERROR_8);
					
I2C_USB_BRIDGE_9:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_9,
					B_DATA_RD 		=> S_DATA_RD_9,
					B_CHANNEL_ID	=> "00011001",
					B_ENA 			=> S_ENA_9,
					B_ADDR	 		=> S_ADDR_9,
					B_RW 				=> S_RW_9,
					B_DATA_WR	 	=> S_DATA_WR_9,
					B_DATA 			=> S_DATA_I2C_9,
					B_ACK_ERR		=> S_ACK_ERROR_9);
					
I2C_USB_BRIDGE_10:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_10,
					B_DATA_RD 		=> S_DATA_RD_10,
					B_CHANNEL_ID	=> "00011010",
					B_ENA 			=> S_ENA_10,
					B_ADDR	 		=> S_ADDR_10,
					B_RW 				=> S_RW_10,
					B_DATA_WR	 	=> S_DATA_WR_10,
					B_DATA 			=> S_DATA_I2C_10,
					B_ACK_ERR		=> S_ACK_ERROR_10);

I2C_USB_BRIDGE_11:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_11,
					B_DATA_RD 		=> S_DATA_RD_11,
					B_CHANNEL_ID	=> "00011011",
					B_ENA 			=> S_ENA_11,
					B_ADDR	 		=> S_ADDR_11,
					B_RW 				=> S_RW_11,
					B_DATA_WR	 	=> S_DATA_WR_11,
					B_DATA 			=> S_DATA_I2C_11,
					B_ACK_ERR		=> S_ACK_ERROR_11);

I2C_USB_BRIDGE_12:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_12,
					B_DATA_RD 		=> S_DATA_RD_12,
					B_CHANNEL_ID	=> "00011100",
					B_ENA 			=> S_ENA_12,
					B_ADDR	 		=> S_ADDR_12,
					B_RW 				=> S_RW_12,
					B_DATA_WR	 	=> S_DATA_WR_12,
					B_DATA 			=> S_DATA_I2C_12,
					B_ACK_ERR		=> S_ACK_ERROR_12);
					
I2C_USB_BRIDGE_13:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_13,
					B_DATA_RD 		=> S_DATA_RD_13,
					B_CHANNEL_ID	=> "00011101",
					B_ENA 			=> S_ENA_13,
					B_ADDR	 		=> S_ADDR_13,
					B_RW 				=> S_RW_13,
					B_DATA_WR	 	=> S_DATA_WR_13,
					B_DATA 			=> S_DATA_I2C_13,
					B_ACK_ERR		=> S_ACK_ERROR_13);
					
I2C_USB_BRIDGE_14:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_14,
					B_DATA_RD 		=> S_DATA_RD_14,
					B_CHANNEL_ID	=> "00011110",
					B_ENA 			=> S_ENA_14,
					B_ADDR	 		=> S_ADDR_14,
					B_RW 				=> S_RW_14,
					B_DATA_WR	 	=> S_DATA_WR_14,
					B_DATA 			=> S_DATA_I2C_14,
					B_ACK_ERR		=> S_ACK_ERROR_14);

I2C_USB_BRIDGE_15:	I2C_USB_BRIDGE
	PORT MAP(	B_CLK				=> CLK,
					B_RESET_IN		=> S_MASTER_RESET,
					B_I2C_ACQ_REQ	=> S_I2C_ACQ_REQ,
					B_BUSY 			=> S_BUSY_15,
					B_DATA_RD 		=> S_DATA_RD_15,
					B_CHANNEL_ID	=> "00011111",
					B_ENA 			=> S_ENA_15,
					B_ADDR	 		=> S_ADDR_15,
					B_RW 				=> S_RW_15,
					B_DATA_WR	 	=> S_DATA_WR_15,
					B_DATA 			=> S_DATA_I2C_15,
					B_ACK_ERR		=> S_ACK_ERROR_15);
										
LIGHTING_PROCESSING_0:  LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_0,
OUTPUT_SIGNAL => LP_DATA_0,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_0,
LIGHTING_VAL_2 => LED2_0);

LIGHTING_PROCESSING_1:  LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_1,
OUTPUT_SIGNAL => LP_DATA_1,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_1,
LIGHTING_VAL_2 => LED2_1);

LIGHTING_PROCESSING_2:  LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_2,
OUTPUT_SIGNAL => LP_DATA_2,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_2,
LIGHTING_VAL_2 => LED2_2);

LIGHTING_PROCESSING_3:  LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_3,
OUTPUT_SIGNAL => LP_DATA_3,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_3,
LIGHTING_VAL_2 => LED2_3);

LIGHTING_PROCESSING_4:  LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_4,
OUTPUT_SIGNAL => LP_DATA_4,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_4,
LIGHTING_VAL_2 => LED2_4);

LIGHTING_PROCESSING_5:  LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_5,
OUTPUT_SIGNAL => LP_DATA_5,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_5,
LIGHTING_VAL_2 => LED2_5);

LIGHTING_PROCESSING_6:  LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_6,
OUTPUT_SIGNAL => LP_DATA_6,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_6,
LIGHTING_VAL_2 => LED2_6);

LIGHTING_PROCESSING_7:  LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_7,
OUTPUT_SIGNAL => LP_DATA_7,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_7,
LIGHTING_VAL_2 => LED2_7);

LIGHTING_PROCESSING_8:  LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_8,
OUTPUT_SIGNAL => LP_DATA_8,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_8,
LIGHTING_VAL_2 => LED2_8);

LIGHTING_PROCESSING_9:  LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_9,
OUTPUT_SIGNAL => LP_DATA_9,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_9,
LIGHTING_VAL_2 => LED2_9);

LIGHTING_PROCESSING_10: LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_10,
OUTPUT_SIGNAL => LP_DATA_10,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_10,
LIGHTING_VAL_2 => LED2_10);

LIGHTING_PROCESSING_11: LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_11,
OUTPUT_SIGNAL => LP_DATA_11,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_11,
LIGHTING_VAL_2 => LED2_11);

LIGHTING_PROCESSING_12: LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_12,
OUTPUT_SIGNAL => LP_DATA_12,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_12,
LIGHTING_VAL_2 => LED2_12);

LIGHTING_PROCESSING_13: LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_13,
OUTPUT_SIGNAL => LP_DATA_13,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_13,
LIGHTING_VAL_2 => LED2_13);

LIGHTING_PROCESSING_14: LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_14,
OUTPUT_SIGNAL => LP_DATA_14,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_14,
LIGHTING_VAL_2 => LED2_14);

LIGHTING_PROCESSING_15: LIGHTING_CONTROL PORT MAP(
INPUT_SIGNAL => S_DATA_I2C_15,
OUTPUT_SIGNAL => LP_DATA_15,
LP_I2C_LP_REQ	=> S_I2C_LP_REQ,
LIGHTING_VAL_1 => LED1_15,
LIGHTING_VAL_2 => LED2_15);
						
--instantiate I2C_BLOCK_MUX
I2C_BLOCK_MUX_0:		I2C_BLOCK_MUX
	PORT MAP(	M_SEL_EXP		=>	S_SEL_EXP,
					M_DATA_I2C_0	=>	LP_DATA_0,
					M_DATA_I2C_1	=>	LP_DATA_1,
					M_DATA_I2C_2	=>	LP_DATA_2,
					M_DATA_I2C_3	=>	LP_DATA_3,
					M_DATA_I2C_4	=>	LP_DATA_4,
					M_DATA_I2C_5	=>	LP_DATA_5,
					M_DATA_I2C_6	=>	LP_DATA_6,
					M_DATA_I2C_7	=>	LP_DATA_7,
					M_DATA_I2C_8	=>	LP_DATA_8,
					M_DATA_I2C_9	=>	LP_DATA_9,
					M_DATA_I2C_10	=>	LP_DATA_10,
					M_DATA_I2C_11	=>	LP_DATA_11,
					M_DATA_I2C_12	=>	LP_DATA_12,
					M_DATA_I2C_13	=>	LP_DATA_13,
					M_DATA_I2C_14	=>	LP_DATA_14,
					M_DATA_I2C_15	=>	LP_DATA_15,
					M_DATA_OUT		=>	LP_DATA_OUT);

--instantiate I2C_CH_SCHED
I2C_CH_SCHED_0:I2C_CH_SCHED
	PORT MAP(	SCH_CLK					=>	CLK,
					SCH_USB_DATA_SENT		=>	S_USB_DATA_SENT,
					SCH_MASTER_RESET		=>	S_MASTER_RESET,
					SCH_I2C_ACQ_REQ		=>	S_I2C_ACQ_REQ,
					SCH_LP_REQ				=> S_I2C_LP_REQ,
					SCH_SEL_EXP				=>	S_SEL_EXP,
					SCH_USB_SEND_REQ		=>	S_USB_SEND_REQ,
					SCH_FTDI_RESET			=> FTDI_RESET,
					SCH_RCVD_DATA			=> S_RCVD_DATA,
					SCH_DATA_RCVD_FLAG	=>	S_DATA_RCVD_FLAG,
					SCH_RCV_ENABLE			=> S_RCV_ENABLE,			
					B_DUMMY					=> DUMMY);
						
--instantiate USB_IF_SEND
USB_IF_SEND_0:	USB_IF_SEND
	PORT MAP(	USB_CLK				=> CLK,
					USB_TXE 				=> FTDI_TXE,
					USB_DATA 			=> LP_DATA_OUT,
					USB_SEND 			=> S_USB_SEND_REQ,
					USB_RESET			=> S_MASTER_RESET,
					USB_FTDI_DATA 		=> FTDI_DATA,
					USB_WR 				=> FTDI_WR,
					USB_SENT 			=>	S_USB_DATA_SENT);
					
--instantiate USB_IF_RCV
USB_IF_RCV_0:	USB_IF_RCV
	PORT MAP(	RCV_CLK					=> CLK,
					RCV_RESET				=> S_MASTER_RESET,
					RCV_RXF 					=> FTDI_RXF,
					RCV_ENABLE				=> S_RCV_ENABLE,
					RCV_RCVD_DATA			=> S_RCVD_DATA,
					RCV_FTDI_DATA 			=> FTDI_DATA,
					RCV_RD 					=> FTDI_RD,
					RCV_DATA_RCVD_FLAG	=>	S_DATA_RCVD_FLAG
--					B_DUMMY					=> DUMMY
					);
     
end behav_v1;