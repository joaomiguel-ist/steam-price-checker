import sys
import os
import json
import time
from datetime import datetime
from tkinter import *

try:
    import requests
except ImportError:
    print("Failed to import module requests")
    try:
        choice = input("Install requests? [y/n] ")
    except KeyboardInterrupt:
        print("\n Error")
        sys.exit(1)
    if choice.strip().lower()[0] == "y":
        print("Attempting to Install requests")
        sys.stdout.flush()
        try:
            import pip
            pip.main(["install", "-q", "requests"])
            import requests
            print("DONE")
        except Exception:
            print("FAIL")
            sys.exit(1)
    elif choice.strip().lower()[0] == "n":
        print("User Denied Install")
        sys.exit(1)
    else:
        print("Invalid Decision")
        sys.exit(1)

appID = input("Please input appIDs: ")
print("")
appids = appID.split()
c = 0
removable = []
# check the user input is valid
for ints in appids:
    getstatus = requests.get('http://store.steampowered.com/api/appdetails/?appids=%d&filters=price_overview&cc=us' % int(ints))
    status = json.loads(getstatus.text)
    try:
        price_check = status[str(ints)]["data"]["price_overview"]["initial"]
        appids[c] = int(ints)
        c += 1
    except:
        print("No such appID: {0}".format(ints))
        removable.append(ints)
        c += 1
# remove the removables
for rems in removable:
    if rems in appids:
        appids.remove(rems)

# target price
target_price = {}
ct = 0
for x in appids:
    getstatus = requests.get(
        'http://store.steampowered.com/api/appdetails/?appids=%d&filters=price_overview&cc=us' % int(x))
    status = json.loads(getstatus.text)
    price = []
    for nums in str(status[str(x)]["data"]["price_overview"]["final"]):
        price.append(nums)
        ct += 1
    if ct == 3:
        price.insert(1, ".")
    else:
        price.insert(2, ".")
    price = float("".join(price))

    getname = requests.get('http://store.steampowered.com/api/appdetails/?appids=%d&cc=us' % x)
    njson = json.loads(getname.text)
    name = njson[str(x)]["data"]["name"]
    targets = input("Target price for {0} in USD (current price is {1} USD): ".format(name, price))
    target_price[x] = float(targets)

print("")

# ask the user to alert when game on discount
alert_on_discount = {}
for ids in appids:
    getname = requests.get('http://store.steampowered.com/api/appdetails/?appids=%d&cc=us' % ids)
    njson = json.loads(getname.text)
    name = njson[str(ids)]["data"]["name"]
    while True:
        uans = input("Alert when {0} is on discount? [y/n]: ".format(name))
        if (uans == "y") or (uans == "Y"):
            alert_on_discount[ids] = True
            break
        elif (uans == "n") or (uans == "N"):
            alert_on_discount[ids] = False
            break
        else:
            print("Please enter [y]es or [n]o")
            continue

print("")

# printing out the watching game names
names = []
for i in appids:
    getname = requests.get('http://store.steampowered.com/api/appdetails/?appids=%d&cc=us' % i)
    gnjson = json.loads(getname.text)
    names.append(gnjson[str(i)]["data"]["name"])
print("Watching games: " +", ".join(names))


print("")

def steam_price(appID):
    getprice = requests.get('http://store.steampowered.com/api/appdetails/?appids=%d&filters=price_overview&cc=us' % appID)
    getname = requests.get('http://store.steampowered.com/api/appdetails/?appids=%d&cc=us' % appID)
    njson = json.loads(getname.text)
    rjson = json.loads(getprice.text)

    game_name = njson[str(appID)]["data"]["name"]
    count = 0
    initial_price = []
    for nums in str(rjson[str(appID)]["data"]["price_overview"]["initial"]):
        initial_price.append(nums)
        count += 1
    if count == 3:
        initial_price.insert(1, ".")
    else:
        initial_price.insert(2, ".")
    count = 0
    final_price = []
    for nums in str(rjson[str(appID)]["data"]["price_overview"]["final"]):
        final_price.append(nums)
        count += 1
    if count == 3:
        final_price.insert(1, ".")
    else:
        final_price.insert(2, ".")
    initial_price = float("".join(initial_price))
    final_price = float("".join(final_price))
    print("{0}\nThe initial price is {1} USD\nThe final price is {2} USD\nSo the discount is {3}%".format(game_name, initial_price, final_price, rjson[str(appID)]["data"]["price_overview"]["discount_percent"]))

    # check the target price and the final price
    if (((alert_on_discount[appID] == True) and (int(rjson[str(appID)]["data"]["price_overview"]["discount_percent"]) > 0)) and (target_price[appID] >= final_price)):
        top = Tk()

        def quit():
            top.destroy()

        top.geometry("700x100")
        top.title("STEAM PRICE ALERT!")

        text = Text(top)
        text.insert(INSERT,
                    "{0} is on {2}% discount and at or under target price!\nThe current price is {1} USD".format(game_name,
                                                                                                                 final_price,
                                                                                                                 rjson[str(
                                                                                                                     appID)][
                                                                                                                     "data"][
                                                                                                                     "price_overview"][
                                                                                                                     "discount_percent"]))
        text.pack()
        text.tag_add("whole", "1.0", "1.999")
        text.tag_config("whole", justify="left")

        button = Button(top, text="OK", justify="center", command=quit)
        button.place(x=250, y=50)

        top.mainloop()

    # check if the game on sale
    elif (alert_on_discount[appID] == True) and (int(rjson[str(appID)]["data"]["price_overview"]["discount_percent"]) > 0):
        top = Tk()

        def quit():
            top.destroy()

        top.geometry("700x100")
        top.title("STEAM PRICE ALERT!")

        text = Text(top)
        text.insert(INSERT,
                    "{0} is on {2}% discount!\nThe current price is {1} USD".format(game_name, final_price, rjson[str(appID)]["data"]["price_overview"]["discount_percent"]))
        text.pack()
        text.tag_add("whole", "1.0", "1.999")
        text.tag_config("whole", justify="left")

        button = Button(top, text="OK", justify="center", command=quit)
        button.place(x=250, y=50)

        top.mainloop()

    # check if game is on discount and at or under target price
    elif target_price[appID] >= final_price:
        top = Tk()

        def quit():
            top.destroy()

        top.geometry("700x100")
        top.title("STEAM PRICE ALERT!")

        text = Text(top)
        text.insert(INSERT,
                    "{0} is at or under target price!\nThe current price is {1} USD".format(game_name, final_price))
        text.pack()
        text.tag_add("whole", "1.0", "1.999")
        text.tag_config("whole", justify="left")

        button = Button(top, text="OK", justify="center", command=quit)
        button.place(x=250, y=50)

        top.mainloop()

while True:
    c = 0
    print("")
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("")
    while c < len(appids):
        steam_price(appids[c])
        print("")
        c += 1
    time.sleep(3600)