# -*- coding: utf-8 -*-
import time
import schedule
import sys
import os
import logging
import numpy as np

my_api_key = '<Your API Key Here>'
my_api_secret = '<Your APU Secret Here>'

pair = 'USDT-NEO'
myCurrency = 'NEO'
interval_to_check = 10
percentage_threshold = 0.80

from bittrex.bittrex import Bittrex, API_V1_1, API_V2_0
my_bittrex = Bittrex(my_api_key, my_api_secret, api_version = API_V2_0)

def get_rate(pair, position=0):
    r = my_bittrex.get_orderbook(pair)
    buy_book = r['result']['buy']
    if position > 0:
        position = position - 1
    my_rate = buy_book[position]['Rate']
    return my_rate

def get_balance(asset):
    r = my_bittrex.get_balance(asset)
    return r['result']['Balance']
    

def initiate_logger():
    time_format = '%d-%b-%Y_%H-%M-%S'
    report_time = time.strftime(time_format)

    new_dir = 'log_files'
    if not os.path.isdir(new_dir):
        os.makedirs(new_dir)
    
    logging.basicConfig(
                    format='%(asctime)s -- %(message)s',
                    handlers=[logging.StreamHandler(),
                              logging.FileHandler('{}/debug_{}.log'.format(new_dir, report_time))],
                    datefmt=time_format, 
                    level=logging.WARNING, 
                    )
    
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)


r = my_bittrex.trade_buy(
        market=pair, 
        order_type='MARKET',
        quantity = 0.015
        )


r = my_bittrex.trade_buy(
        market=pair, 
        order_type='LIMIT',
        quantity = 0.055,
        rate = get_rate(pair, position=9),
        time_in_effect = 'GOOD_TIL_CANCELLED',
        )

def get_curr_price(pair_):
    """
    Function gets the current price of the currency.
    To resist against flash drops and spikes, function 
        pulls prices at certain interval and averages
        Calculates variance and check if it is too high
    
    
    Parameters:
        pair_ : The pair we want to get the price for. (Price of 2nd in terms of 1st
        Answer the question: How much of 1st currency (in the pair) will I get, for 1 unit of second currency (in the pair).
        
        Example:
            'USDT-NEO'
            'BTC-XRP'
    
    Returns:
        price : Price of 2nd currency in the pair in terms of 1st will be returned.
    
    """
    price_list = []
    for _ in range(5):
       price_list.append(get_rate(pair_))
       time.sleep(1)
    
    price = sum(price_list) / len(price_list)
    
    variance = sum([(x - price) ** 2 for x in price_list]) / len(price_list)
    # np.var(arr) or statistics.pvariance(list) might perform better
    
    if variance > 10:
        logger.debug("Possible outlier in price: {}".format([round(x, 4) for x in price_list]))
        logger.debug("Calculated Mean price: {:.4f}".format(price))
        
    return price_list

def stop_loss_check():
    
    curr_price = get_curr_price(pair)
    logger.debug("Current price is {}".format(curr_price))
    
    if curr_price > prev_price:
        stop_loss_price = curr_price * percentage_threshold
        logger.debug("Stop Loss Price updated to {:.4f}".format(stop_loss_price))
    
    if curr_price <= stop_loss_price:
        my_quantity = get_balance(myCurrency)
		
		# Uncomment the below if you want the trade to be actually placed.
		
#        my_bittrex.trade_buy(
#            market=pair, 
#            order_type='MARKET',
#            quantity = my_quantity,
#            time_in_effect = 'GOOD_TIL_CANCELLED',
#            )
        
        logger.debug("Sold {:.4f} quantity at MARKET.".format(my_quantity))
        sys.exit()
    
    logger.debug("Standing by... ")

	
def is_outlier(points, thresh=3.5):
    """
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    """
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh	
	
def percentile_based_outlier(data, threshold=95):
    diff = (100 - threshold) / 2.0
    minval, maxval = np.percentile(data, [diff, 100 - diff])
    return (data < minval) | (data > maxval)
	
	
if __name__ == '__main__':
    initiate_logger()
    
    logger.debug("Monitoring " + pair)
    
    prev_price = get_curr_price(pair)
    stop_loss_price = prev_price * percentage_threshold
    
    logger.debug("Current price is {:.4f} with stop loss set to: {:.4f}".format(prev_price, stop_loss_price))
    
    schedule.every(interval_to_check).minutes.do(stop_loss_check)
    
    while 1:
        schedule.run_pending()
        time.sleep(1)
    
        
""" Testing """

#r = my_bittrex.get_markets()['result']
#r = my_bittrex.get_balance(myCurrency)
#r = my_bittrex.get_market_history(pair)
#r = my_bittrex.get_currencies()
#r = my_bittrex.get_balances()
#r = my_bittrex.get_wallet_health()
#r = my_bittrex.get_balance_distribution()
        