import ttkbootstrap as ttk
import tkinter as tk
import requests
from bs4 import BeautifulSoup
#1031*693
fen_main = tk.Tk()
fen_main.title = "DealGames"
fen_main.geometry("1031x693")



search_bar = ttk.Entry(fen_main,width = 50)
search_bar.insert(0,'Search your game here...',)
search_bar.pack(padx = 5, pady = 15)
search_bar.pack()
fen_main.mainloop()




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

