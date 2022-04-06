from selenium import webdriver
import webbrowser
driver = webdriver.Chrome(r"C:\Users\lenovo\AppData\Local\Google\Chrome\Application\chromedriver.exe")
url = 'http://localhost:63342/pythonProjectWeather/weather/降雨积水路段.html'
driver.get(url)
driver.maximize_window()

