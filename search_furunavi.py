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
from datetime import datetime


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


    results = [["商品名","重さ(g)","値段","円/100g","URL",datetime.now()]]
    for page in range(1,page_cnt+1):
        try:
            print(f"{page}/{page_cnt}ページ")
            driver.get(target_url+f"&pageno={page}")
            sleep(1)

            # ページ内の製品を取得
            main_list = driver.find_element(By.CLASS_NAME,"main_list")
            products = main_list.find_elements(By.CLASS_NAME,"product-info")

            # 製品ごとにデータ取得
            for product in products:
                result = []

                # 製品名取得
                product_name_ele = product.find_element(By.CLASS_NAME,"product-name")
                product_name = unicodedata.normalize('NFKC',product_name_ele.text)
                result.append(product_name)

                # 量を取得
                g_position = product_name.find("g")  # g(グラム)の位置を確認
                try:
                    qty = ""
                    if g_position == -1:
                        qty = "なし"
                    else:
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
                                multiplier = float(multiplier)
                        if multiplier:
                            qty *= multiplier
                except Exception as e:
                    qty = e
                    print("qty error")
                    print(e)
                    print("qty:",qty)
                    print("multiplier:",multiplier)
                result.append(qty)

                # 製品の価格を取得
                product_price = int(product.find_element(By.CLASS_NAME,"product-price").text.replace(",",""))
                result.append(product_price)

                # 100gあたりの価格を計算
                try:
                    price_per_100g = product_price/qty * 100
                except Exception as e:
                    price_per_100g = e
                    print("price_per_100g error")
                    print(e)
                result.append(price_per_100g)

                # 製品のURLを取得
                product_url = product_name_ele.find_element(By.TAG_NAME,"a").get_attribute("href")
                result.append(product_url)

                results.append(result)
        except Exception as e:
            print(e)

    def save_to_csv():
        with open(results_file_path,'w',newline="",encoding='shift-jis') as f:
            writer = csv.writer(f)
            writer.writerows(results)
    try:
        save_to_csv()
    except PermissionError as e:
        print(f"{results_filename}を閉じてEnterキーを押してください。")
        print(e)
        input()
        save_to_csv()

main()