import requests
import time

while True:
  iTOKEN = '6711233009:AAE7zKPUZzXzu3ulH2WjD0ctAZdQSoOLLv8'
  iURL = f'https://api.telegram.org/bot{iTOKEN}/getUpdates'
  iRESULT = requests.get(iURL)
  print(iRESULT.json())
  time.sleep(5)
