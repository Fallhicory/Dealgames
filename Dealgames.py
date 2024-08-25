import ttkbootstrap as ttk
import tkinter as tk
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse
import threading

def search_all_sites():
    game_name = search_bar.get()
    print(f"Searching for game: {game_name} ...")
    results_text.delete('1.0', tk.END)  # Clear previous results
    threading.Thread(target=lambda: search_g2a(game_name)).start()
    threading.Thread(target=lambda: search_eneba(game_name)).start()
    threading.Thread(target=lambda: search_gamivo(game_name)).start()
    threading.Thread(target=lambda: search_indiegala(game_name)).start()
# GUI setup
fen_main = tk.Tk()
fen_main.title("DealGames")
fen_main.geometry("1031x693")

search = ttk.Frame(master=fen_main)
search.pack(pady=10)
results = ttk.Frame(master=fen_main)

# Search bar setup
search_bar = ttk.Entry(search, width=50)
search_bar.insert(0, 'Search your game here...')
search_bar.bind('<FocusIn>', lambda event: on_entry_click(event))
search_bar.bind('<FocusOut>', lambda event: on_focusout(event))
search_bar.config(foreground='grey')
search_bar.grid(row=0, column=0, padx=(5, 0), pady=15)

# Button to trigger search
search_button = ttk.Button(search, text="Search", command=search_all_sites)
search_button.grid(row=0, column=1, padx=10, pady=5)

# Text widget to display results
scroll = ttk.Scrollbar(results,orient='vertical')
scroll.pack(side="right",fill="y")
results_text = tk.Text(results, height=35, width=170,yscrollcommand=scroll.set, wrap="none", font=("helvetica", 12))
results_text.pack(padx=10, pady=(0, 10))
scroll.config(command=results_text.yview)
results.pack()

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
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        
        # Calculate new scroll height after scrolling
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def search_g2a(game_name):
    encoded_game_name = urllib.parse.quote(game_name)
    options = Options()
    # options.add_argument('--headless') # Uncomment to run browser in headless mode
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        url = f"https://www.g2a.com/fr/category/games-c189?query={encoded_game_name}"
        driver.get(url)
        time.sleep(0.25)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

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
                # Update results in the text widget
                fen_main.after(0, lambda: results_text.insert(tk.END, f"[G2A] Game: {item['Title']} - Price: {item['Price']}\n"))
        return results
    except Exception as e:
        print(f"Error searching G2A: {e}")
    finally:
        driver.quit()

def search_eneba(game_name):
    encoded_game_name = urllib.parse.quote(game_name)
    options = Options()
    # options.add_argument('--headless') # Uncomment to run browser in headless mode
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        page_number = 1
        while True:
            url = f"https://www.eneba.com/fr/store/all?text={encoded_game_name}&page={page_number}"
            driver.get(url)
            time.sleep(1)
            scroll_until_end(driver, scroll_pause_time=1)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_games = soup.find_all('div', class_="pFaGHa WpvaUk")
            if not all_games:
                print("End of results.")
                break

            for game in all_games:
                item = {}
                title_tag = game.find("span", class_="YLosEL")
                if title_tag:
                    item['Title'] = title_tag.text.strip()
                price_tag = game.find("span", class_="L5ErLT")
                if price_tag:
                    item['Price'] = price_tag.text.strip()

                if 'Title' in item and 'Price' in item:
                    # Update results in the text widget
                    fen_main.after(0, lambda: results_text.insert(tk.END, f"[Eneba] Game: {item['Title']} - Price: {item['Price']}\n"))

            page_number += 1
    except Exception as e:
        print(f"Error searching Eneba: {e}")
    finally:
        driver.quit()

def search_gamivo(game_name):
    encoded_game_name = urllib.parse.quote(game_name)
    options = Options()
    # options.add_argument('--headless') # Uncomment to run browser in headless mode
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    # Ouvrir l'URL cible
    url = f"https://www.gamivo.com/fr/search/{encoded_game_name}"
    driver.get(url)

    time.sleep(0.5)  # Ajuste le temps d'attente si nécessaire

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Fermer le navigateur
    driver.quit()

    all_games = soup.find_all('app-product-tile', class_="ng-star-inserted")
    print(f"Nombre total de jeux trouvés : {len(all_games)}")

    for game in all_games:
        item = {}
        title_tag = game.find("span", class_="ng-star-inserted")
        if title_tag:
            item['Title'] = title_tag.text.strip()
        else:
            print("Titre non trouvé pour cet élément.")

        price_tag = game.find("span", class_="current-price__value")
        if price_tag:
            item['Price'] = price_tag.text.strip()
        else:
            print("Prix non trouvé pour cet élément.")

        if 'Title' in item and 'Price' in item:
            fen_main.after(0, lambda: results_text.insert(tk.END, f"[Gamivo] Game: {item['Title']} - Price: {item['Price']}\n"))

def search_indiegala(game_name):
    encoded_game_name = urllib.parse.quote(game_name)
    options = Options()
    # options.add_argument('--headless') # Uncomment to run browser in headless mode
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    # Ouvrir l'URL cible
    url = f"https://www.indiegala.com/search/{encoded_game_name}/store-games"
    driver.get(url)
    time.sleep(1)  # Ajuste le temps d'attente si nécessaire
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Fermer le navigateur
    driver.quit()
    all_games = soup.find_all('div', class_="relative main-list-results-item")
    print(f"Nombre total de jeux trouvés : {len(all_games)}")
    for game in all_games:
        item = {}
        title_tag = game.find("h3", class_="bg-gradient-red")
        if title_tag:
            item['Title'] = title_tag.text.strip()
        else:
            print("Titre non trouvé pour cet élément.")
        price_tag = game.find("div", class_="main-list-results-item-price")
        if price_tag:
            item['Price'] = price_tag.text.strip()
        else:
            price_tag = game.find("div", class_="main-list-results-item-price-new")
            if price_tag:
                item['Price'] = price_tag.text.strip()
            else:
                print("Price not found for this element.")
            
        if 'Title' in item and 'Price' in item:
            fen_main.after(0, lambda: results_text.insert(tk.END, f"[Indiegala] Game: {item['Title']} - Price: {item['Price']}\n"))

fen_main.mainloop()
