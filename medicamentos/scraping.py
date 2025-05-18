
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from .models import Medicamento
from django.db import transaction
from urllib.parse import quote_plus
from webdriver_manager.chrome import ChromeDriverManager

def scrape_cruz_verde(query: str):
    print(f"🔍 Iniciando scraping de Cruz Verde para «{query}»…")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    # 1) Codifica el término para URL y construye la ruta de búsqueda
    encoded = quote_plus(query)
    url = f"https://www.cruzverde.com.co/search?query={encoded}"
    driver.get(url)

    # 2) Cierra popups si hay (cookies, región…)
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.close-cookie"))
        )
        btn.click()
    except:
        pass

    # 3) Espera a que aparezca al menos un producto
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "a.font-semibold"))
    )

    # 4) Forzar scroll para lazy loading (si fuera necesario varias veces)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    tarjetas = driver.find_elements(
        By.CSS_SELECTOR,
        "div.relative.h-full.bg-white.border.rounded-sm.border-gray"
    )
    print(f"👍 Encontré {len(tarjetas)} tarjetas de producto.")

    with transaction.atomic():
        Medicamento.objects.all().delete()
        for tarjeta in tarjetas:
            try:
                laboratorio = tarjeta.find_element(
                    By.XPATH,
                    ".//div[contains(@class,'italic') and contains(@class,'uppercase')]"
                ).text.strip()
                nombre = tarjeta.find_element(
                    By.CSS_SELECTOR, "a.font-semibold"
                ).text.strip()
                precio_text = tarjeta.find_element(
                    By.CSS_SELECTOR, "span.font-bold.text-prices"
                ).text
                precio = float(precio_text.replace('$','').replace('.','').strip())
                url_producto = tarjeta.find_element(
                    By.CSS_SELECTOR, "a.font-semibold"
                ).get_attribute("href")
                img_el = tarjeta.find_element(
                    By.CSS_SELECTOR,
                    "img.ng-star-inserted"  # o un selector más concreto si cambia
                 )
                imagen_url = img_el.get_attribute("src")
            except Exception as e:
                print(f"⚠️ Tarjeta ignorada: {e}")
                continue

            Medicamento.objects.create(
                laboratorio=laboratorio,
                nombre=nombre,
                precio=precio,
                url=url_producto,
                imagen_url=imagen_url,
                fuente= "CruzVerde"
            )

    driver.quit()
    total = Medicamento.objects.count()
    print(f"✅ Scraping completado, {total} medicamentos guardados.")


def scrape_la_rebaja(query: str):
    print(f"🔍 Iniciando scraping de La Rebaja para «{query}»…")
    
    # 1) Configura ChromeOptions
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")                      # Modo headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    options.add_argument("--ignore-certificate-errors")     # Ignorar errores SSL
    options.add_argument("--ignore-ssl-errors=yes")
    options.set_capability("acceptInsecureCerts", True)

    # 2) Suprimir mensajes de logging y DevTools
    #    Excluir el switch que activa el logging por defecto en ChromeDriver :contentReference[oaicite:0]{index=0}
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    #    Desactivar la extensión de automatización para evitar logs extra
    options.add_experimental_option("useAutomationExtension", False)
    
    # 3) Crear el driver con nivel de log reducido (solo errores)
    service = Service(ChromeDriverManager().install(), log_level=3)  # log_level=3 → ERROR únicamente :contentReference[oaicite:1]{index=1}
    driver = webdriver.Chrome(service=service, options=options)
    
    # 4) Codifica el término y navega
    encoded = quote_plus(query)
    url = f"https://www.larebajavirtual.com/{encoded}?_q={encoded}&map=ft"
    driver.get(url)
    
    # 5) Cierra popups si hay (cookies, región…)
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.close-cookie"))
        )
        btn.click()
    except:
        pass
    
    # 6) Espera a que aparezca al menos un producto
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "section.vtex-product-summary-2-x-container"))
    )
    
    # 7) Forzar scroll para lazy loading
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    
    productos = driver.find_elements(By.CSS_SELECTOR, "section.vtex-product-summary-2-x-container")
    print(f"👍 Encontré {len(productos)} productos.")
    
    resultados = []
    for prod in productos:
        try:
            nombre = prod.find_element(
                By.CSS_SELECTOR,
                "span.vtex-product-summary-2-x-productBrand"
            ).text.strip()
            
            precio_text = prod.find_element(
                By.CSS_SELECTOR,
                "span.vtex-product-price-1-x-sellingPriceValue"
            ).text.strip()
            precio = float(precio_text.replace('$','').replace('.','').replace(',','').strip())
            
            enlace = prod.find_element(By.TAG_NAME, "a").get_attribute("href")
            imagen = prod.find_element(
                By.CSS_SELECTOR, 
                "img.vtex-product-summary-2-x-imageNormal"
            ).get_attribute("src")
            
        except Exception as e:
            print(f"⚠️ Producto ignorado: {e}")
            continue
        
        Medicamento.objects.create(
            nombre= nombre,
            precio= precio,
            url= enlace,
            imagen_url= imagen,
            fuente= "LaRebaja",
        )
    total=Medicamento.objects.count()
    driver.quit()
    print(f"✅ Scraping completado, {len(total)} productos encontrados.")
   
