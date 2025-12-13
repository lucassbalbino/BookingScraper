from scrape import  cookie_pass, delete_all_cookies, get_driver, load_flexible_dates
import time


#https = 'https://www.booking.com/hotel/br/ibis-budget-campo-grande.pt-br.html?aid=397594&label=gog235jc-1FCAEoggI46AdIH1gDaLsBiAEBmAEfuAEXyAEM2AEB6AEB-AECiAIBqAIDuAKC29rCBsACAdICJGY2OTcyNGZkLWI4YzktNDUwNy1iODVhLTEzMTJkZTI5ODk3ZdgCBeACAQ&sid=6bcf1fae832f847c2bd5da968421d99e&all_sr_blocks=231122403_100039428_2_2_0_794101&checkin=2025-07-21&checkout=2025-07-22&dest_id=-634091&dest_type=city&dist=0&group_adults=2&group_children=0&hapos=3&highlighted_blocks=231122403_100039428_2_2_0_794101&hpos=3&matching_block_id=231122403_100039428_2_2_0_794101&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA&sb_price_type=total&sr_order=popularity&sr_pri_blocks=231122403_100039428_2_2_0_794101_18900&srepoch=1751048867&srpvid=9201637d954f0870&type=total&ucfs=1&'

#https = 'https://www.booking.com/hotel/br/loft-no-e-suites-campos.pt-br.html?aid=304142&label=gen173nr-1FCAQoggJCCHJlZ2lvbl9YSC1YBGi7AYgBAZgBLbgBF8gBDNgBAegBAfgBA4gCAagCA7gCgNnFwwbAAgHSAiQ1ODcyOWRmZi1lNTE1LTQwNjgtOGQ4Yi1mMmI3N2U2NjliMDnYAgXgAgE&sid=13bf16c24383479127147c48e3e559f1&all_sr_blocks=911579701_362470946_2_2_0&checkin=2025-08-23&checkout=2025-08-27&dist=0&group_adults=1&group_children=0&hapos=30&highlighted_blocks=911579701_362470946_2_2_0&hpos=5&matching_block_id=911579701_362470946_2_2_0&no_rooms=1&req_adults=1&req_children=0&room1=A&sb_price_type=total&sr_order=popularity&sr_pri_blocks=911579701_362470946_2_2_0__91800&srepoch=1752263816&srpvid=43008c4046540305&type=total&ucfs=1&'

#https = 'https://www.booking.com/hotel/br/apartamento-confortavel-campo-grande.pt-pt.html?aid=397594&label=gog235jc-1FCAEoggI46AdIH1gDaLsBiAEBmAEfuAEXyAEM2AEB6AEB-AECiAIBqAIDuAKC29rCBsACAdICJGY2OTcyNGZkLWI4YzktNDUwNy1iODVhLTEzMTJkZTI5ODk3ZdgCBeACAQ&sid=6bcf1fae832f847c2bd5da968421d99e&all_sr_blocks=1242178501_406100849_2_0_0&checkin=2025-07-21&checkout=2025-07-22&dest_id=-634091&dest_type=city&dist=0&group_adults=2&group_children=0&hapos=29&highlighted_blocks=1242178501_406100849_2_0_0&hpos=4&matching_block_id=1242178501_406100849_2_0_0&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA&sb_price_type=total&sr_order=popularity&sr_pri_blocks=1242178501_406100849_2_0_0__13300&srepoch=1751398746&srpvid=383299c391b906ef&type=total&ucfs=1&'

https = 'https://www.booking.com/searchresults.pt-br.html?label=gog235jc-1FCAEoggI46AdIH1gDaLsBiAEBmAEfuAEXyAEM2AEB6AEB-AECiAIBqAIDuAKC29rCBsACAdICJGY2OTcyNGZkLWI4YzktNDUwNy1iODVhLTEzMTJkZTI5ODk3ZdgCBeACAQ&sid=6bcf1fae832f847c2bd5da968421d99e&aid=397594&checkin=2025-07-21&checkout=2025-07-22&dest_id=648&dest_type=region&srpvid=607c6a9f0ee3a2b68a3675c95b50e9bf&ss=mato-grosso-do-sul'
driver = get_driver()

driver.get(https)
#time.sleep(2000)
cookie_pass(driver, https)

delete_all_cookies(driver)

load_flexible_dates(driver)

time.sleep(2000)

