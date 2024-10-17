-- This file generates syncronization signal for the PMT
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
entity PMT_Controller is
port(

clk: in std_logic;
input1, input2: in std_logic;
output1: out std_logic;
output2: out std_logic

);
end entity PMT_Controller;

architecture calculate_sync of PMT_Controller is

signal toutput1 : std_logic;
signal toutput2 : std_logic;
--constant PulseDuration  :integer    :=500000  --Duration of the sync pulses in number of cycles of the clk
signal c1 : integer range 0 to 50000000 ; -- counter for 50mHz clock Duration of the sync pulses in number of cycles of the clk
signal c2 : integer range 0 to 50000000 ; -- counter for 50mHz clock Duration of the sync pulses in number of cycles of the clk
signal Dout1 : integer range 1 to 10000000; -- clock counter   for output 1 - 5000Hz
signal Dout2 : integer range 1 to 20000000 ; --  clock counter  for output 2  - 1000Hz 

begin

process(clk)

begin
		
if (clk='1' and clk'event) then
			
			Dout1<=Dout1+1;
			Dout2<=Dout2+1;
		
			if  Dout1 < 5000000 then
				toutput1<= '0';
			elsif Dout1 >= 5000000 then
				toutput1 <= '1';
			end if;
			
			if  Dout2 = 1 then
				toutput2<=not toutput2;
			elsif Dout2 = 20000000 then
				Dout2 <= 1;
			end if;
end if;
				
			if (input1='0') then
		
					c1<=c1+1;
		
					if c1 < 50000000 then
						output1<=toutput1;	
						
					elsif c1 = 50000000 then
							c1 <=  0;
					end if;
							
			end if;
			
			if (input2='0') then

					c2<=c2+1;
			
					if c2 < 50000000 THEN
						output2<=toutput2;
						
					elsif c2 = 50000000 then
							c2 <=  0;
					end if;
					
end if;
		

		
		
end process;
end architecture calculate_sync; 