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
from concurrent.futures import ThreadPoolExecutor


def search_all_sites():
    game_name = search_bar.get()
    print(f"Searching for game: {game_name} ...")
    clear_search_results()  # Efface les résultats de recherche précédents
    progress_bar['value'] = 0
    progress_bar['maximum'] = 4  # Nombre de recherches (1 par site)
    threading.Thread(target=lambda: search_g2a(game_name)).start()
    threading.Thread(target=lambda: search_eneba(game_name)).start()
    threading.Thread(target=lambda: search_gamivo(game_name)).start()
    threading.Thread(target=lambda: search_indiegala(game_name)).start()
    threading.Thread(target=lambda: search_instant_gaming(game_name)).start()
def clear_search_results():
    # Détruit tous les widgets enfants de scrollable_frame
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

def add_search_result(site_name, game_title, price, image_url=None,url=None):
    frame = ttk.Frame(scrollable_frame)
    frame.pack(fill=tk.X, padx=10, pady=5)

    # Configurer les colonnes du frame
    frame.grid_columnconfigure(0, weight=0)  # Colonne de l'image
    frame.grid_columnconfigure(1, weight=1, minsize=200)  # Colonne des textes
    frame.grid_columnconfigure(2, weight=0)  # Colonne du bouton d'achat
    frame.grid_columnconfigure(3, weight=0)  # Colonne du prix

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
            print(f"Erreur lors du téléchargement de l'image: {e}")
            image_label = ttk.Label(frame, text="Image indisponible", width=20, relief="solid", borderwidth=1)
            image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nw")
    else:
        image_label = ttk.Label(frame, text="Image indisponible", width=20, relief="solid", borderwidth=1)
        image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nw")

    # Titre du jeu avec padding en haut
    title_label = ttk.Label(frame, text=game_title, font=("Helvetica", 15), wraplength=450)
    title_label.grid(row=0, column=1, columnspan=2, sticky='nw', pady=(10, 0))  # Ajout de pady pour baisser le texte

    # Nom du site avec padding en haut
    site_label = ttk.Label(frame, text=site_name, font=("Helvetica", 12, "bold"), foreground='orange')
    site_label.grid(row=1, column=1, columnspan=2, sticky='nw', pady=(4, 0))  # Ajout de pady pour ajuster le texte

    # Créer un frame pour le bouton et le prix, pour les aligner à droite
    right_frame = ttk.Frame(frame)
    right_frame.grid(row=0, column=3, rowspan=2, sticky='e')  # Place le frame à droite, occupe deux lignes
    
    def open_url():
        if url:
            import webbrowser
            webbrowser.open(url)

    # Bouton d'achat
    buy_button = ttk.Button(right_frame, text="Acheter", bootstyle="primary",command=open_url)
    buy_button.pack(padx=10, pady=5, anchor='e')  # Aligner le bouton à droite

    # Étiquette de prix
    price_label = ttk.Label(right_frame, text=price, font=("Helvetica", 20, "bold"))
    price_label.pack(padx=10, pady=5, anchor='e')  # Aligner le prix à droite


def search_g2a(game_name): #[1288:5636:0828/213018.417:ERROR:socket_manager.cc(147)] Failed to resolve address for ec2-52-23-111-175.compute-1.amazonaws.com., errorcode: -105
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

                if 'Title' in item and 'Price' in item and 'URL' in item:
                    fen_main.after(0, lambda: add_search_result("G2A", item['Title'], item['Price'], item.get('Image'), item['URL']))
            page_number += 1
    except Exception as e:
        print(f"Error searching G2A: {e}")
    finally:
        fen_main.after(0, lambda: progress_bar.step(1)) 
        driver.quit()


def search_eneba(game_name):
    encoded_game_name = urllib.parse.quote(game_name)
    options = Options()
    # options.add_argument('--headless')  # Uncomment to run browser in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
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
                image_tag = game.find("img", src=True)  # Trouver l'image avec la balise <img>
                if image_tag:
                    item['Image'] = image_tag['src']
                link_tag = game.find("a", href=True)  # Extraction de l'URL du jeu
                if link_tag:
                    item['URL'] = "https://www.eneba.com" + link_tag['href']  # Construire l'URL complète
                if 'Title' in item and 'Price' in item and 'URL' in item:
                    fen_main.after(0, lambda: add_search_result("Eneba", item['Title'], item['Price'], item.get('Image'), item['URL']))
            page_number += 1
    except Exception as e:
        print(f"Error searching Eneba: {e}")
    finally:
        fen_main.after(0, lambda: progress_bar.step(1))  # Incrémente la barre de progression
        driver.quit()


