from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from concurrent.futures import ThreadPoolExecutor

# Cấu hình Chrome để chạy nền
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Kết nối MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['phone_database']
collection = db['phones_collection']

def get_phones_links():
    links = []
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://cellphones.com.vn/mobile.html"

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        body = driver.find_element(By.TAG_NAME, "body")

        for k in range(60):  # Số lần thử click "Xem thêm" và tải thêm sản phẩm
            try:
                try:
                    # Xóa overlay nếu có
                    overlay = driver.find_element(By.CLASS_NAME, "header-overlay")
                    driver.execute_script("arguments[0].style.display = 'none';", overlay)
                except NoSuchElementException:
                    print("Không tìm thấy phần tử che khuất, tiếp tục nhấp vào nút 'Xem thêm'.")

                try:
                    WebDriverWait(driver, 10, poll_frequency=1).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Xem thêm')]"))
                    ).click()
                except TimeoutException:
                    pass
            except Exception as e:
                pass

        for i in range(50):
            body.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.01)

        list_links = driver.find_elements(By.CLASS_NAME, "product-info")

        for item in list_links:
            try:
                a_tag = item.find_element(By.TAG_NAME, "a")
                link = a_tag.get_attribute("href")
                if link not in links:
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
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        body = driver.find_element(By.TAG_NAME, "body")

        for i in range(60):
            body.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.01)

        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = ""

        try:
            gia = driver.find_element(By.CLASS_NAME, "tpt---price").text
        except:
            try:
                gia = driver.find_element(By.CLASS_NAME, 'product__price--show').text
            except:
                try:
                    gia = driver.find_element(By.CLASS_NAME, "tpt---sale-price").text
                except:
                    gia = ""

        try:
            kich_thuoc = driver.find_element(By.XPATH, "//li[p[text()='Kích thước màn hình']]/div").text
        except:
            kich_thuoc = ""

        try:
            CN_manhinh = driver.find_element(By.XPATH, "//li[p[text()='Công nghệ màn hình']]/div").text
        except:
            CN_manhinh = ""

        try:
            cam_truoc = driver.find_element(By.XPATH, '//li[p[text()="Camera trước"]]/div').text
        except:
            cam_truoc = ""

        try:
            cam_sau = driver.find_element(By.XPATH, "//li[p[text()='Camera sau']]/div").text
        except:
            cam_sau = ""

        try:
            chip_set = driver.find_element(By.XPATH, "//li[p[text()='Chipset']]/div").text
        except:
            chip_set = ""

        try:
            NFC = driver.find_element(By.XPATH, "//li[p[text()='Công nghệ NFC']]/div").text
        except:
            NFC = ""

        try:
            ram = driver.find_element(By.XPATH, "//li[p[text()='Dung lượng RAM']]/div").text
        except:
            ram = ""

        try:
            rom = driver.find_element(By.XPATH, "//li[p[text()='Bộ nhớ trong']]/div").text
        except:
            rom = ""

        try:
            pin = driver.find_element(By.XPATH, "//li[p[text()='Pin']]/div").text
        except:
            pin = ""

        try:
            sim = driver.find_element(By.XPATH, "//li[p[text()='Thẻ SIM']]/div").text
        except:
            sim = ""

        try:
            do_phan_giai = driver.find_element(By.XPATH, "//li[p[text()='Độ phân giải màn hình']]/div").text
        except:
            do_phan_giai = ""

        try:
            tinh_nang_mh = driver.find_element(By.XPATH, "//li[p[text()='Tính năng màn hình']]/div").text
        except:
            tinh_nang_mh = ""

        try:
            cpu = driver.find_element(By.XPATH, "//li[p[text()='Loại CPU']]/div").text
        except:
            cpu = ""

        # Chèn dữ liệu vào MongoDB
        collection.insert_one({
            'Ten': name,
            'Gia': gia,
            'Kich_thuoc_man_hinh': kich_thuoc,
            'Cong_nghe_man_hinh': CN_manhinh,
            'Camera_truoc': cam_truoc,
            'Camera_sau': cam_sau,
            'Chipset': chip_set,
            'Cong_nghe_NFC': NFC,
            'Dung_luong_ram': ram,
            'Bo_nho_trong': rom,
            'Dung_luong_pin': pin,
            'The_SIM': sim,
            'Do_phan_giai_man_hinh': do_phan_giai,
            'Tinh_nang_man_hinh': tinh_nang_mh,
            'Loai_CPU': cpu
        })
        print(f"Đã lưu {name} vào MongoDB")

    except Exception as e:
        print(f"Lỗi khi truy cập {link}: {e}")

    finally:
        driver.quit()

phone_links = get_phones_links()
print(f"Thu thập được {len(phone_links)} liên kết sản phẩm")

# Xử lý dữ liệu song song
with ThreadPoolExecutor(max_workers=3) as executor:
    list(executor.map(get_phones_info, phone_links))

print("Hoàn thành việc lưu dữ liệu vào MongoDB.")
