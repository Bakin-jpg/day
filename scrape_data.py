#!/usr/bin/env python3
import httpx
import json
import asyncio
from datetime import datetime
from pathlib import Path

BASE_URL = "https://kickass-anime.ru/api"
OUTPUT_DIR = Path("data")

class KickassAnimeScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        self.timeout = 30.0
    
    async def fetch_json(self, url: str):
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    
    async def scrape_home(self):
        data = await self.fetch_json(f"{BASE_URL}/anime")
        return data.get('result', [])
    
    async def scrape_schedule(self):
        return await self.fetch_json(f"{BASE_URL}/schedule")
    
    async def scrape_anime_detail(self, slug: str):
        return await self.fetch_json(f"{BASE_URL}/show/{slug}")
    
    async def scrape_episode(self, episode_slug: str):
        return await self.fetch_json(f"{BASE_URL}/episode/{episode_slug}")

async def main():
    scraper = KickassAnimeScraper()
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().isoformat()
    
    print("[1/3] Scraping anime list...")
    anime_list = await scraper.scrape_home()
    print(f"  âœ“ Found {len(anime_list)} anime")
    
    print("[2/3] Scraping schedule...")
    schedule = await scraper.scrape_schedule()
    print(f"  âœ“ Found {len(schedule)} scheduled anime")
    
    print("[3/3] Scraping details for top 10 anime...")
    details = []
    for anime in anime_list[:10]:
        try:
            detail = await scraper.scrape_anime_detail(anime['slug'])
            details.append(detail)
            print(f"  âœ“ {detail['title']}")
        except Exception as e:
            print(f"  âœ— Error scraping {anime.get('slug', 'unknown')}: {e}")
    
    # Save data
    output = {
        'timestamp': timestamp,
        'anime_list': anime_list,
        'schedule': schedule,
        'top_anime_details': details
    }
    
    output_file = OUTPUT_DIR / 'anime_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nâœ… Data saved to {output_file}")
    print(f"   Total size: {output_file.stat().st_size / 1024:.2f} KB")
    
    # Save individual files
    (OUTPUT_DIR / 'anime_list.json').write_text(json.dumps(anime_list, indent=2, ensure_ascii=False), encoding='utf-8')
    (OUTPUT_DIR / 'schedule.json').write_text(json.dumps(schedule, indent=2, ensure_ascii=False), encoding='utf-8')
    (OUTPUT_DIR / 'details.json').write_text(json.dumps(details, indent=2, ensure_ascii=False), encoding='utf-8')
    
    # Create latest update timestamp
    (OUTPUT_DIR / 'last_update.txt').write_text(timestamp)
    
    print("\nðŸ“¦ All files saved:")
    print("   - data/anime_data.json (combined)")
    print("   - data/anime_list.json")
    print("   - data/schedule.json")
    print("   - data/details.json")
    print("   - data/last_update.txt")

if __name__ == "__main__":
    asyncio.run(main())
