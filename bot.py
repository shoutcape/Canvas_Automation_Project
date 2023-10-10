
#Automaatio kirjastot
import os
from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.Vault import FileSecrets
import time


#UI kirjastot
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal, QWaitCondition, QMutex, QObject
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QIcon

import sys

browser = Selenium()

#Luodaan suhteellinen polku palautuskansiolle, jotta se toimii myös muilla koneilla
home_directory = os.path.expanduser("~")
desktop_directory = os.path.join(home_directory, 'Desktop')
#Varmista että työpöydällä on kansio nimeltä Kurssienpalautukset
palautukset = os.path.join(desktop_directory, 'Kurssienpalautukset')


url = "https://tunnistus.laurea.fi/adfs/ls/?SAMLRequest=fZLNbsIwEITvfYrI95AQgiAWiURBVZFoi4D20EvlGAOWnDX1rvvz9jWBqvTC0eud%2FXbGHqFozIGPPe1hqd69Qoq%2BGgPI24uSeQfcCtTIQTQKOUm%2BGj%2FMedZJ%2BcFZstIadiG5rhCIypG2wKLZtGRvslvnuRpu4sG2TuM8K%2FqxGPYGsay7%2FWGa50VdFCx6UQ6DpmRhRBAiejUDJAEUSmnWi9MizgbrdMizjOeDVxZNgw8NglrVnuiAPEnIA2gkjx0jvFOis9WJ2GwxMZiwaPy72sQC%2Bka5lXIfWqrn5fxvhBTwIS71xu40JEfjLFqc47jVsNGwu55EfWpCfr9eL%2BLF02rNqtFxDm%2F9ueqIDMQzSge%2FzksKh460TUvMRsmlYHR6yseAmk0X1mj5Hd1Z1wi6vsmxojfxtm3l5ASgVkAhEWPs5yTQSZUs0BVLqhPy%2F4epbn4A&SigAlg=http%3A%2F%2Fwww.w3.org%2F2001%2F04%2Fxmldsig-more%23rsa-sha256&Signature=xqm9r%2FSVmDb3nxNYYDuJapmDE%2BLzzcu5FYVui%2BQuq3063kIlXDlv8hBVrudJut1xxyjgr14tTRGCj%2FDevnxhDdHUkvI6HsiYvXi9AKahnYNzfouV8vh58EzGDs0E9mocKYA225OFp7kbZAA%2FM4tnwdLYIXGp6HzHgR3MylXvKBpwqecXCov%2Fv1zjQppFbNoGjYGcEtWrOveGAxAkJc4AnWfU5U0yCYAVL6v1surv9GK8hGnzY%2FBoEoYvxGy2q1HlbJC63mCN1hHa6X2XXAdUlP40tASz10cthjHQLZ07r2vpJJl4DEabUildrWpjSmFLks2uobgS%2F5KjBKw%2FNBv3jQ%3D%3D"

    
class WorkerThread(QThread):
    finished = pyqtSignal()
    signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        
    def create_folder(self):
        if os.path.exists(palautukset):
            print("Palautuskansio on jo olemassa")
        else:
            os.mkdir(palautukset)
            print("palautuskansio luotu")
        
    def open_folder(self):
        try:
            os.startfile(palautukset)
        except: 
            print("Kansiota ei löydy")

 
    def run(self):

        try:
            #original_stdout = sys.stdout
            #sys.stdout = CustomStream(self.terminal)
            


            
            self.open_site()
            self.login()
            self.get_courses()
            self.get_assignment_folders()
            self.check_and_return_submissions()
            #sys.stdout = original_stdout
        except:
            print("Tehtävän palautus epäonnistui, varmista palautuksen saatavuus")
        finally:
            self.close_all_browsers()
            self.finished.emit()
        
    
    def open_site(self):
        browser.open_chrome_browser(url)
        browser.set_browser_implicit_wait(2)


        
    def check_special_characters(self, var: str):
        erikoismerkit = "\/:*?<>|[]\""    
        for char in var:
            if char in erikoismerkit:
                var = var.replace(char, "")
        return var
    
    def check_alert(self):
        try:
            browser.alert_should_not_be_present()
        
        except:
            pass
    
    def login(self):
        #Aseta käyttäjätunnus ja salasana vault.json tiedostoon. user hakemistoon
        secrets = FileSecrets(os.path.join(home_directory, "vault.json"))
        credentials = secrets.get_secret("credentials")
        username = credentials["username"]
        password = credentials["password"]
        
        browser.input_text("id:userNameInput", username)
        browser.input_text("id:passwordInput", password)
        browser.submit_form()
                
    def get_courses(self):
        browser.click_element("id:global_nav_courses_link")
        time.sleep(1)
        lista = browser.get_webelements("css:#nav-tray-portal > span > span > div > div > div > div > div > ul:nth-child(3)")
        for kurssi_nimi in lista:
            kurssit = kurssi_nimi.text.splitlines()
            kurssit = ([elementti for elementti in kurssit if elementti != 'Syksy 2023'])
        # Varmistetaan että kurssikansion merkit ovat sallittuja
        for kurssi in kurssit:
            kurssi = self.check_special_characters(kurssi)
            kurssikansio = os.path.join(palautukset, f"{kurssi}")
            if not os.path.exists(kurssikansio):
                os.mkdir(kurssikansio)
                print(f"Kansio {kurssi} luotu")
                
        else:
            print("Kurssikansiot on luotu")
            
    def get_assignment_folders(self):
        kurssikansio = list(os.listdir(palautukset))
        for kurssi in kurssikansio:
            dir_list = os.listdir(os.path.join(palautukset, kurssi))
            if len(dir_list) == 0:
                browser.reload_page()
                browser.click_link("id:global_nav_courses_link")
                try:
                    browser.click_link(f"link:{kurssi}")
                    
                except:
                    #osittainen haku
                    alt_kurssi = kurssi.split(" ")
                    browser.click_element(f'xpath://a[contains(text(), "{alt_kurssi[-2]} {alt_kurssi[-1]}")]')
                    
                
                browser.click_link("class:assignments")
                
                tehtavalista = browser.get_webelements("class:ig-title")
                for element in tehtavalista:
                    tehtavat = element.text.splitlines()
                    tehtavat = [self.check_special_characters(tehtavat[0])]
                    os.mkdir(os.path.join(palautukset, kurssi, tehtavat[0]))
                    print("Luotu:", tehtavat[0])
                
            else:
                print(f"Tehtäväkansiot on jo luotu kohteeseen {kurssi}")
                
    def check_and_return_submissions(self):
        palautetut = 0
        kurssikansiot = list(os.listdir(palautukset))
        for kurssi in kurssikansiot:
            tehtavakansiot = list(os.listdir(os.path.join(palautukset, kurssi)))
            for tehtava in tehtavakansiot:
                if len(list(os.listdir(os.path.join(palautukset, kurssi, tehtava)))) != 0 and "Palautettu" not in  tehtava:
                    palautetut += 1
                    self.tiedostonimi = os.listdir(os.path.join(palautukset, kurssi, tehtava))[0]
                    print(f"Tehtava {tehtava} on valmiina palautukseen. Tiedostonimi: {self.tiedostonimi}")
                    browser.reload_page() #ladataan sivu uudelleen jotta kurssilistan voi avata
                    print("Ladataan sivua...")
                    self.check_alert()
                    browser.click_link("id:global_nav_courses_link")
                    try:
                        browser.click_link(f"link:{kurssi}")
                    except:
                        #osittainen haku
                        kurssi2 = kurssi.split(" ")
                        browser.click_element(f'xpath://a[contains(text(), "{kurssi2[-2]} {kurssi2[-1]}")]')
                        
                    browser.click_link("class:assignments")
                    
                    #luodaan self versiot jotka välitetään toiselle metodille.
                    self.tehtava = tehtava
                    self.kurssi = kurssi
                    tehtava2 = tehtava.split(" ")
                    try:
                        try:
                            #osiainen haku
                            tehtavasivu = browser.find_element(f'xpath=//a[contains(text(), "{tehtava2[-4]} {tehtava2[-3]} {tehtava2[-2]} {tehtava2[-1]}")]')
                        except:
                            #osittainen haku
                            tehtavasivu = browser.find_element(f'xpath=//a[contains(text(), "{tehtava2[-3]} {tehtava2[-2]} {tehtava[-1]}")]')
                    except:
                        #osittainen haku
                        tehtavasivu = browser.find_element(f'xpath=//a[contains(text(), "{tehtava2[-2]} {tehtava2[-1]}")]')
                    
                    browser.click_element(tehtavasivu)
                    #otsikko = getattr(browser, "get_text")("class:title")
                    otsikko = browser.get_text("tag:h1")
                    print(otsikko)
                    if self.check_special_characters(otsikko) != tehtava:
                        print("Tehtävän nimi ei täsmää. Tarkista tehtävän nimi ja yritä uudelleen")
                        print(f"Tehtävän nimi: {otsikko}")
                        print(f"Tehtävän kansio: {tehtava}")
                    else:
                        print("Tehtävän nimi sama kuin kansio. Jatketaan palautusta")
                        
                    #Aloita tehtävä
                    browser.click_element("css:#assignment_show > div.assignment-title > div.assignment-buttons > button")
                    
                    #luodaan palautettavan tiedoston sijainti
                    filelocation = os.path.join(palautukset, kurssi, tehtava, os.listdir(os.path.join(palautukset, kurssi, tehtava))[0])
                    
                    assignment_information = browser.get_webelements("css:#assignment_show > ul")
                    for info in assignment_information:
                        info = info.text.splitlines()
                    
                    info = info[0].split(" ")
                    #TODO: Tarkista onko tiedostotyyppi rajattu, jos on, voi suoraan lisätä tiedoston sivulle.
                    if "pdf" in info or "docx" in info:
                        #valitse tiedosto
                        print("Valitaan tiedosto...")
                        insertfile = browser.find_element("attachments[-1][uploaded_data]")
                        
                        #lähetetään tiedosto sivulle
                        insertfile.send_keys(filelocation)
                        print(f"Tiedoston {self.tiedostonimi} sijoitus ok")
                    else:
                    
                        #Lataa tiedosto
                        browser.click_element("css:#submit_online_upload_form > table > tbody > tr:nth-child(2) > td > div:nth-child(2) > div > button:nth-child(1)")
                        self.check_alert() #tarkistetaan onko alertti olemassa
                        
                        #valitse tiedosto
                        print("Valitaan tiedosto...")
                        insertfile = browser.find_element("name:attachments[0][uploaded_data]")
                        
                        #lähetetään tiedosto sivulle
                        insertfile.send_keys(filelocation)
                        print(f"Tiedoston {self.tiedostonimi} sijoitus ok")
                    
                    #TEHTÄVÄN PALAUTUS
                    self.signal.emit()
                    self.confirm_submission(self.tiedostonimi)
                    time.sleep(2)
                    
        if palautetut == 0:
            print("Ei palautettavia tehtäviä")
        if palautetut != 0:
            print(f"Palautettuja tehtäviä: {palautetut}")
                
    
    def confirm_submission(self, tiedostonimi):
        print(f"Lähetetäänkö tiedosto {tiedostonimi}")
        submit_button = browser.find_element("id:submit_file_button")
        window.mutex.lock()
        window.condition.wait(window.mutex)
        window.mutex.unlock()
        #print the return button element for testing purposes
        print("Tehtävä palautettu")
        
        os.rename(os.path.join(palautukset, self.kurssi, self.tehtava), os.path.join(palautukset, self.kurssi, "Palautettu " + self.tehtava))
        print(f"Kansion {self.kurssi} nimi muutettu")
        #activate this line of code to actually submit assignments
        #browser.click_element(submit_button)
            
        
    def close_all_browsers(self):
        browser.close_all_browsers()
        
    
        
        
        
