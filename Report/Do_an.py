from lxml.etree import XPath
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import string
#import threading
import time
# Cấu hình Chrome để chạy nền
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")


d = pd.DataFrame({'Ten': [], 'Gia': [],'Kich_thuoc_man_hinh': [],'Cong_nghe_man_hinh': [],'Camera_truoc': [],'Camera_sau': [],'Chipset': [],'Cong_nghe_NFC': [],'Dung_luong_ram': [],'Bo_nho_trong': [],
                  'Dung_luong_pin': [],'The_SIM': [],'Do_phan_giai_man_hinh': [],'Tinh_nang_man_hinh': [],'Loai_CPU': [],})



def get_phones_links():
    links = []
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://cellphones.com.vn/mobile.html"

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        body = driver.find_element(By.TAG_NAME, "body")

        # Lặp lại quá trình click "Xem thêm" và cuộn trang để tải thêm sản phẩm
        for k in range(60):  # Số lần thử click "Xem thêm" và tải thêm sản phẩm
            try:
                # Lấy tất cả các button trên trang
                buttons = driver.find_elements(By.TAG_NAME, "a")

                try:
                    # Xóa overlay nếu có
                    overlay = driver.find_element(By.CLASS_NAME, "header-overlay")
                    driver.execute_script("arguments[0].style.display = 'none';", overlay)
                except NoSuchElementException:
                    print("Không tìm thấy phần tử che khuất, tiếp tục nhấp vào nút 'Xem thêm'.")

                # # Duyệt qua từng button và tìm nút "Xem thêm"
                # for button in buttons:
                #     if "Xem thêm" in button.text and "sản phẩm" in button.text:
                #         button.click()
                #         time.sleep(5)  # Chờ thêm sản phẩm tải lên
                #         break  # Thoát vòng lặp nếu đã click thành công
                try:
                    # Thử click vào nút 'Xem thêm'
                    WebDriverWait(driver, 10, poll_frequency=1).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Xem thêm')]"))
                    ).click()
                except TimeoutException:
                    pass
            except Exception as e:
                pass

        # Tiếp tục di chuyển xuống dưới trang để tải sản phẩm
        for i in range(50):
            body.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.01)

        # Lấy các liên kết sau khi đã cuộn và nhấp vào "Xem thêm"
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
# Tạo cơ sở dữ liệu
import sqlite3

# Create the database and table
conn = sqlite3.connect('phones.db')
c = conn.cursor()
try:
    c.execute('''
        CREATE TABLE IF NOT EXISTS phones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Ten TEXT,
            Gia TEXT,
            Kich_thuoc_man_hinh TEXT,
            Cong_nghe_man_hinh TEXT,
            Camera_truoc TEXT,
            Camera_sau TEXT,
            Chipset TEXT,
            Cong_nghe_NFC TEXT,
            Dung_luong_ram TEXT,
            Bo_nho_trong TEXT,
            Dung_luong_pin TEXT,
            The_SIM TEXT,
            Do_phan_giai_man_hinh TEXT,
            Tinh_nang_man_hinh TEXT,
            Loai_CPU TEXT
        )
    ''')

    # Confirm the table structure
    c.execute("SELECT * FROM phones")
    records = c.fetchall()
except Exception as e:
    print(e)
finally:
    conn.commit()
    conn.close()

