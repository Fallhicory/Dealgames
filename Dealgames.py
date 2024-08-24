import ttkbootstrap as ttk
import tkinter as tk
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import urllib.parse

#1031*693

def on_entry_click(event):
    """Erase text on click"""
    if search_bar.get() == 'Search your game here...':
        search_bar.delete(0, tk.END)
        search_bar.config(foreground='black')

def on_focusout(event):
    """Put text when empty"""
    if search_bar.get() == '':
        search_bar.insert(0, 'Search your game here...')
        search_bar.config(foreground='grey')

def scroll_until_end(driver, scroll_pause_time=1):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroller jusqu'à la fin de la page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Attendre le chargement des nouveaux contenus
        time.sleep(scroll_pause_time)

        # Calculer la nouvelle hauteur de la page après scroll
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

fen_main = tk.Tk()
fen_main.title("DealGames")
fen_main.geometry("1031x693")

search = ttk.Frame(master=fen_main)
search_bar = ttk.Entry(search, width=50)
search_bar.insert(0, 'Search your game here...')
search_bar.bind('<FocusIn>', on_entry_click)
search_bar.bind('<FocusOut>', on_focusout)
search_bar.config(foreground='grey')
search_bar.grid(row=0, column=0, padx=(5, 0), pady=15)

Search_but = ttk.Button(search, text="Search")
Search_but.grid(row=0, column=1, padx=10, pady=5)


search.pack()

fen_main.mainloop()

#Actually, all the search scripts are on python notebook (at the moment)
# %%
import requests
from bs4 import BeautifulSoup
# %%
url = 'https://www.cdkeys.com/fr_fr/pc/jeux'
# %%
page = requests.get(url)
# %%
soup = BeautifulSoup(page.text, 'html')
# %%
print(soup.title.text)
# %%
all_games = soup.find_all("li", class_="product-item")
for game in all_games:
    item = {}
    title_tag = game.find("a", class_="product-item-link")
    if title_tag:
        item['Title'] = title_tag.text.strip()
    # Extraire le prix du jeu
    item['Price'] = game.find("span", class_="price").text.strip()
    # Afficher le nom et le prix du jeu
    print(f"Nom du jeu : {item['Title']} - Prix : {item['Price']}")

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import urllib.parse

def search_g2a(game_name):
    encoded_game_name = urllib.parse.quote(game_name)
    driver = webdriver.Chrome()
    url = f"https://www.g2a.com/fr/category/games-c189?query={encoded_game_name}"
    driver.get(url)
    
    time.sleep(0.5)  # Attendre le chargement de la page
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    all_games = soup.find_all('li', class_="sc-gIvpjk kgKIqe indexes__StyledProductBox-wklrsw-122 beGIwZ productCard")
    results = []
    
    for game in all_games:
        item = {}
        title_tag = game.find("h3", class_="sc-iqAclL sc-dIsUp dJFpVb eHDAgC sc-daBunf brOVbM")
        if title_tag:
            item['Title'] = title_tag.text.strip()
        price_tag = game.find("span", class_="sc-iqAclL sc-crzoAE dJFpVb eqnGHx sc-bqGGPW gjCrxq")
        if price_tag:
            item['Price'] = price_tag.text.strip()
        if 'Title' in item:
            results.append(item)
            print(f"[G2A] Nom du jeu : {item['Title']} - Prix : {item['Price']}")
    return results

