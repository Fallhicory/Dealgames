import ttkbootstrap as ttk
import tkinter as tk
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.parse
import threading
import requests
from PIL import Image, ImageTk
from io import BytesIO

def add_error_message(message):
    error_label = ttk.Label(scrollable_frame, text=message, font=("Helvetica", 15), foreground="red")
    error_label.pack(pady=20,padx=50)

def search_all_sites():
    global results_found
    results_found = False
    game_name = search_bar.get()
    print(f"Searching for game: {game_name} ...")
    clear_search_results()  
    progress_bar['value'] = 0
    progress_bar['maximum'] = 5  
    #threading.Thread(target=lambda: search_g2a(game_name)).start() #Didn't work bc of amazon ad services
    threading.Thread(target=lambda: search_eneba(game_name)).start()
    threading.Thread(target=lambda: search_gamivo(game_name)).start()
    threading.Thread(target=lambda: search_indiegala(game_name)).start()
    threading.Thread(target=lambda: search_instant_gaming(game_name)).start()
    threading.Thread(target=lambda: search_gamebillet(game_name)).start()

    def check_results():
        if not results_found:
            add_error_message("Gmae not found.")
    fen_main.after(20000, check_results)
def clear_search_results():

    for widget in scrollable_frame.winfo_children():
        widget.destroy()

def add_search_result(site_name, game_title, price, image_url=None,url=None):
    frame = ttk.Frame(scrollable_frame)
    frame.pack(fill=tk.X, padx=10, pady=5)

    frame.grid_columnconfigure(0, weight=0)  #image
    frame.grid_columnconfigure(1, weight=1, minsize=200)  # text
    frame.grid_columnconfigure(2, weight=0)  # buy button
    frame.grid_columnconfigure(3, weight=0)  # price

    # Placeholder pour l'image du jeu
    if image_url:
        try:
            response = requests.get(image_url)
            image_data = response.content
            pil_image = Image.open(BytesIO(image_data)).resize((125, 160))
            img = ImageTk.PhotoImage(pil_image)
            image_label = ttk.Label(frame, image=img)
            image_label.image = img
            image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nw")
        except Exception as e:
            print(f"Error while downloading: {e}")
            image_label = ttk.Label(frame, text="Image not available", width=20, relief="solid", borderwidth=1)
            image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nw")
    else:
        image_label = ttk.Label(frame, text="Image not available", width=20, relief="solid", borderwidth=1)
        image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nw")

    # Title game
    title_label = ttk.Label(frame, text=game_title, font=("Helvetica", 15), wraplength=450)
    title_label.grid(row=0, column=1, columnspan=2, sticky='nw', pady=(10, 0))  # Ajout de pady pour baisser le texte

    # Name site
    site_label = ttk.Label(frame, text=site_name, font=("Helvetica", 12, "bold"), foreground='orange')
    site_label.grid(row=1, column=1, columnspan=2, sticky='nw', pady=(4, 0))  # Ajout de pady pour ajuster le texte

    right_frame = ttk.Frame(frame)
    right_frame.grid(row=0, column=3, rowspan=2, sticky='e')
    
    def open_url():
        if url:
            import webbrowser
            webbrowser.open(url)

    buy_button = ttk.Button(right_frame, text="Acheter", bootstyle="primary",command=open_url)
    buy_button.pack(padx=10, pady=5, anchor='e') 

    price_label = ttk.Label(right_frame, text=price, font=("Helvetica", 20, "bold"))
    price_label.pack(padx=10, pady=5, anchor='e') 


def search_g2a(game_name): #[1288:5636:0828/213018.417:ERROR:socket_manager.cc(147)] Failed to resolve address for ec2-52-23-111-175.compute-1.amazonaws.com., errorcode: -105
    global results_found
    encoded_game_name = urllib.parse.quote(game_name)
    options = Options()
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        page_number = 1
        while True:
            url = f"https://www.g2a.com/fr/category/games-c189?page={page_number}&query={encoded_game_name}"
            driver.get(url)
            time.sleep(0.25)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_games = soup.find_all('li', class_="sc-gIvpjk kgKIqe indexes__StyledProductBox-wklrsw-122 beGIwZ productCard")

            if not all_games:
                print("[G2A] End of results.")
                break
            
            for game in all_games:
                item = {}
                title_tag = game.find("h3", class_="sc-iqAclL sc-dIsUp dJFpVb eHDAgC sc-daBunf brOVbM")
                if title_tag:
                    item['Title'] = title_tag.text.strip()
                price_tag = game.find("span", class_="sc-iqAclL sc-crzoAE dJFpVb eqnGHx sc-bqGGPW gjCrxq")
                if price_tag:
                    item['Price'] = price_tag.text.strip()
                image_tag = game.find("img", src=True)
                if image_tag:
                    item['Image'] = image_tag['src']
                link_tag = game.find("a", href=True)
                if link_tag:
                    item['URL'] = "https://www.g2a.com" + link_tag['href'] 

                if 'Title' in item:
                    fen_main.after(0, lambda: add_search_result("G2A", item['Title'], item['Price'], item.get('Image'), item['URL']))
                    results_found = True
            page_number += 1
    except Exception as e:
        print(f"Error searching G2A: {e}")
    finally:
        fen_main.after(0, lambda: progress_bar.step(1)) 
        driver.quit()


