import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

def scrape_price() -> Dict[str, Any]:
    try:
        url = "https://auth.mtmt.tech/buy"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")

        # 查找“永久”套餐
        target_li = None
        for li in soup.find_all("li"):
            if "永久" in li.get_text(strip=True):
                target_li = li
                break

        if not target_li:
            return {"success": False, "price": None, "message": "未找到'永久'套餐"}

        # 查找价格
        parent = target_li.find_parent()
        price_element = parent.select_one(".price-text:not(.del)")
        if not price_element:
            price_element = soup.select_one(".price-text:not(.del)")

        if not price_element:
            return {"success": False, "price": None, "message": "未找到价格元素"}

        price = price_element.get_text(strip=True)

        return {"success": True, "price": price, "message": "获取成功"}

    except Exception as e:
        return {"success": False, "price": None, "message": f"错误: {str(e)}"}


# Vercel Serverless Function 入口
def handler(request):
    data = scrape_price()
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS"
        },
        "body": data
    }


# 支持 OPTIONS 请求（CORS）
def handler_options(request):
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    }


# Vercel 入口点
def main(request):
    if request.method == "OPTIONS":
        return handler_options(request)
    return handler(request)