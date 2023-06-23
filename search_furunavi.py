from selenium import webdriver
from time import sleep
import math
import csv
import unicodedata
from pprint import pprint
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os


def main():
    file_path = os.path.dirname(os.path.abspath(__file__))
    results_filename = 'results.csv'
    results_file_path = f"{file_path}/{results_filename}"

    try:
        os.remove(results_file_path)
    except WindowsError as e:
        pass

    # ブラウザを開かないように設定
    options = Options()
    options.add_argument('--headless')

    search_word = "牛赤身"
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)

    target_url = f"https://furunavi.jp/Product/Search?keyword={search_word}&pagesize=100"
    driver.get(target_url)

    # ページ数取得
    product_cnt = driver.find_element(By.CLASS_NAME,"pagination_top").find_element(By.CLASS_NAME,"product_count")
    page_cnt = math.ceil(int(product_cnt.text) / 100)


    results = [["商品名","重さ(g)","値段","円/100g","URL",]]
    for page in range(1,page_cnt+1):
        print(f"{page}/{page_cnt}ページ")
        driver.get(target_url+f"&pageno={page}")
        sleep(1)

        main_list = driver.find_element(By.CLASS_NAME,"main_list")
        products = main_list.find_elements(By.CLASS_NAME,"product-info")

        for product in products:
            product_name_ele = product.find_element(By.CLASS_NAME,"product-name")
            product_name = unicodedata.normalize('NFKC',product_name_ele.text)
            result = [product_name]
            g_position = product_name.rfind("g")
            qty = ""
            if g_position != -1:
                for i in range(1,10):
                    char_to_confirm = product_name[g_position-i]
                    if char_to_confirm.isdigit() or char_to_confirm == ".":
                        qty = char_to_confirm + qty
                    elif char_to_confirm == ",":
                        pass
                    elif char_to_confirm == "k":
                        pass
                    else:
                        break
                if qty:
                    qty = float(qty)
                if product_name[g_position-1] == "k":
                    qty = qty*1000

                multiplier = ""
                if len(product_name) > g_position+1:
                    if product_name[g_position+1] == "×":
                        for i in range(2,6):
                            if len(product_name) > g_position+i:
                                char_to_confirm = product_name[g_position+i]
                                if char_to_confirm.isdigit():
                                    multiplier += char_to_confirm
                                else:
                                    break
                        try:
                            multiplier = float(multiplier)
                        except Exception as e:
                            print(e)
                            print(multiplier)
                if multiplier:
                    qty *= multiplier
            result.append(qty)
            product_price = int(product.find_element(By.CLASS_NAME,"product-price").text.replace(",",""))
            result.append(product_price)
            product_url = product_name_ele.find_element(By.TAG_NAME,"a").get_attribute("href")
            price_per_100g = product_price/qty * 100 if qty else ""
            result.append(price_per_100g)
            result.append(product_url)
            results.append(result)

    with open(results_file_path,'w',newline="") as f:
        writer = csv.writer(f)
        writer.writerows(results)

main()