def search_eneba(game_name):
    global results_found
    encoded_game_name = urllib.parse.quote(game_name)
    options = Options()
    # options.add_argument('--headless')  # Uncomment to run browser in headless mode
    options.add_argument("--disable-gpu")  
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        page_number = 1
        while True:
            url = f"https://www.eneba.com/fr/store/all?text={encoded_game_name}&page={page_number}"
            driver.get(url)
            time.sleep(0.5)
            scroll_until_end(driver, scroll_pause_time=0.5)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_games = soup.find_all('div', class_="pFaGHa WpvaUk")
            print(f"[Eneba] Total number of games found: {len(all_games)}")
            if not all_games:
                print("[Eneba] End of results.")
                break

            for game in all_games:
                item = {}
                title_tag = game.find("span", class_="YLosEL")
                if title_tag:
                    item['Title'] = title_tag.text.strip()
                price_tag = game.find("span", class_="L5ErLT")
                if price_tag:
                    item['Price'] = price_tag.text.strip()
                image_tag = game.find("img", src=True)  
                if image_tag:
                    item['Image'] = image_tag['src']
                link_tag = game.find("a", href=True)  
                if link_tag:
                    item['URL'] = "https://www.eneba.com" + link_tag['href']  
                if 'Title' in item and 'Price' in item and 'URL' in item:
                    fen_main.after(0, lambda: add_search_result("Eneba", item['Title'], item['Price'], item.get('Image'), item['URL']))
                    results_found = True
            page_number += 1
    except Exception as e:
        print(f"Error searching Eneba: {e}")
    finally:
        fen_main.after(0, lambda: progress_bar.step(1))  
        driver.quit()


def search_gamivo(game_name):
    global results_found
    encoded_game_name = urllib.parse.quote(game_name)
    options = Options()
    options.add_argument("--disable-gpu")  
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        page_number = 1
        while True:
            url = f"https://www.gamivo.com/fr/search/{encoded_game_name}?page={page_number}"
            driver.get(url)
            time.sleep(0.5)  # Adjust the wait time if necessary
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            all_games = soup.find_all('app-product-tile', class_="ng-star-inserted")
            print(f"[Gamivo] Total number of games found: {len(all_games)}")
            if not all_games:
                print("[Gamivo] End of results.")
                break

            for game in all_games:
                item = {}
                title_tag = game.find("span", class_="ng-star-inserted")
                if title_tag:
                    item['Title'] = title_tag.text.strip()
                price_tag = game.find("span", class_="current-price__value")
                if price_tag:
                    item['Price'] = price_tag.text.strip()
                image_tag = game.find("img", src=True)  
                if image_tag:
                    item['Image'] = image_tag['src']
                link_tag = game.find("a", href=True)  
                if link_tag:
                    item['URL'] = "https://www.gamivo.com" + link_tag['href']  
                if 'Title' in item and 'Price' in item and 'URL' in item:
                    fen_main.after(0, lambda: add_search_result("Gamivo", item['Title'], item['Price'], item.get('Image'), item['URL']))
                    results_found = True
            page_number += 1
    except Exception as e:
        print(f"Error searching Gamivo: {e}")
    finally:
        fen_main.after(0, lambda: progress_bar.step(1)) 
        driver.quit()


