import os
import time
import unidecode
import selenium
import selenium.webdriver.support.ui
import selenium.webdriver.chrome.options
import selenium.webdriver.common.action_chains

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.support import expected_conditions as EC


DOWNLOAD_DIRECTORY = "download"


class Session:
    def __init__(self, act_doc_viewer=False):
        options = selenium.webdriver.chrome.options.Options()
        options.add_extension("ext_xpath_helper.crx")

        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--kiosk-printing")
        # options.add_argument("--no-sand-box")  # in testing phase
        # options.add_argument("--headless")  # in testing phase

        options.add_experimental_option("detach", True)
        prefs = {"download.default_directory": DOWNLOAD_DIRECTORY,
                 "savefile.default_directory": DOWNLOAD_DIRECTORY,
                 "download.prompt_for_download": False,
                 "plugins.always_open_pdf_externally": (not act_doc_viewer),
                 "safebrowsing_enabled": False  # in testing phase
                 }
        options.add_experimental_option("prefs", prefs)

        self.driver = selenium.webdriver.Chrome(options=options)

        self.driver.set_window_position(0, 0)
        self.driver.maximize_window()

        self.actions = selenium.webdriver.common.action_chains.ActionChains(self.driver)
        self.wait = selenium.webdriver.support.ui.WebDriverWait(self.driver, 60)

    def login_mail(self, email_user, email_pass):
        self.driver.get("https://sesp.pr.gov.br/")
        self.driver.implicitly_wait(5)
        self.driver.find_element(By.ID, "user").send_keys(email_user)
        self.actions.send_keys(Keys.TAB).perform()
        self.actions.send_keys(email_pass).send_keys(Keys.TAB).send_keys(Keys.RETURN).perform()
        self.wait.until(EC.url_matches("https://sesp.pr.gov.br/expressoMail1_2/index.php"))

    def prepare_email(self, subject, text, recipient, conf_reading=False):
        try:
            WebDriverWait(self.driver, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, "ui-dialog")))
            print("pop-up located")

            ok_button = self.driver.find_element(By.XPATH, "//button[span[text()='Ok']]")
            ok_button.click()

        except TimeoutException:
            print("no pop-up found")

        btn_new = "//tr[2]/td[@class='content-menu-td']/div[@class='em_div_sidebox_menu']/" \
                  "span[@class='em_sidebox_menu']"

        self.driver.find_element(By.XPATH, btn_new).click()

        self.driver.find_element(By.ID, "return_receipt_1").click() if conf_reading else None

        self.driver.find_element(By.ID, "to_1").send_keys(recipient)
        self.driver.find_element(By.ID, "subject_1").send_keys(subject)
        self.actions.send_keys(Keys.TAB).send_keys(text).perform()

    def attach_annexes_by_folder(self, folder_name, doc_name, send_only_if_all=True):
        folder_name = unidecode.unidecode(folder_name)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, "Annexes", folder_name, doc_name)

        annex = [path]

        flag = self.attach_annexes(paths_annexes=annex, send_only_if_all=send_only_if_all)

        return flag

    def attach_annexes(self, paths_annexes=None, send_only_if_all=True):
        link_annex = "//tr[10]/td[2]/a"
        paths_to_annex = [] if not paths_annexes else [p for p in paths_annexes if p is not None]

        for i, path in enumerate(paths_to_annex):
            self.driver.find_element(By.XPATH, link_annex).click()
            try:
                self.driver.find_element(By.ID, f"inputFile_1_{i + 1}").send_keys(path)
            except InvalidArgumentException:
                if send_only_if_all:
                    return 1
                else:
                    continue
        return 0

    def send(self):
        try:
            self.driver.find_element(By.ID, "send_button_1").click()
            self.wait.until(EC.invisibility_of_element_located((By.ID, "send_button_1")))
            return 1
        except TimeoutException:
            return 0

    def reset(self):
        self.driver.refresh()
        try:
            self.wait.until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
            self.wait.until(EC.invisibility_of_element_located((By.ID, "send_button_1")))
        except NoAlertPresentException:
            pass

    def print_page(self):
        self.driver.execute_script("window.print()")

    def save_receipt(self, subject):
        self.driver.find_element(By.ID, "lINBOX/Enviadostree_folders").click()
        time.sleep(2)
        self.driver.find_element(By.XPATH, f"//*[contains(text(), '{subject}')]").click()
        time.sleep(2)
        self.driver.find_element(By.XPATH, "//*[contains(text(), 'Mostrar detalhes')]").click()
        time.sleep(2)

        # before_files = os.listdir(_utils.paths.source)
        self.print_page()
        # file = _utils.control_download(before_files)
        # file = _utils.check_download()
        # os.rename(f"{_utils.paths.source}/{file}", f"{_utils.paths.source}/{new_file_name}.pdf")
        # os.rename(file, f"{_utils.paths.source}/{new_file_name}.pdf")

    def end_session(self):
        self.driver.quit()
