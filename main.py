from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import uvicorn

app = FastAPI(
    title="MTMT Price Scraper",
    description="A simple API to scrape permanent plan price from MTMT buy page.",
    version="1.0.0"
)

@app.get("/price")
async def get_permanent_price():
    try:
        url = "https://auth.mtmt.tech/buy"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, "html.parser")

        # 查找包含“永久”的 li
        target_li = None
        for li in soup.find_all("li"):
            if "永久" in li.get_text(strip=True):
                target_li = li
                break

        if not target_li:
            return {
                "success": False,
                "price": None,
                "message": "未找到包含'永久'的选项"
            }

        # 查找价格
        parent = target_li.find_parent()
        price_element = parent.select_one(".price-text:not(.del)")
        if not price_element:
            price_element = soup.select_one(".price-text:not(.del)")

        if not price_element:
            return {
                "success": False,
                "price": None,
                "message": "未找到价格元素"
            }

        price = price_element.get_text(strip=True)

        return {
            "success": True,
            "price": price,
            "message": "成功获取价格"
        }

    except Exception as e:
        return {
            "success": False,
            "price": None,
            "message": f"抓取失败: {str(e)}"
        }

# 仅用于本地运行
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)