def search_indiegala(game_name):
    global results_found
    encoded_game_name = urllib.parse.quote(game_name)
    options = Options()
    #options.add_argument('--headless')
    options.add_argument("--disable-gpu") 
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    url = f"https://www.indiegala.com/search/{encoded_game_name}/store-games"

    driver.get(url)
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    all_games = soup.find_all('div', class_="relative main-list-results-item")
    print(f"[Indiegala]Total number of games found: {len(all_games)}")
    if not all_games:
        print("[Indiegala] End of results.")
    for game in all_games:
        item = {}
        title_tag = game.find("h3", class_="bg-gradient-red")
        if title_tag:
            link_tag = title_tag.find("a")
        if link_tag:
            item['Title'] = link_tag.text.strip()
        price_tag = game.find("div", class_="main-list-results-item-price") or game.find("div", class_="main-list-results-item-price-new")
        if price_tag:
            item['Price'] = price_tag.text.strip()
        image_tag = game.find("img", src=True)
        if image_tag:
            item['Image'] = image_tag['src']
        link_tag = game.find("a", href=True) 
        if link_tag:
            item['URL'] = "https://www.indiegala.com" + link_tag['href'] 
        if 'Title' in item and 'Price' in item and 'URL' in item:
            fen_main.after(0, lambda: add_search_result("Indiegala", item['Title'], item['Price'], item.get('Image'), item['URL']))
            results_found = True

def search_instant_gaming(game_name):
    global results_found
    encoded_game_name = urllib.parse.quote_plus(game_name)
    options = Options()
    options.add_argument('--headless')  # Uncomment to run browser in headless mode
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    page_number = 1
    url = f"https://www.instant-gaming.com/fr/rechercher/?q={encoded_game_name}&page={page_number}"
    driver.get(url)
    time.sleep(2)  
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    all_games = soup.find_all('div', class_="item force-badge")
    if not all_games:
        print("[Instant Gaming] End of results. (games not found)")
    else:
        for game in all_games:
            item = {}
            title_tag = game.find("span", class_="title")
            if title_tag:
                item['Title'] = title_tag.text.strip()
            price_tag = game.find("div", class_="price")
            if price_tag:
                item['Price'] = price_tag.text.strip()
            image_tag = game.find("img", src=True)
            if image_tag:
                item['Image'] = image_tag['src']
            link_tag = game.find("a", href=True) 
            if link_tag:
                item['URL'] = link_tag['href']  
            if 'Title' in item and 'Price' in item:
                add_search_result("Instant Gaming", item['Title'], item['Price'], item.get('Image'), item['URL'])
                results_found = True

def search_gamebillet(game_name):
    global results_found
    encoded_game_name = urllib.parse.quote_plus(game_name)
    options = Options()
    options.add_argument("--disable-gpu")  
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        url = f"https://www.gamebillet.com/search?q={encoded_game_name}"
        driver.get(url)
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_games = soup.find_all('div', class_="col-xs-6 col-sm-4 col-lg-3")
        if not all_games:
            print("[Gamebillet] End of results.")
        for game in all_games:
            item = {}

            title_tag = game.find('h3')
            if title_tag and title_tag.a:
                item['Title'] = title_tag.a.text.strip()
                item['URL'] = "https://www.gamebillet.com" + title_tag.a['href']

            price_tag = game.select_one('div.buy-wrapper > span')
            if price_tag:
                item['Price'] = price_tag.text.strip()

            # Extraire l'URL de l'image
            image_tag = game.find('img', class_='img-responsive center-block grid-img-as-bg')
            if image_tag:
                item['Image'] = image_tag['src']

            if 'Title' in item and 'Price' in item and 'URL' in item:
                fen_main.after(0, lambda: add_search_result("Gamebillet", item['Title'], item['Price'], item.get('Image'), item['URL']))
                results_found = True

    except Exception as e:
        print(f"Error searching Gamebillet: {e}")
    finally:
        fen_main.after(0, lambda: progress_bar.step(1))
        driver.quit()  
                    

def scroll_until_end(driver, scroll_pause_time): #For eneba
    """Scrolls down a webpage until the end."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

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

# UI Setup
fen_main = ttk.Window( title="Dealgames", size=(735, 890))
search_frame = ttk.Frame(fen_main)
search_frame.pack(pady=20)

search_bar = ttk.Entry(search_frame, width=50)
search_bar.insert(0, 'Search your game here...')
search_bar.bind('<FocusIn>', lambda event: on_entry_click(event))
search_bar.bind('<FocusOut>', lambda event: on_focusout(event))
search_bar.config(foreground='grey')
search_bar.grid(row=0, column=0, padx=(5, 0), pady=15)

search_button = ttk.Button(search_frame, text="Rechercher", command=search_all_sites)
search_button.grid(row=0, column=1, padx=5)

progress_frame = ttk.Frame(fen_main)
progress_frame.pack(pady=(0, 5)) 

progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate",bootstyle="info-striped", length=312)
progress_bar.pack(padx=(5, 0))

search_frame.columnconfigure(1, minsize=0, weight=0)

canvas = tk.Canvas(fen_main)
scrollbar = ttk.Scrollbar(fen_main, bootstyle="round", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
fen_main.mainloop()