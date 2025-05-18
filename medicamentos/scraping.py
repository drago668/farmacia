
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .models import Medicamento
from django.db import transaction
from urllib.parse import quote_plus

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

def scrape_farmatodo(query: str):
    print(f"🔍 Iniciando scraping de Farmatodo para «{query}»…")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    encoded = quote_plus(query)
    url = f"https://www.farmatodo.com.co/buscar?product={encoded}&departamento=Todos&filtros="
    driver.get(url)

    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card-ftd"))
    )
    time.sleep(2)

    tarjetas = driver.find_elements(By.CSS_SELECTOR, "div.card-ftd")
    print(f"👍 Encontré {len(tarjetas)} tarjetas en Farmatodo.")

    for tarjeta in tarjetas:
        try:
            # Forzamos lazy-load de imagen
            driver.execute_script("arguments[0].scrollIntoView(true);", tarjeta)
            time.sleep(0.2)

            nombre      = tarjeta.find_element(By.CSS_SELECTOR, "p.text-title").text.strip()
            laboratorio = tarjeta.find_element(By.CSS_SELECTOR, "p.text-brand").text.strip()

            # Precio (normal u oferta)
            precio_el = tarjeta.find_elements(By.CSS_SELECTOR, "span.price__text-price") \
                       or tarjeta.find_elements(By.CSS_SELECTOR, "span.price__text-offer-price")
            if not precio_el:
                raise ValueError("Precio no encontrado")
            precio_text = precio_el[0].text
            precio = float(precio_text.replace('$','').replace('.','').strip())

            # URL del producto
            link_el = tarjeta.find_element(By.CSS_SELECTOR, "a.product-image__link")
            url_producto = link_el.get_attribute("href")

            # Imagen lazy-loaded
            img_el = tarjeta.find_element(By.CSS_SELECTOR, "img.product-image__image.lozad")
            imagen_url = img_el.get_attribute("data-src") or img_el.get_attribute("src")

        except Exception as e:
            print(f"⚠️ Tarjeta Farmatodo ignorada: {e}")
            continue

        Medicamento.objects.create(
            laboratorio = laboratorio,
            nombre      = nombre,
            precio      = precio,
            url         = url_producto,
            imagen_url  = imagen_url,
            fuente      = "Farmatodo"
        )

    driver.quit()
    print("✅ Scraping Farmatodo completado.")






"""def scrape_farmatodo(query: str):
    print(f"🔍 Iniciando scraping de Farmatodo para «{query}»…")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    # Construye la URL de búsqueda
    encoded = quote_plus(query)
    url = f"https://www.farmatodo.com.co/buscar?product={encoded}&departamento=Todos&filtros="
    driver.get(url)

    # Espera a que aparezcan las tarjetas
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card-ftd"))
    )
    time.sleep(2)

    tarjetas = driver.find_elements(By.CSS_SELECTOR, "div.card-ftd")
    print(f"👍 Encontré {len(tarjetas)} tarjetas en Farmatodo.")

    for tarjeta in tarjetas:
        try:
            # Nombre y laboratorio (siempre presentes)
            nombre = tarjeta.find_element(By.CSS_SELECTOR, "p.text-title").text.strip()
            laboratorio = tarjeta.find_element(By.CSS_SELECTOR, "p.text-brand").text.strip()

            # Precio: el primero que aparezca (normal u oferta)
            precio_el = tarjeta.find_elements(By.CSS_SELECTOR, "span.price__text-price") \
                        or tarjeta.find_elements(By.CSS_SELECTOR, "span.offer-only")
            precio_text = precio_el[0].text if precio_el else None
            if not precio_text:
                raise ValueError("Precio no encontrado")
            precio = float(precio_text.replace('$','').replace('.','').strip())

            # URL del producto: toma el primer <a> que redirija al detalle
            link_el = tarjeta.find_element(By.CSS_SELECTOR, "a.product-image__link, a.content-product")
            url_producto = link_el.get_attribute("href")

            # Imagen: busca cualquier <img> dentro de la tarjeta
            img_candidates = tarjeta.find_elements(By.TAG_NAME, "img")
            imagen_url = ""
            for img in img_candidates:
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src and src.startswith("http"):
                    imagen_url = src
                    break
            # Si no hay imagen, puedes poner una por defecto o dejar vacío

        except Exception as e:
            print(f"⚠️ Tarjeta Farmatodo ignorada: {e}")
            continue

        Medicamento.objects.create(
            laboratorio = laboratorio,
            nombre      = nombre,
            precio      = precio,
            url         = url_producto,
            imagen_url  = imagen_url,
            fuente      = "Farmatodo"
        )

    driver.quit()
"""

