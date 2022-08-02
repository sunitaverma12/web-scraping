from importlib.resources import contents
from itertools import product
from logging import exception
from math import prod
from unicodedata import name
import requests
from bs4 import BeautifulSoup
from cgitb import text
from distutils.log import error
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from sqlalchemy import null
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import copy
import json
import csv


def scrap_product_listing(html,driver):
     current_url=driver.current_url
     soup = BeautifulSoup(html, 'html.parser')
     tag=soup.find('href')
     print(tag)
     
     product_listing=soup.find_all(  'div',class_="a-section a-spacing-small a-spacing-top-small")
     # print(product_listing)
     products_data=[]

     for idx,product in enumerate(product_listing):
          product_data={}
     
          # print(type(product))
          product_name=product.find_all(  'span',class_="a-size-medium a-color-base a-text-normal")
          product_rating=product.find_all(  'span',class_="a-icon-alt")
          product_price=product.find_all(  'span',class_="a-price-whole")
          product_reviews=product.find_all(  'span',class_="a-size-base s-underline-text")
          product_url=product.find_all(  'a',class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal",href= True)

          if not product_name or not product_rating or not product_price or not product_reviews:
               continue
          product_data['name'] = product_name[0].get_text()
          product_data['rating'] = product_rating[0].get_text()
          product_data['price'] = product_price[0].get_text()
          product_data['reviews'] = product_reviews[0].get_text()
          url= product_url[0]['href']
          # time.sleep(2)

          driver.get('https://www.amazon.in'+url)
          htmldetail=driver.page_source

          soup = BeautifulSoup(htmldetail, 'html.parser')
         
          products_detail=soup.find_all(  'div', id="detailBullets_feature_div")
          if products_detail:
               for li_tag in products_detail[0].find_all('ul', {'class':'a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list'}):
                    for span_tag in li_tag.find_all('li'):
                         field = span_tag.find('span', {'class':'a-list-item'}).text.split(':')
                         new_field=''.join(e for e in field[0] if e.isalnum())
                         if new_field in ('Manufacturer','ASIN'):
                              product_data[new_field] = field[1].replace(" ", "").replace('\n','')


          products_data.append(product_data)
          time.sleep(2)  

     driver.get(current_url)

     return products_data


def save_data(data):
     with open('amazon_products.csv', 'w', newline='') as file:
          writer = csv.writer(file)
          writer.writerow(data[0].keys())
          for items in data:
               writer.writerow(items.values())

website=("https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1")
path='/home/deepak/scraping-amazon/chromedriver'
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(website)
print(driver.page_source)
all_product=[]

page_number=1
try:
     while (page_number<21):


          html=driver.page_source
          products=scrap_product_listing(html,driver)
          print(products)
          all_product.extend(products)
          driver.find_element( "xpath", '//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]').click()
          page_number+=1 
          time.sleep(5)
except exception as e:
     print(e)
     print('==============')
     print(page_number) 
finally:
     save_data(all_product)                             





