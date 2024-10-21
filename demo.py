from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import time
from pymongo import MongoClient

# Kết nối tới MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Đảm bảo MongoDB đang chạy trên localhost
db = client["mobile_data"]  # Tên cơ sở dữ liệu
collection = db["products"]  # Tên bộ sưu tập

# Thiết lập WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
url = "https://cellphones.com.vn/mobile.html"
driver.get(url)

# Đợi trang tải
time.sleep(3)

try:
    # Cuộn xuống cuối trang để tải thêm sản phẩm liên tục . cái này  GPT nhé 
    SCROLL_PAUSE_TIME = 2
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Cuộn xuống cuối trang
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Đợi trang tải thêm nội dung
        time.sleep(SCROLL_PAUSE_TIME)
        # Tính chiều cao mới của trang và so sánh với chiều cao cũ
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Nếu không có thay đổi về chiều cao, nghĩa là đã tải hết sản phẩm
            break
        last_height = new_height

    # tương tự hoạ sĩ
    product_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'product-item')]")
    print(f"Số lượng sản phẩm tìm thấy: {len(product_elements)}")

    # Duyệt qua từng sản phẩm và lấy dữ liệu
    for product in product_elements:
        try:
            # Lấy đường dẫn đến trang sản phẩm
            link = product.find_element(By.XPATH, ".//a").get_attribute("href")
            driver.get(link)  # Truy cập vào trang sản phẩm

            # Đợi trang tải
            time.sleep(3)

            # Lấy tên sản phẩm
            name = driver.find_element(By.XPATH, "//h1").text

            if collection.find_one({"product_name": name}):
                print(f"Sản phẩm '{name}' đã tồn tại trong cơ sở dữ liệu. Bỏ qua.")
                driver.back()  # Quay lại trang danh sách sản phẩm
                continue

            # lấy box-info_box_price để lấy giá chuẩn không có giảm giá hay tăng giá 
            try:
                price = driver.find_element(By.XPATH, "//div[contains(@class, 'box-info__box-price')]//p").text
            except NoSuchElementException:
                price = "Không có giá"

            # ratting mà không có được :v
            
            try:
                reviews = driver.find_element(By.XPATH, "//div[@class='rating-total']//p").text
            except NoSuchElementException:
                reviews = "Không có đánh giá"
            try:
                comments= driver.find_element(By.XPATH,"//div[@class='content']//p").text
            except :
                comments=".."

            # lưu monggod
            product_data = {
                'product_name': name,
                'price': price,
                'reviews': reviews,
                'comments':comments
            }

            
            collection.insert_one(product_data)
            print(f"Đã lưu sản phẩm: {name}")

            driver.back()
            time.sleep(2)  #

        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu sản phẩm: {e}")
            driver.back()  # Đảm bảo quay lại trang danh sách nếu có lỗi
            continue

    print('Đã lưu tất cả ')

except Exception as e:
    print(f"Có lỗi xảy ra: {e}")

# Đóng trình duyệt
driver.quit()

# Đóng kết nối MongoDB
client.close()
