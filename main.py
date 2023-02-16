import config
from utils import proxyhandler
import requests, json, re, threading, time
import discord_webhook



def ping(title, url, size, price, img, stock):
    webhook = discord_webhook.DiscordWebhook(url=config.webhookURLs)
    embed = discord_webhook.DiscordEmbed(title=title, url=url, color=0xf9f8f6)
    embed.set_author(name="Aliexpress <3")
    embed.add_embed_field(name='Size', value=f'{size} (x{stock})')
    embed.add_embed_field(name='Price', value=price)
    embed.set_thumbnail(url=img)
    embed.set_footer(text="Aliexpress Restock Bot - lız#9999", icon_url="https://i.imgur.com/6lmp0Qo.jpeg")

    webhook.add_embed(embed)
    webhook.execute()


def getProduct(product_id):
    s = requests.Session()
    if config.use_proxies:
        s.proxies.update(proxyhandler.getProxy())

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'DNT': '1',
        'Connection': 'keep-alive',
    }

    r = s.get(f'https://aliexpress.us/item/{product_id}.html', headers=headers)
    r = r.text.split("window.runParams = {")[1].split("csrfToken")[0]
    r = r.split("data: ")[1]
    r = re.sub(r',\s{20,99}', "", r)
    r = json.loads(r)

    try:
        sizeNames = r["skuModule"]["productSKUPropertyList"][1]["skuPropertyValues"]

        variants = [{
            "id": x["skuIdStr"],
            "title": x["skuAttr"].split("#")[1].split(";")[0],
            "image": r["pageModule"]["imagePath"],
            "size": [y for y in sizeNames if str(y["propertyValueId"]) == x["skuPropIds"].split(",")[1]][0]["propertyValueDisplayName"],
            "price": str(x["skuVal"]["skuActivityAmount"]["value"]) + " " + x["skuVal"]["skuActivityAmount"]["currency"],
            "stock": x["skuVal"]["availQuantity"],
        }
            for x in r["skuModule"]["skuPriceList"]]

    except IndexError:  # doesnt have sizes
        variants = [{
            "id": x["skuIdStr"],
            "title": x["skuAttr"].split("#")[1].split(";")[0],
            "image": r["pageModule"]["imagePath"],
            "size": x["skuAttr"].split("#")[1].split(";")[0],
            "price": str(x["skuVal"]["skuActivityAmount"]["value"]) + " " + x["skuVal"]["skuActivityAmount"]["currency"],
            "stock": x["skuVal"]["availQuantity"],
        }
            for x in r["skuModule"]["skuPriceList"]]

    return {
        "title": r["titleModule"]["subject"],
        "url": f"https://aliexpress.com/item/{product_id}.html",
        "variants": [x for x in variants if x["stock"] > 0],
    }


def run(task):
    global pinged, delay

    while True:
        try:
            product = getProduct(task)
            for variant in product["variants"]:
                pid = variant["id"]

                if pid not in pinged:
                    print(f'Restock: {variant["title"]} <{variant["size"]}>')
                    ping(title=variant["title"], url=product["url"], size=variant["size"], price=variant["price"], img=variant["image"], stock=variant["stock"])
                    pinged.append(pid)

            time.sleep(delay)

        except Exception as e:
            print("Error:", e)
            time.sleep(delay)


def main():
    for task in config.productIDs:
        threading.Thread(target=run, args=(task,)).start()


if __name__ == '__main__':
    pinged = []
    delay = config.delay
    main()


