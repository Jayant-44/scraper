import cloudscraper
from bs4 import BeautifulSoup
import csv
import sys

def scrape_mdcomputers(search_term):
    base_url = "https://mdcomputers.in/index.php"
    params = {'route': 'product/search', 'search': search_term}
    
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })
    
    try:
        response = scraper.get(base_url, params=params)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Save the raw HTML to a file for manual inspection
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())
        
    print("✅ Saved raw HTML to 'debug.html' in your tasks folder.")
    return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Debugging: Check if Cloudflare completely blocked us
    page_title = soup.find('title').text.strip() if soup.find('title') else ""
    if "Just a moment" in page_title or "Cloudflare" in page_title:
        print("❌ Blocked by Cloudflare. The website has strict anti-bot protection active right now.")
        return []
        
    # Look for the most common OpenCart product classes
    products = soup.find_all('div', class_='product-layout')
    if not products:
        products = soup.find_all('div', class_='product-thumb')
    if not products:
        products = soup.find_all('div', class_='product-item-container')

    products_data = []

    for item in products:
        try:
            # Extract Title and URL
            title_tag = item.find('h4')
            if not title_tag:
                title_tag = item.find('div', class_='caption').find('h4') if item.find('div', class_='caption') else None
                
            if title_tag and title_tag.find('a'):
                name = title_tag.text.strip()
                link = title_tag.find('a')['href']
            else:
                continue

            # Extract Price
            price_div = item.find('p', class_='price') or item.find('div', class_='price')
            if price_div:
                price_new = price_div.find('span', class_='price-new')
                if price_new:
                    price = price_new.text.strip()
                else:
                    price = price_div.text.strip().split('\n')[0].strip()
            else:
                price = "Price not found"

            products_data.append({'Product Name': name, 'Price': price, 'URL': link})
        except Exception:
            continue
            
    return products_data

def save_to_csv(data, filename="products.csv"):
    if not data:
        print("No data to save.")
        return
        
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Successfully saved {len(data)} products to {filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        term = " ".join(sys.argv[1:])
    else:
        term = input("Enter search term (e.g., external harddrive): ")
        
    print(f"\nScraping MDComputers for '{term}'...")
    results = scrape_mdcomputers(term)
    
    if results:
        print("\n--- Preview ---")
        for idx, p in enumerate(results[:5], 1):
            print(f"{idx}. {p['Product Name']} | {p['Price']}")
        print("---------------\n")
        
        csv_filename = f"mdcomputers_{term.replace(' ', '_')}.csv"
        save_to_csv(results, csv_filename)
    else:
        print("No products found.")