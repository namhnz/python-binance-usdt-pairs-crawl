from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd
import openpyxl
import os

print("Tool lấy danh sách các cặp USDT spot tren Binance")

# Khoi tao selenium
s = Service(ChromeDriverManager().install())
op = webdriver.ChromeOptions()
op.add_argument("--log-level=3")
op.add_argument(r"start-maximized")
# op.add_experimental_option("detach", True);
driver = webdriver.Chrome(service=s, options=op)
driver.maximize_window()

# Mo trang Spot USDT
print("Đang mở trang Spot USDT")
driver.get(r"https://www.binance.com/en/markets/spot-USDT")
sleep(3)

# Sap xep cac cap USDT theo khoi luong Market Cap
print("Đang thực hiện sắp xếp các cặp USDT theo khối lượng Market Cap...")
marketCapHeaderSortButton = driver.find_element(
    By.XPATH, r"/html/body/div[1]/div/div/main/div/div[2]/div/div/div[2]/div[2]/div/div[1]/div[6]/div")
# marketCapHeaderSortButton.click()  # Click lan dau la sap xep theo tang dan
driver.execute_script("arguments[0].click();", marketCapHeaderSortButton)
# marketCapHeaderSortButton.click()  # Click lan 2 la sap xep tu lon den be
driver.execute_script("arguments[0].click();", marketCapHeaderSortButton)
sleep(3)

# Bien dung de nhan bien khi nao da het trang
canMoveToNextPage = True


def LayCacDongDuLieuTuBang():
    global canMoveToNextPage

    # Hien thi vi tri trang dang lay du lieu
    pageNavigationBar = driver.find_element(By.CLASS_NAME, r"css-b0tuh4")
    allNavigationButtons = pageNavigationBar.find_elements(
        By.TAG_NAME, r"button")
    for navigationButon in allNavigationButtons:
        if navigationButon.get_attribute("disabled") != None and ("Page number" in navigationButon.get_attribute("aria-label")):
            print("Đang lấy dữ liệu các cặp USDT tại trang: " +
                  navigationButon.text)

        if navigationButon.get_attribute("disabled") != None and navigationButon.get_attribute("aria-label") == "Next page":
            canMoveToNextPage = False

    # # Lay tieu de cac cot trong bang
    # print("Đang lấy tiêu đề các cột dữ liệu trong bảng thống kê...")
    # tableHeader = driver.find_element(By.XPATH, r"/html/body/div[1]/div/div/main/div/div[2]/div/div/div[2]/div[2]/div/div[1]");
    # tableColumnHeaderContainers = tableHeader.find_elements(By.CLASS_NAME, r"css-1e8pqe6");
    # tableColumnHeaderTitleTexts = [];
    # for columnHeaderContainer in tableColumnHeaderContainers:
    #     divInsideHeaderContainers = columnHeaderContainer.find_elements(By.TAG_NAME, r"div");
    #     for divInsideHeader in divInsideHeaderContainers:
    #         if divInsideHeader.get_attribute(r"data-bn-type") == "text":
    #             tableColumnHeaderTitleTexts.append(divInsideHeader.get_attribute(r"title"));

    # Lay phan chua cac dong du lieu cac cap USDT
    print("Đang lấy phần tử chứa các dòng dữ liệu cặp USDT")
    tableDataContainer = driver.find_element(
        By.XPATH, r"/html/body/div[1]/div/div/main/div/div[2]/div/div/div[2]/div[2]/div/div[2]")

    print("Đang lấy các dòng chứa dữ liệu...")
    tableRowDataContainter = tableDataContainer.find_elements(
        By.CLASS_NAME, r"css-leyy1t")

    coinPairInfoList = []

    for rowDataContainer in tableRowDataContainter:
        # Lay ten coin/USDT
        coinNameText = rowDataContainer.find_element(
            By.CLASS_NAME, r"css-17wnpgm").text
        coinWithUSDTText = coinNameText + r"/USDT"

        # Lay gia tri Market Cap
        marketCapValueText = rowDataContainer.find_elements(
            By.CLASS_NAME, r"css-102bt5g")[2].text
        if marketCapValueText == "–":
            marketCapValueText = "0.0"
        else:
            marketCapValueText = marketCapValueText[1:]

        marketCapValueLong = 0.0
        if(marketCapValueText.endswith("M")):
            marketCapValueLong = float(
                marketCapValueText.replace(',', '')[:-1]) * 1000000
        else:
            marketCapValueLong = float(marketCapValueText.replace(',', ''))

        coinPairInfoList.append(
            [coinNameText, coinWithUSDTText, marketCapValueText, marketCapValueLong])

    # Chuyen sang trang moi de lay cac cap khac
    print("Đang chuyển sang trang tiếp theo")
    nextPageButton = driver.find_element(
        By.XPATH, r"/html/body/div[1]/div/div/main/div/div[2]/div/div/div[2]/div[3]/div/button[9]")
    # nextPageButton.click()
    driver.execute_script("arguments[0].click();", nextPageButton)
    sleep(1)

    # Tra ve danh sach cac cap USDT da lay duoc
    return coinPairInfoList

# Ghi du lieu vao file Excel


def GhiDuLieuVaoFileExcel(dataToWrite):
    df = pd.DataFrame(dataToWrite, index=range(len(dataToWrite) + 1)[1:], columns=[
                      r"Ten coin", r"Cap coin/USDT", r"Market Cap (Text)", r"Market Cap (Number)"])

    saveExcelFileName = r"binance_USDT_pair_list.xlsx"
    if os.path.exists(saveExcelFileName):
        os.remove(saveExcelFileName)
        print(
            f'Tìm thấy file {saveExcelFileName} đã có trước đó, đã tiến hành xoá file thành công')

    print(f'Đang ghi {len(dataToWrite)} dòng dữ liệu vào file Excel...')
    df.to_excel(saveExcelFileName, sheet_name="list")


def GhiDuLieuVaoFileText(dataToWrite):
    print("Đang ghi dữ liệu các cặp USDT có Market Cap > 50tr USD vào file text...")
    textWriteToFile = ""
    for dataLine in dataToWrite:
        if dataLine[3] > 50000000:
            coinUSDTPairText = f'"{dataLine[1]}"'
            textWriteToFile = textWriteToFile + coinUSDTPairText + ",\n"

    saveTextFileName = r"binance_USDT_pair_list_cap_over_50m.txt"
    if os.path.exists(saveTextFileName):
        os.remove(saveTextFileName)
        print(
            f'Tìm thấy file {saveTextFileName} đã có trước đó, đã tiến hành xoá file thành công')

    print(f'Đang các dòng dữ liệu vào file text...')
    with open(saveTextFileName, "w") as textFile:
        print(textWriteToFile, file=textFile)


# Chay vong lap de lay du lieu tu tat ca cac trang
allPairInfoListFromBinance = []

while(canMoveToNextPage):
    allPairInfoListFromBinance.extend(LayCacDongDuLieuTuBang())

# Ghi ket qua vao file Excel
GhiDuLieuVaoFileExcel(allPairInfoListFromBinance)

# Ghi ket qua cac cap USDT co Market Cap tren 50 trieu USD vao file text de copy
GhiDuLieuVaoFileText(allPairInfoListFromBinance)

# Dong selenium
print("Đang đóng cửa sổ Chrome")
driver.close()

print("Xong!")