def search_gamivo(game_name):
    encoded_game_name = urllib.parse.quote(game_name)
    options = Options()
    # options.add_argument('--headless')  # Uncomment to run browser in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        page_number = 1
        while True:
            url = f"https://www.gamivo.com/fr/search/{encoded_game_name}?page={page_number}"
            driver.get(url)
            time.sleep(0.5)  # Adjust the wait time if necessary
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            all_games = soup.find_all('app-product-tile', class_="ng-star-inserted")
            print(f"[Gamivo]Total number of games found: {len(all_games)}")
            if not all_games:
                print("[Gamivo] End of results.")
                break

            for game in all_games:
                item = {}
                title_tag = game.find("span", class_="ng-star-inserted")
                if title_tag:
                    item['Title'] = title_tag.text.strip()
                else:
                    print("Title not found for this element.")
                price_tag = game.find("span", class_="current-price__value")
                if price_tag:
                    item['Price'] = price_tag.text.strip()
                else:
                    print("Price not found for this element.")
                image_tag = game.find("img", src=True)  # Find the image with the <img> tag
                if image_tag:
                    item['Image'] = image_tag['src']
                link_tag = game.find("a", href=True)  # Extraction de l'URL du jeu
                if link_tag:
                    item['URL'] = "https://www.gamivo.com" + link_tag['href']  # Construire l'URL complète
                if 'Title' in item and 'Price' in item and 'URL' in item:
                    fen_main.after(0, lambda: add_search_result("Gamivo", item['Title'], item['Price'], item.get('Image'), item['URL']))
    except Exception as e:
        print(f"Error searching Gamivo: {e}")
    finally:
        fen_main.after(0, lambda: progress_bar.step(1))  # Incrémente la barre de progression
        driver.quit()

def search_indiegala(game_name):
    encoded_game_name = urllib.parse.quote(game_name)
    options = Options()
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        page_number = 1
        while True:
            url = f"https://www.indiegala.com/store?search={encoded_game_name}&page={page_number}"
            driver.get(url)
            time.sleep(10)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_games = soup.find_all('div', class_="product-tile game-tile")

            if not all_games:
                print("[Indiegala] End of results.")
                break

            for game in all_games:
                item = {}
                title_tag = game.find("h5", class_="ellipsis_title")
                if title_tag:
                    item['Title'] = title_tag.text.strip()
                price_tag = game.find("div", class_="price-current")
                if price_tag:
                    item['Price'] = price_tag.text.strip()
                image_tag = game.find("img", src=True)
                if image_tag:
                    item['Image'] = image_tag['src']
                link_tag = game.find("a", href=True)  # Extraction de l'URL du jeu
                if link_tag:
                    item['URL'] = "https://www.indiegala.com" + link_tag['href']  # Construire l'URL complète

                if 'Title' in item and 'Price' in item and 'URL' in item:
                    fen_main.after(0, lambda: add_search_result("Indiegala", item['Title'], item['Price'], item.get('Image'), item['URL']))
            page_number += 1
    except Exception as e:
        print(f"Error searching Indiegala: {e}")
    finally:
        driver.quit()
        fen_main.after(0, lambda: progress_bar.step(1))  # Incrémente la barre de progression

def search_instant_gaming(game_name):
    encoded_game_name = urllib.parse.quote_plus(game_name)
    options = Options()
    # options.add_argument('--headless')  # Uncomment to run browser in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        page_number = 1
        while True:
            url = f"https://www.instant-gaming.com/fr/rechercher/?q={encoded_game_name}&page={page_number}"
            driver.get(url)
            time.sleep(0.25)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_games = soup.find_all('li', class_="item force-badge")
            results = []
            
            if not all_games:
                print("End of results.")
                break  # Break the loop when there are no more pages to scrape
            
            for game in all_games:
                item = {}
                title_tag = game.find("span", class_="Title")
                if title_tag:
                    item['Title'] = title_tag.text.strip()
                price_tag = game.find("span", class_="price")
                if price_tag:
                    item['Price'] = price_tag.text.strip()
                image_tag = game.find("img", src=True)  # Trouver l'image avec la balise <img>
                if image_tag:
                    item['Image'] = image_tag['src']
                if 'Title' in item and 'Price' in item:
                    results.append(item)
                    fen_main.after(0, lambda: add_search_result("Instant Gaming", item['Title'], item['Price'], item.get('Image')))
                page_number += 1
    except Exception as e:
        print(f"Error searching Instant Gaming : {e}")
    finally:
        driver.quit()

def scroll_until_end(driver, scroll_pause_time):
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

searching = False

def start_search():
    global searching
    searching = True
    btn_stop.config(state="normal")  # Activer le bouton stop
    search_button.config(state="disabled")  # Désactiver le bouton rechercher
    perform_search()

def stop_search():
    global searching
    searching = False
    btn_stop.config(state="disabled")  # Désactiver le bouton stop
    search_button.config(state="normal")  # Réactiver le bouton rechercher

def perform_search():
    global searching
    while searching:
        # Votre code de recherche ici
        print("Recherche en cours...")  # Juste un exemple
        # Ajoutez une condition ou un break pour sortir de la boucle si searching est False
        if not searching:
            break

    btn_stop.config(state="disabled")  # Désactiver le bouton stop
    search_button.config(state="normal")  # Réactiver le bouton rechercher
    print("Recherche arrêtée.")

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
btn_stop = ttk.Button(fen_main, text="Stop", command=stop_search, state="disabled")
btn_stop.pack(padx=5)

progress_frame = ttk.Frame(fen_main)
progress_frame.pack(pady=(0, 5))  # Ajuste l'espace au besoin

progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate",bootstyle="info-striped", length=312)
progress_bar.pack(padx=(5, 0))

# Reducing the width of the second column (containing the search button)
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