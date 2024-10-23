from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
from pymongo import MongoClient  # Thêm pymongo để kết nối với MongoDB


# Cấu hình Chrome để chạy nền
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
client = MongoClient("mongodb://localhost:27017/") 
db = client['phone_database']
collection = db['phone_collection']

def get_element_text(driver, xpath):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text
    except Exception:
        return "Không tìm thấy"

def get_phones_links():
    links = []
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://cellphones.com.vn/mobile.html"
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        
        
        body = driver.find_element(By.TAG_NAME, "body")
        scroll_pause_time = 2  # Thời gian tạm dừng khi cuộn
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Cuộn trang xuống cuối
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Chờ trang tải
            time.sleep(scroll_pause_time)

            # Tính toán chiều cao mới sau khi cuộn
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # Nếu không có sự thay đổi về chiều cao trang, nghĩa là đã cuộn tới cuối
            if new_height == last_height:
                break
            last_height = new_height

        # Sau khi cuộn xuống hết trang, thu thập các liên kết sản phẩm
        list_links = driver.find_elements(By.CLASS_NAME, "product-info")

        for item in list_links:
            try:
                a_tag = item.find_element(By.TAG_NAME, "a")
                link = a_tag.get_attribute("href")
                if link not in links:  # Đảm bảo không thu thập trùng lặp
                    links.append(link)
            except Exception as e:
                print(f"Lỗi khi lấy liên kết sản phẩm: {e}")
                continue

        print(f"Tổng số liên kết sản phẩm tìm được: {len(links)}")

    except Exception as e:
        print(f"Lỗi khi truy cập trang: {e}")

    finally:
        driver.quit()

    return links
    
def get_phones_info(link):
    try:
            
        # Khoi tao webdriver
        driver = webdriver.Chrome(options=chrome_options)

        # Mở trang
        driver.get(link)

        # Đợi trang tải
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        
        scroll_pause_time = 2  # Tạm dừng 3 giây sau mỗi lần cuộn
        scroll_step = 1500  # Cuộn xuống 500px mỗi lần
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Cuộn xuống từng phần của trang
            driver.execute_script(f"window.scrollBy(0, {scroll_step});")

            # Chờ cho nội dung tải thêm
            time.sleep(scroll_pause_time)

            # Tính toán chiều cao mới của trang sau khi cuộn
            new_height = driver.execute_script("return document.body.scrollHeight")

            # Nếu không có sự thay đổi về chiều cao, nghĩa là đã cuộn tới cuối trang
            if new_height == last_height:
                break
            last_height = new_height
        # Lấy tên sản phẩm
        name = get_element_text(driver, "//h1")

        # Các thông số khác
        Camtruoc = get_element_text(driver, "//li[p[text()='Camera trước']]/div")
        KichThuocManHinh = get_element_text(driver, "//li[p[text()='Kích thước màn hình']]/div")
        CamSau = get_element_text(driver, "//li[p[text()='Camera sau']]/div")
        Chip = get_element_text(driver, "//li[p[text()='Chipset']]/div")
        Congnghe = get_element_text(driver, "//li[p[text()='Công nghệ NFC']]/div")
        DungluongRam = get_element_text(driver, "//li[p[text()='Dung lượng RAM']]/div")
        BoNho = get_element_text(driver, "//li[p[text()='Bộ nhớ trong']]/div")
        Pin = get_element_text(driver, "//li[p[text()='Pin']]/div")
        Sim = get_element_text(driver, "//li[p[text()='Thẻ SIM']]/div")
        Dophangiai = get_element_text(driver, "//li[p[text()='Độ phân giải màn hình']]/div")
        Tinhmanhinh = get_element_text(driver, "//li[p[text()='Công nghệ màn hình']]/div")
        Cpu = get_element_text(driver, "//li[p[text()='Loại CPU']]/div")

        # Lấy giá sản phẩm
        try:
            price = driver.find_element(By.XPATH, "//span[@class='text-price']").text
        except NoSuchElementException:
            try:
                price = driver.find_element(By.XPATH, "(//p[@class='tpt---sale-price'])[2]").text
            except:
                price = "Không tìm thấy giá"

        product_info = {
            "Tên sản phẩm": name,
            "Camera trước": Camtruoc,
            "Kích thước màn hình": KichThuocManHinh,
            "Camera sau": CamSau,
            "Chipset": Chip,
            "Công nghệ NFC": Congnghe,
            "Dung lượng RAM": DungluongRam,
            "Bộ nhớ trong": BoNho,
            "Pin": Pin,
            "Thẻ SIM": Sim,
            "Độ phân giải màn hình": Dophangiai,
            "Công nghệ màn hình": Tinhmanhinh,
            "Loại CPU": Cpu,
            "Giá sản phẩm": price,
        }
        collection.insert_one(product_info)
        print(f"Đã lưu sản phẩm: {name}")
        return product_info

    except Exception as e:
        print(f"Lỗi khi truy cập {link}: {e}")
        return None
    finally:
        driver.quit()

# Sử dụng các hàm
phone_links = get_phones_links()
print(f"Thu thập được {len(phone_links)} liên kết")

# Lấy thông tin từng sản phẩm
for link in phone_links:
    info = get_phones_info(link)
    if info:
        print(info)