#Käyttöliittymä
class window(QMainWindow):
    condition = QWaitCondition()
    mutex = QMutex()


    def __init__(self):
        super().__init__()
        loadUi("window.ui", self)
        self.worker_thread = WorkerThread()
        self.custom_stream = CustomStream()
        self.pixmap = QPixmap("canvasproject_small.png")
        self.setWindowIcon(QIcon("canvascircle_g0O_icon.ico"))

        
        self.stop_button.clicked.connect(self.close_application)
        self.start_button.clicked.connect(self.start_robot)
        self.send_button.clicked.connect(self.on_send_button_clicked)
        self.open_folder_button.clicked.connect(self.worker_thread.open_folder)
         
        self.create_folder_button.clicked.connect(self.worker_thread.create_folder)
        
        self.worker_thread.finished.connect(self.work_finished)
        self.worker_thread.signal.connect(self.activate_send_button)
        
        
        #Tällä saadaan tekstikenttä tulostamaan sys.stdout aka print
        self.custom_stream.append_text.connect(self.terminal.insertPlainText)
        sys.stdout = self.custom_stream
        
        self.logo.setPixmap(self.pixmap)


        
        
    def on_send_button_clicked(self):
    # Jatketaan workerthread luokan confirm_submission-metodin suorittamista
        self.condition.wakeOne()
        self.send_button.setEnabled(False)
        
    def activate_send_button(self):
        self.send_button.setEnabled(True)
                
    def start_robot(self):
        #Käynnistetään robotin suoritus ja laitetaan nappi pois käytöstä
        self.start_button.setEnabled(False)
        self.start_button.setText("Käynnissä")
        self.worker_thread.start()
        
    def confirm_submission(self):
        self.confirm_submission.emit("kyllä")
            
        
    def work_finished(self):
        self.start_button.setEnabled(True)
        self.start_button.setText("Käynnistä")
        
        
    def close_application(self):
        self.worker_thread.close_all_browsers()
        self.close()
        


#Tämä luokka on vastuussa siitä että sys.stdout tulostuu käyttöliittymän tekstikenttään
class CustomStream(QObject):
    append_text = pyqtSignal(str)

    
    def write(self, text):
        self.append_text.emit(text)
        
    def flush(self):
       # Tämä on tarpeen, jotta CustomStream noudattaa sys.stdout -liittymää
       pass

    
            


def main():
    try:
        app = QApplication(sys.argv)
        w = window()
        w.show()
        sys.exit(app.exec_())
    finally:
        browser.close_all_browsers()
    
if __name__ == "__main__":
    main()
    
    
    #TODO:
    # DONE 1. Tarkista onko tiedosto jo palautettu 
    # DONE 2. Palautettavan tiedoston eri tiedostotyypit saattavat
    # vaikuttaa valitse tiedosto napin saatavuuteen siksi olisi hyvä
    # lisätä tarkistus jotta voidaan toimia tiedostotyypin mukaan.