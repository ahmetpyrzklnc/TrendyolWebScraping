import time
import os
import requests
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

PRODUCT_CARD_SELECTOR = "div.p-card-wrppr.with-campaign-view"
PRODUCT_LINK_SELECTOR = "a"
PRODUCT_IMAGE_SELECTOR = "img"

DETAIL_IMAGE_SELECTOR = "div.base-product-image img"
THUMBNAIL_CONTAINER_SELECTOR = 'div[data-testid="sliderList"]'
THUMBNAIL_SELECTOR = "div.product-slide.thumbnail-feature"
FOCUSED_THUMBNAIL_SELECTOR = "div.product-slide.thumbnail-feature.focused"
ZOOM_IMAGE_SELECTOR = "div.js-image-zoom__zoomed-image"

class TrendyolScraper:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--start-maximized')
        self.options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.maximize_window()
        
        self.driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
        self.driver.execute_cdp_cmd('Network.clearBrowserCache', {})
        
        self.wait_time = lambda: random.uniform(0.5, 1)

        self.base_url = "https://www.trendyol-milla.com/sr?wb=101476,103500,143760,148061,165523,103124&lc=75&qt=trendyolmilla&st=trendyolmilla&os=1"
        self.wait = WebDriverWait(self.driver, 10)
        
        self.image_dir = "scraped_images_trendyol_shirts"
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
            
        self.debug_dir = os.path.join(self.image_dir, "debug")
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)
            
        self.product_details_dir = os.path.join(self.image_dir, "product_details")
        if not os.path.exists(self.product_details_dir):
            os.makedirs(self.product_details_dir)

    def wait_for_element(self, selector, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except TimeoutException:
            print(f"Element bulunamadı: {selector}")
            return None

    def wait_and_find_elements(self, selector, timeout=10):
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            )
            return elements
        except TimeoutException:
            print(f"Elementler bulunamadı: {selector}")
            return []

    def auto_scroll(self, max_scroll_count=3):
        try:
            time.sleep(0.5)
            
            scroll_count = 0
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while scroll_count < max_scroll_count:
                scroll_distance = random.randint(800, 1200)
                
                self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                time.sleep(0.3)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(0.5)
                    break
                    
                last_height = new_height
                scroll_count += 1
                
                if scroll_count >= max_scroll_count:
                    break
                    
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Scroll hatası: {str(e)}")

    def extract_high_quality_url(self, url):
        if not url:
            return None
        
        original_url = url
        print(f"\n🔍 Orijinal URL: {original_url}")
        
        if "mnresize/" in url:
            uuid_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', url)
            ty_path_match = re.search(r'(ty\d+/prod/.*?)/', url)
            
            if uuid_match and ty_path_match:
                uuid = uuid_match.group(1)
                ty_path = ty_path_match.group(1)
                new_url = f"https://cdn.dsmcdn.com/{ty_path}/{uuid}/1_org_zoom.jpg"
                print(f"👉 Direct high quality URL: {new_url}")
                return new_url
            else:
                url = re.sub(r'mnresize/\d+/\d+/', '', url)
                print(f"👉 Cleaned mnresize: {url}")
        
        if "_org_zoom" not in url and "_org." not in url:
            zoom_url = re.sub(r'_\d+\.jpg', '_1_org_zoom.jpg', url)
            print(f"👉 Changed to _org_zoom format: {zoom_url}")
            return zoom_url
        
        uuid_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', url)
        if uuid_match:
            uuid = uuid_match.group(1)
            ty_match = re.search(r'(ty\d+/.*?)/', url)
            if ty_match:
                ty_path = ty_match.group(1)
                new_url = f"https://cdn.dsmcdn.com/{ty_path}/{uuid}/1_org_zoom.jpg"
                print(f"👉 UUID format with _org_zoom: {new_url}")
                return new_url
        
        print(f"⭐ Final URL: {url}")
        return url

    def extract_background_image_url(self, element):
        try:
            style = element.get_attribute("style")
            if style and "background-image" in style:
                match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
                if match:
                    return match.group(1)
        except:
            pass
        return None

    def download_image(self, url, filename, product_details=False):
        if not url:
            print(f"İndirilecek URL boş: {filename}")
            return False
            
        try:
            print(f"İndiriliyor: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Referer': self.base_url,
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            save_dir = self.product_details_dir if product_details else self.image_dir
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            filepath = os.path.join(save_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"✅ Görsel kaydedildi: {filename} ({len(response.content) // 1024} KB)")
            return True
        except Exception as e:
            print(f"❌ İndirme hatası ({filename}): {str(e)}")
            return False

    def process_product_card(self, card, index):
        try:
            try:
                link = card.get_attribute("href")
                if not link:
                    link_element = card.find_element(By.TAG_NAME, "a")
                    link = link_element.get_attribute("href")
            except:
                try:
                    link_element = card.find_element(By.CSS_SELECTOR, "a")
                    link = link_element.get_attribute("href")
                except:
                    print(f"⚠️ Ürün {index} için link bulunamadı")
                    return
            
            try:
                img_element = card.find_element(By.TAG_NAME, "img")
                img_url = img_element.get_attribute("src")
            except:
                try:
                    img_element = card.find_element(By.CSS_SELECTOR, "img")
                    img_url = img_element.get_attribute("src")
                except:
                    print(f"⚠️ Ürün {index} için görsel bulunamadı")
                    img_url = None
            
            if link:
                print(f"✅ Ürün {index} linki: {link}")
                
                if img_url:
                    filename = f"product_{index}_main.jpg"
                    self.download_image(img_url, filename)
                
                self.process_product_detail(link, index)
            else:
                print(f"❌ Ürün {index} için link bulunamadı")
        except Exception as e:
            print(f"❌ Ürün kartı işleme hatası (ürün {index}): {str(e)}")

    def process_product_detail(self, url, product_index):
        try:
            print(f"\n🔍 Ürün {product_index} detay sayfası açılıyor: {url}")
            
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            time.sleep(1)
            
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(2)
            
            if not os.path.exists(self.debug_dir):
                os.makedirs(self.debug_dir)
            
            main_image_url = self.get_main_image_url()
            if main_image_url:
                print(f"✅ Ana görüntü URL'si: {main_image_url}")
                filename = f"{product_index:06d}_1.jpg"
                self.download_image(main_image_url, filename, product_details=True)
                print(f"📥 Ana görsel indirildi: {filename}")
            else:
                print("⚠️ Ana görüntü URL'si bulunamadı")
            
            slider = None
            try:
                slider = self.driver.find_element(By.CSS_SELECTOR, THUMBNAIL_CONTAINER_SELECTOR)
                print("✅ Slider bulundu: " + THUMBNAIL_CONTAINER_SELECTOR)
            except:
                print(f"Slider bulunamadı, alternatif seçiciler deneniyor...")
                time.sleep(1)
                
                for alt_selector in ['div[data-testid="sliderList"]', 'div[class*="sliderList"]', 'div[class*="carousel"]', 'div[class*="gallery"]']:
                    try:
                        slider = self.driver.find_element(By.CSS_SELECTOR, alt_selector)
                        print(f"✅ Slider alternatif seçici ile bulundu: {alt_selector}")
                        break
                    except:
                        continue
                
                if not slider:
                    print("⚠️ Slider bulunamadı, devam edilemiyor")
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    return
            
            thumbnails = []
            for selector in [THUMBNAIL_SELECTOR, 'div[class*="thumbnail"]', 'div.product-slide', 'div[class*="product-slide"]', 'div[class*="gallery-item"]', 'img[class*="thumbnail"]']:
                try:
                    thumbs = slider.find_elements(By.CSS_SELECTOR, selector)
                    if thumbs and len(thumbs) > 0:
                        thumbnails = thumbs
                        print(f"✅ {len(thumbnails)} thumbnail bulundu: {selector}")
                        break
                except:
                    continue
            
            if not thumbnails:
                for selector in ['div[class*="thumbnail"]', 'div.product-slide', 'div[class*="product-slide"]', 'div[class*="gallery-item"]', 'img[class*="thumbnail"]']:
                    try:
                        thumbs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if thumbs and len(thumbs) > 0:
                            thumbnails = thumbs
                            print(f"✅ {len(thumbnails)} thumbnail sayfada bulundu: {selector}")
                            break
                    except:
                        continue
            
            print(f"Ürün {product_index} için {len(thumbnails)} thumbnail bulundu")
            
            for i, thumbnail in enumerate(thumbnails[1:], 2):
                try:
                    print(f"\n👆 Thumbnail {i} işleniyor...")
                    
                    self.driver.execute_script("window.focus();")
                    time.sleep(0.5)
                    
                    self.driver.execute_script("""
                        arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});
                        window.scrollBy(0, -100);
                    """, thumbnail)
                    time.sleep(0.5)
                    
                    actions = ActionChains(self.driver)
                    actions.move_to_element(thumbnail).pause(0.5).perform()
                    
                    self.driver.execute_script("""
                        var event = new MouseEvent('mouseover', {
                            'view': window,
                            'bubbles': true,
                            'cancelable': true
                        });
                        arguments[0].dispatchEvent(event);
                    """, thumbnail)
                    time.sleep(0.5)
                    
                    click_success = False
                    
                    try:
                        actions = ActionChains(self.driver)
                        actions.move_to_element(thumbnail).pause(0.3).click().perform()
                        time.sleep(0.8)
                        print("✅ ActionChains ile thumbnail'a tıklandı")
                        click_success = True
                    except Exception as e:
                        print(f"⚠️ ActionChains tıklama başarısız: {str(e)}")
                    
                    if not click_success:
                        try:
                            self.driver.execute_script("""
                                var clickEvent = new MouseEvent('mousedown', {
                                    'view': window, 'bubbles': true, 'cancelable': true, 'button': 0
                                });
                                arguments[0].dispatchEvent(clickEvent);
                                
                                arguments[0].click();
                                
                                var upEvent = new MouseEvent('mouseup', {
                                    'view': window, 'bubbles': true, 'cancelable': true, 'button': 0
                                });
                                arguments[0].dispatchEvent(upEvent);
                            """, thumbnail)
                            time.sleep(0.8)
                            print("✅ JavaScript ile thumbnail'a tıklandı")
                            click_success = True
                        except Exception as e:
                            print(f"⚠️ JavaScript tıklama başarısız: {str(e)}")
                    
                    if not click_success:
                        try:
                            thumbnail.click()
                            time.sleep(0.8)
                            print("✅ Normal tıklama ile thumbnail'a tıklandı")
                            click_success = True
                        except Exception as e:
                            print(f"⚠️ Normal tıklama başarısız: {str(e)}")
                    
                    if not click_success:
                        try:
                            child_elements = thumbnail.find_elements(By.CSS_SELECTOR, "img, span, div")
                            if len(child_elements) > 0:
                                child_elements[0].click()
                                time.sleep(0.8)
                                print("✅ Alt element üzerinden tıklama başarılı")
                                click_success = True
                        except Exception as e:
                            print(f"⚠️ Alt element tıklama başarısız: {str(e)}")
                    
                    if not click_success:
                        try:
                            self.driver.execute_script("""
                                arguments[0].focus();
                                var clickEvent = new Event('click', {bubbles: true});
                                arguments[0].dispatchEvent(clickEvent);
                                var changeEvent = new Event('change', {bubbles: true});
                                arguments[0].dispatchEvent(changeEvent);
                            """, thumbnail)
                            time.sleep(0.8)
                            print("✅ DOM olayları doğrudan tetiklendi")
                            click_success = True
                        except Exception as e:
                            print(f"⚠️ DOM olay tetikleme başarısız: {str(e)}")
                    
                    new_image_url = self.get_main_image_url()
                    if new_image_url:
                        print(f"✅ Yeni görüntü URL'si: {new_image_url}")
                        filename = f"{product_index:06d}_{i}.jpg"
                        self.download_image(new_image_url, filename, product_details=True)
                        print(f"📥 Thumbnail {i} görseli indirildi")
                    else:
                        print(f"⚠️ Thumbnail {i} için görüntü URL'si bulunamadı")
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"⚠️ Thumbnail {i} işleme hatası: {str(e)}")
            
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
        except Exception as e:
            print(f"❌ Detay sayfası işleme hatası: {str(e)}")
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass

    def get_main_image_url(self):
        try:
            zoom_selectors = [
                'div.js-image-zoom__zoomed-image',
                'div[class*="js-image-zoom"]',
                'div[class*="zoom"]',
                'div.js-image-zoom',
                'div.js-image-zoom__zoomed-area'
            ]
            
            for selector in zoom_selectors:
                try:
                    zoom_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    style = zoom_element.get_attribute("style")
                    
                    bg_match = re.search(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
                    if bg_match:
                        url = bg_match.group(1)
                        if url and ('_org_zoom.jpg' in url or '_org.jpg' in url):
                            print(f"✅ Zoom elementinden URL bulundu ({selector})")
                            return url
                except:
                    continue
                
            url = self.driver.execute_script("""
                var elements = document.querySelectorAll('*');
                for (var i = 0; i < elements.length; i++) {
                    var style = window.getComputedStyle(elements[i]);
                    var bgImage = style.backgroundImage;
                    if (bgImage && bgImage !== 'none') {
                        var matches = bgImage.match(/url\\(['"]?(.*?)['"]?\\)/);
                        if (matches && matches[1] && (matches[1].includes('_org_zoom.jpg') || matches[1].includes('_org.jpg'))) {
                            return matches[1];
                        }
                    }
                }
                return null;
            """)
            
            if url:
                print("✅ JavaScript ile yüksek çözünürlüklü URL bulundu")
                return url
            
            main_img = self.driver.find_element(By.CSS_SELECTOR, DETAIL_IMAGE_SELECTOR)
            if main_img:
                src = main_img.get_attribute("src")
                if src:
                    if '_org_zoom.jpg' not in src and '_org.jpg' not in src:
                        uuid_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', src)
                        ty_path_match = re.search(r'(ty\d+/prod/.*?)/', src)
                        
                        if uuid_match and ty_path_match:
                            uuid = uuid_match.group(1)
                            ty_path = ty_path_match.group(1)
                            return f"https://cdn.dsmcdn.com/{ty_path}/{uuid}/1_org_zoom.jpg"
                        else:
                            return src.replace('_1.jpg', '_1_org_zoom.jpg').replace('mnresize/128/192/', '')
                    return src
                
            all_images = self.driver.find_elements(By.TAG_NAME, "img")
            for img in all_images:
                try:
                    src = img.get_attribute("src")
                    if src and ('_org_zoom.jpg' in src or '_org.jpg' in src):
                        print("✅ Tüm img elementlerinden yüksek çözünürlüklü URL bulundu")
                        return src
                except:
                    continue
                
            return None
        except Exception as e:
            print(f"⚠️ Görüntü URL'si alma hatası: {str(e)}")
            return None

    def scrape_products(self):
        try:
            total_pages = 48
            start_page = 1
            pages_to_scrape = total_pages
            
            product_counter = 0
            
            for page in range(start_page, pages_to_scrape + 1):
                page_url = f"{self.base_url}&pi={page}"
                
                print(f"\n📄 Sayfa {page}/{pages_to_scrape} açılıyor: {page_url}")
                
                self.driver.get(page_url)
                time.sleep(1)
                
                wait = WebDriverWait(self.driver, 15)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PRODUCT_CARD_SELECTOR)))
                
                self.auto_scroll(max_scroll_count=3)
                
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        product_cards = self.driver.find_elements(By.CSS_SELECTOR, PRODUCT_CARD_SELECTOR)
                        if product_cards:
                            print(f"✅ Sayfa {page}: {len(product_cards)} ürün bulundu.")
                            break
                    except:
                        if retry < max_retries - 1:
                            print(f"⚠️ Ürün kartları bulunamadı, yeniden deneniyor... (Deneme {retry+1}/{max_retries})")
                            time.sleep(1)
                            self.driver.refresh()
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PRODUCT_CARD_SELECTOR)))
                        else:
                            print(f"❌ Sayfa {page} için ürün kartları bulunamadı, sonraki sayfaya geçiliyor.")
                            continue
                
                for i, card in enumerate(product_cards):
                    try:
                        print(f"\n🔄 Ürün işleniyor: {i+1}/{len(product_cards)} (Toplam: {product_counter+1})")
                        self.process_product_card(card, product_counter)
                        product_counter += 1
                    except Exception as e:
                        print(f"❌ Ürün işleme hatası (ürün {product_counter}): {str(e)}")
                        continue
                    
                    time.sleep(self.wait_time())
                
                print(f"✅ Sayfa {page}/{pages_to_scrape} tamamlandı. Toplam işlenen ürün: {product_counter}")
                
                time.sleep(self.wait_time())
                
            print(f"\n✅ Scraping tamamlandı! Toplam {product_counter} ürün işlendi.")
            
        except Exception as e:
            print(f"❌ Scraping hatası: {str(e)}")
        finally:
            self.driver.quit()

def main():
    scraper = TrendyolScraper()
    scraper.scrape_products()

if __name__ == "__main__":
    main()