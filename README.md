

Program that would track a given crypto-currency on your Bittrex Account and place a trailing stop loss.
The program does not actually place a sell order until the price of crypto-currency has fallen below the percentage threshold.
Since this is sensitive, the program would place a log file in its home directory and record every step for debugging and validation purposes. 
Outliers detection functions have been added for protection against flash drops and sudden spikes. 

[The code is open source so you can see all of it and thus verify that it is safe to use]

Instructions:
 1 - Put your API key and API Secret in the start.py file.
 2 - Specify the currency, currency pair (what do you want your currency to trade for), and percentage threshold.
 3 - You can also specify how often do you want the program to check the price.
 4 - Run the program.
 
Future Dev:
 1 - Command Line interface to be added to allow user to specify various parameters.
 2 - Add technical indicators for automated trades such as Moving Averages, Oscillators etc.
 2 - GUI to be developed. 