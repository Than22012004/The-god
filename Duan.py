from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from pymongo import MongoClient
from selenium.webdriver.common.keys import Keys
import time

# Cấu hình Chrome để chạy nền
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Kết nối với MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['phone_database']
collection = db['phone_collection']

def lay_text_phan_tu(driver, xpath):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element.text
    except Exception:
        return "Không tìm thấy"

def dong_popup(driver):
    try:
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "cancel-button-top"))
        )
        close_button.click()
        print("Đã đóng popup.")
    except TimeoutException:
        print("Không tìm thấy popup; tiếp tục.")

def lay_cac_link_dien_thoai():
    links = []
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://cellphones.com.vn/mobile.html"

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        
        # Cuộn liên tục để tải thêm sản phẩm cho đến khi "Xem thêm" không còn khả dụng
        while True:
            try:
                # Cố gắng đóng bất kỳ lớp phủ nào
                overlay = driver.find_element(By.CLASS_NAME, "header-overlay")
                driver.execute_script("arguments[0].style.display = 'none';", overlay)
            except NoSuchElementException:
                pass

            try:
                # Nhấp vào "Xem thêm" để tải thêm sản phẩm
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Xem thêm')]"))
                ).click()
                time.sleep(2)  # Chờ sản phẩm tải lên
            except TimeoutException:
                print("Đã tải hết sản phẩm.")
                break

        # Thu thập các liên kết sản phẩm
        list_links = driver.find_elements(By.CLASS_NAME, "product-info")
        for item in list_links:
            try:
                a_tag = item.find_element(By.TAG_NAME, "a")
                link = a_tag.get_attribute("href")
                if link not in links:
                    links.append(link)
            except NoSuchElementException:
                continue

        print(f"Tổng số liên kết sản phẩm tìm được: {len(links)}")

    except Exception as e:
        print(f"Lỗi khi truy cập trang: {e}")

    finally:
        driver.quit()

    return links

def lay_thong_tin_dien_thoai(link):
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get(link)
        dong_popup(driver)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        # Cuộn trang để đảm bảo tất cả thông tin sản phẩm được tải
        body = driver.find_element(By.TAG_NAME, "body")
        for _ in range(50):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.1)

        # Lấy thông tin sản phẩm
        ten = lay_text_phan_tu(driver, "//h1")
        Camtruoc = lay_text_phan_tu(driver, "//li[p[text()='Camera trước']]/div")
        KichThuocManHinh = lay_text_phan_tu(driver, "//li[p[text()='Kích thước màn hình']]/div")
        CamSau = lay_text_phan_tu(driver, "//li[p[text()='Camera sau']]/div")
        Chip = lay_text_phan_tu(driver, "//li[p[text()='Chipset']]/div")
        Congnghe = lay_text_phan_tu(driver, "//li[p[text()='Công nghệ NFC']]/div")
        DungluongRam = lay_text_phan_tu(driver, "//li[p[text()='Dung lượng RAM']]/div")
        BoNho = lay_text_phan_tu(driver, "//li[p[text()='Bộ nhớ trong']]/div")
        Pin = lay_text_phan_tu(driver, "//li[p[text()='Pin']]/div")
        Sim = lay_text_phan_tu(driver, "//li[p[text()='Thẻ SIM']]/div")
        Dophangiai = lay_text_phan_tu(driver, "//li[p[text()='Độ phân giải màn hình']]/div")
        Tinhmanhinh = lay_text_phan_tu(driver, "//li[p[text()='Công nghệ màn hình']]/div")
        Cpu = lay_text_phan_tu(driver, "//li[p[text()='Loại CPU']]/div")

        
        try:
            gia = driver.find_element(By.XPATH, "//span[@class='text-price']").text
        except NoSuchElementException:
            gia = "Giá liên hệ"

        thong_tin_san_pham = {
            "Tên sản phẩm": ten,
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
            "Giá sản phẩm": gia,
        }

        # Lưu vào MongoDB
        collection.insert_one(thong_tin_san_pham)
        print(f"Đã lưu sản phẩm: {ten}")
        return thong_tin_san_pham

    except Exception as e:
        print(f"Lỗi khi truy cập {link}: {e}")
        return None
    finally:
        driver.quit()

# Thực thi quá trình lấy dữ liệu
link_dien_thoai = lay_cac_link_dien_thoai()
print(f"Thu thập được {len(link_dien_thoai)} liên kết")

for link in link_dien_thoai:
    thong_tin = lay_thong_tin_dien_thoai(link)
    if thong_tin:
        print(thong_tin)