# ham them
def them(name, gia, kich_thuoc, CN_manhinh, cam_truoc, cam_sau, chip_set, NFC, ram, rom, pin, sim, do_phan_giai, tinh_nang_mh, cpu):
    conn = sqlite3.connect('phones.db')
    c = conn.cursor()
    # them du lieu vao database
    c.execute('''
        INSERT INTO phones (
            Ten, Gia, Kich_thuoc_man_hinh, Cong_nghe_man_hinh, Camera_truoc, Camera_sau, Chipset,
            Cong_nghe_NFC, Dung_luong_ram, Bo_nho_trong, Dung_luong_pin, The_SIM, 
            Do_phan_giai_man_hinh, Tinh_nang_man_hinh, Loai_CPU
        ) VALUES (
            :Ten, :Gia, :Kich_thuoc_man_hinh, :Cong_nghe_man_hinh, :Camera_truoc, :Camera_sau, :Chipset,
            :Cong_nghe_NFC, :Dung_luong_ram, :Bo_nho_trong, :Dung_luong_pin, :The_SIM, 
            :Do_phan_giai_man_hinh, :Tinh_nang_man_hinh, :Loai_CPU
        )
    ''', {
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
    conn.commit()
    conn.close()



# Ham lay thong tin cua san pham
def get_phones_info(link):
    try:
        # Khoi tao webdriver
        driver = webdriver.Chrome(options=chrome_options)

        # mo trang
        driver.get(link)

        # Doi trang tai
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        body = driver.find_element(By.TAG_NAME, "body")
        # Tiếp tục di chuyển xuống dưới trang để tải sản phẩm
        for i in range(60):
            body.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.01)
        # Lay ten san pham
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = ""

        # Lấy giá sản phẩm
        try:
            # Thử tìm giá với "tpt---price"
            gia = driver.find_element(By.CLASS_NAME, "tpt---price").text
        except:
            try:
                # Nếu vẫn không tìm thấy,thu voi "text-price"
                gia = driver.find_element(By.CLASS_NAME, 'product__price--show').text
            except :
                try:
                    # Nếu không tìm thấy, thử với "tpt---sale-price"
                    gia = driver.find_element(By.CLASS_NAME, "tpt---sale-price").text
                except:
                    # Nếu không tìm thấy ở bất kỳ lớp nào, đặt giá trị mặc định là ""
                    gia = ""
        # # Lay hinh anh
        # try:
        #     pic = driver.find_element(By.XPATH, '//*[@id="v2Gallery"]/div/img').get_attribute("src")
        # except :
        #     # Trường hợp ngoại lệ khi không tìm thấy phần tử ở XPATH đầu tiên
        #     try:
        #         pic = driver.find_element(By.XPATH, '//*[@id="blockProductCTA"]/div[1]/div[2]/div/div[1]/div/img)').get_attribute("src")
        #     except :
        #         pic = ""

        # Thong so ky thuat

        # Kich thuoc man hinh
        try:
            kich_thuoc = driver.find_element(By.XPATH, "//li[p[text()='Kích thước màn hình']]/div").text

        except:
            kich_thuoc = ""

        # Cong nghe man hinh
        try:
            CN_manhinh = driver.find_element(By.XPATH, "//li[p[text()='Công nghệ màn hình']]/div").text
        except:
            CN_manhinh = ""
        # Camera truoc
        try:
            cam_truoc = driver.find_element(By.XPATH,'//li[p[text()="Camera trước"]]/div').text

        except:
            cam_truoc = ""
        # Camera sau
        try:
            cam_sau = driver.find_element(By.XPATH,"//li[p[text()='Camera sau']]/div").text
        except:
            cam_sau = ""
        #Chipset
        try:
            chip_set = driver.find_element(By.XPATH,"//li[p[text()='Chipset']]/div").text
        except:
            chip_set = ""


        #Cong nghe NFC
        try:
            NFC = driver.find_element(By.XPATH,"//li[p[text()='Công nghệ NFC']]/div").text
        except:
            NFC = ""

        #Dung luong ram
        try:
            ram = driver.find_element(By.XPATH,
                                      "//li[p[text()='Dung lượng RAM']]/div").text
        except:
            ram = ""

        #Bo nho trong
        try:
            rom = driver.find_element(By.XPATH,
                                      "//li[p[text()='Bộ nhớ trong']]/div").text
        except:
            rom = ""

        #Pin
        try:
            pin = driver.find_element(By.XPATH,
                                      "//li[p[text()='Pin']]/div").text
        except:
            pin = ""
        #The SIM
        try:
            sim = driver.find_element(By.XPATH,
                                      "//li[p[text()='Thẻ SIM']]/div").text
        except:
            sim = ""
        # Do phan giai man hinh
        try:
            do_phan_giai = driver.find_element(By.XPATH,"//li[p[text()='Độ phân giải màn hình']]/div").text
        except:
            do_phan_giai = ""
        #Tinh nang man hinh
        try:
            tinh_nang_mh = driver.find_element(By.XPATH,
                                      "//li[p[text()='Tính năng màn hình']]/div").text
        except:
            tinh_nang_mh = ""

        #Loai CPU
        try:
            cpu = driver.find_element(By.XPATH,
                                      "//li[p[text()='Loại CPU']]/div").text
        except:
            cpu = ""


        # # Tao dictionary chua tt ban nhac
        # phones = {'Ten': name, 'Gia': gia,'Kich_thuoc_man_hinh':kich_thuoc,'Cong_nghe_man_hinh':CN_manhinh,
        #           'Camera_truoc':cam_truoc,'Camera_sau':cam_sau,'Chipset':chip_set,'Cong_nghe_NFC':NFC,'Dung_luong_ram':ram,'Bo_nho_trong':rom,
        #           'Dung_luong_pin':pin,'The_SIM':sim,'Do_phan_giai_man_hinh':do_phan_giai,'Tinh_nang_man_hinh':tinh_nang_mh,'Loai_CPU':cpu}
        them(name, gia, kich_thuoc, CN_manhinh, cam_truoc, cam_sau, chip_set, NFC, ram, rom, pin, sim, do_phan_giai, tinh_nang_mh, cpu)
        return name, gia, kich_thuoc, CN_manhinh, cam_truoc, cam_sau, chip_set, NFC, ram, rom, pin, sim, do_phan_giai, tinh_nang_mh, cpu

    except Exception as e:
        print(f"Lỗi khi truy cập {link}: {e}")
        return None

    finally:
        driver.quit()


phone_links = get_phones_links()
print(f"Thu thập được {len(phone_links)} ")

# su dung ThreadPoolExecutorde xu li cac thong tin song song
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(get_phones_info, phone_links))

# # them ket qua vao DataFrame
# for phones in results:
#     if phones:
#         d = pd.concat([d, pd.DataFrame([phones])], ignore_index=True)

# file_name = 'phones.xlsx'
# d.to_excel(file_name, index=False)
print('Data đã được ghi thành công!!!!.')




# def popup_watcher(driver):
#     while True:
#         try:
#             # Kiểm tra và đóng pop-up
#             close_popup = driver.find_element(By.CLASS_NAME, "cancel-button-top")
#             close_popup.click()
#             print("Pop-up đã được đóng.")
#         except NoSuchElementException:
#             pass  # Không tìm thấy pop-up, tiếp tục kiểm tra
#         time.sleep(1)  # Kiểm tra mỗi giây
#
# # Khởi động thread theo dõi pop-up
# popup_thread = threading.Thread(target=popup_watcher, args=(driver,))
# popup_thread.daemon = True
# popup_thread.start()
