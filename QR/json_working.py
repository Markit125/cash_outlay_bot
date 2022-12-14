from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import os
import time

import json
import glob


def download_json(qr_code_line):
    
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    firefox_profile.set_preference("browser.download.folderList", 2)
    firefox_profile.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_profile.set_preference("browser.download.dir", f'{os.getcwd()}')
    firefox_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

    driver = webdriver.Firefox(
                            executable_path=GeckoDriverManager().install(),
                            firefox_profile=firefox_profile
                        )
    driver.maximize_window()

    try:
        driver.get('https://proverkacheka.com/#b-checkform_tab-qrraw')

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Строка")))
        driver.execute_script("window.stop();")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "Строка"))).click()
        
        qr_input = driver.find_element(by=By.ID, value='b-checkform_qrraw')
        qr_input.clear()
        qr_input.send_keys(qr_code_line)
        blank_space = driver.find_element(by=By.XPATH,
                    value="//div[contains(@class, 'page-header')]")

        time.sleep(1)
        blank_space.click()

        check_buttons = driver.find_elements(by=By.XPATH,
                    value="//button[contains(@class, 'b-checkform_btn-send')]")

        yoffset = 500
        action=ActionChains(driver)

        action.move_to_element_with_offset(to_element=check_buttons[-1], yoffset=yoffset, xoffset=2)
        check_buttons[-1].click()
        time.sleep(1)

        success = False

        for _ in range(3):
            try:
                ads = driver.find_elements(By.CLASS_NAME, "b-footer_adv-close")
                if ads != []:
                    ads[0].click()

            except Exception as ex:
                print(f"\nERR with advertize closing\n{ex}\n")
            
            try:
                element = driver.find_element(By.XPATH, "//button[@class='btn btn-primary btn-sm dropdown-toggle']")
                action.move_to_element_with_offset(to_element=element, yoffset=yoffset, xoffset=2)
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                    "//button[@class='btn btn-primary btn-sm dropdown-toggle']"))).click()

                element = driver.find_element(by=By.LINK_TEXT, value='JSON')
                action.move_to_element_with_offset(to_element=element, yoffset=yoffset, xoffset=2)
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, "JSON"))).click()

                success = True
                break

            except Exception as ex:
                print(f"\nERR\n{ex}\n")
                time.sleep(1)

        if success:
            return 'Got it'
        else:
            return 'Try it again'
        
    except Exception as ex:
        print('\nERROR\n\n', ex)
        return 'Somthing went wrong'
        
    finally:
        driver.close()
        driver.quit()


def extract_json():
    try:
        filename = glob.glob('check*.json')[0]
        with open(filename, 'r') as f:
            data = json.load(f)['items']
        os.remove(filename)
        return data
    except:
        return None


def main():
    extract_json()


if __name__ == '__main__':
    main()