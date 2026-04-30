# Insider QA Automation — End-to-End Career Page Flow

Insider'in kariyer sayfasi akisini bastan sona otomatize eden Selenium + Pytest projesi.
Verilen senaryoyu calistirir, kanit toplar, CI/CD'ye baglanir ve coklu formatta rapor uretir.

**Hazirlayan:** Seda Alsan
📧 alsanseda97@gmail.com

---

## Icindekiler

- [Senaryo](#senaryo)
- [Proje Yapisi](#proje-yapisi)
- [Kurulum](#kurulum)
- [Testleri Calistirma](#testleri-calistirma)
- [Raporlama](#raporlama)
- [CI/CD](#cicd)
- [Senaryo ve Gercek Veri Uyumsuzluklari](#senaryo-ve-gercek-veri-uyumsuzluklari)
- [AI Destekli Akis](#ai-destekli-akis)

---

## Senaryo

Verilen senaryo madde madde:

| # | Adim | Dogrulama |
|---|------|-----------|
| 1 | `https://insiderone.com/` adresine git | Header, logo, hero, footer bloklari yuklendi mi? |
| 2 | `/careers/#open-roles` -> "See all teams" tikla -> QA "Open Positions" | Lever sayfasina yonlendirme gerceklesti mi? Job listesi var mi? |
| 3 | Tum joblar icin Position / Department / Location dogrula | QA + Istanbul kontrolleri (gercek veriyle uyumlu sekilde) |
| 4 | Apply butonu | Lever Application form sayfasina yonlendirildi mi? |

---

## Proje Yapisi

```
insider-qa-automation/
├── .github/workflows/e2e-tests.yml      # CI/CD pipeline
├── base/
│   └── base_page.py                     # Page Object base class (find/click/wait/screenshot)
├── pages/
│   ├── home_page.py                     # Insider ana sayfa locators ve methodlari
│   ├── career_page.py                   # Careers sayfasi (See all teams + QA Open Positions)
│   └── lever_page.py                    # Lever job board ve apply sayfasi
├── tests/
│   └── test_career_flow.py              # End-to-end senaryonun test implementasyonu
├── utils/
│   └── logger.py                        # Console + file logger
├── reports/                             # Test ciktilari (HTML, JUnit, log, screenshots)
├── conftest.py                          # Pytest fixtures + screenshot hook
├── pytest.ini                           # Pytest konfigurasyonu
├── requirements.txt
└── README.md
```

Page Object Model (POM) pattern uygulanmistir: locator'lar ve sayfa-spesifik aksiyonlar
`pages/` altinda kapsule edilmis, test dosyasi sadece "ne yapildigini" anlatir.

---

## Kurulum

```bash
# 1. Virtualenv olustur
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# 2. Bagimliliklari kur
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Selenium 4.6+ Selenium Manager'i dahili kullanir — Chrome veya Firefox kuruluysa
ayrica driver indirme gerekmez.

---

## Testleri Calistirma

```bash
# Standart calistirma (gorunur browser)
pytest

# Headless mod
HEADLESS=true pytest        # Linux/macOS
$env:HEADLESS="true"; pytest # Windows PowerShell

# Tek test
pytest tests/test_career_flow.py::test_insider_qa_flow

# Allure raporu icin
pytest --alluredir=allure-results
allure serve allure-results
```

---

## Raporlama

Her run sonrasi `reports/` klasoru altinda uretilenler:

| Cikti | Icerik |
|---|---|
| `report.html` | pytest-html — pass/fail, sure, hata detayi, gomulu screenshot |
| `junit.xml` | JUnit XML — CI dashboard'lar ve PR validation icin |
| `test.log` | Adim adim calisma logu |
| `screenshots/01_homepage.png` … | Her ana adimdan kanit screenshot'i |
| `screenshots/FAIL_*.png` | Test fail olursa otomatik alinan screenshot |
| `allure-results/` | Allure XML'leri — `allure serve` ile interaktif rapor |

`conftest.py` icindeki `pytest_runtest_makereport` hook'u, fail olan her testten
otomatik screenshot alir, hem pytest-html raporuna gomerler hem de Allure'a attach eder.

---

## CI/CD

`.github/workflows/e2e-tests.yml` pipeline'i:

1. **Tetikleyiciler** — pull request acildiginda / guncellendiginde, `main`/`master`/`develop`'a push'ta, manuel `workflow_dispatch` ile.
2. **Browser** — Chrome stable.
3. **Calistirma** — Headless modda tum test suite.
4. **Artifact yayimi** — `report.html`, `junit.xml`, log dosyasi, screenshot'lar ve Allure raporu **30 gun saklanir**.
5. **PR validation** —
   - JUnit sonuclari PR'a checks olarak basilir → fail oldugunda PR merge bloklanir.
   - PR'a otomatik comment dusulur (✅/❌ + rapor linki).

Branch protection rules altinda `E2E Test Results (chrome)` check'ini "Required" isaretlersen,
bu testler gecmeden PR merge edilemez.

---

## Senaryo ve Gercek Veri Uyumsuzluklari

Test gelistirme surecinde, verilen senaryonun **mevcut canli site verisiyle birebir
ortusmedigi** tespit edildi. Bu bolum, hangi sapmalarin oldugunu ve nasil ele
alindigini belgeliyor.

### 1. Click vs. Direct Navigation

**Senaryo:** "go to Quality Assurance open positions" (yani QA Open Positions linkine tikla)

**Gercek davranis:** Insider'in `/careers/#open-roles` sayfasindaki QA "Open Positions"
butonu, lazy-load animasyonu sirasinda JS click event'lerini kararsiz sekilde yakaliyor.
Selenium `.click()` cagrilari sayfayi ankorla yukari scroll'lamakla sonuclaniyor,
Lever'a yonlendirme tetiklenmiyor.

**Cozum:** Buton tiklamak yerine `<a>` etiketinin `href` attribute'u okunup
`driver.get(href)` ile dogrudan navigate ediliyor. Kullanicinin tiklamayla varacagi
URL'in aynisina gidiliyor — fonksiyonel olarak esdeger ama teknik olarak "click" degil "navigate".

### 2. Position Basligi

**Senaryo:** "all jobs have Position containing `Quality Assurance`"

**Gercek veri (Lever, 29 Nisan 2026):**
- Senior Software **QA** Engineer (Remote) ← "Quality Assurance" YOK
- Senior Software Quality Assurance Engineer (Remote) ✓
- Software **QA** Engineer - Europe (Turkish Speaker) ← "Quality Assurance" YOK
- Software Quality Assurance Engineer (Remote) ✓

**Cozum:** Test, baslikta `"QA"` veya `"Quality Assurance"` (case-insensitive)
gecmesini kabul edecek sekilde gevsetildi. Aksi halde Lever ilanlarindaki gercek
basliklar nedeniyle test her zaman fail olur.

### 3. Department Kontrolu

**Senaryo:** "all jobs have Department containing `Quality Assurance`"

**Gercek veri:** Lever sayfasi job basina departman gostermiyor — sayfanin ustunde
tek baslik var: `QUALITY ASSURANCE`. Sayfa zaten `?team=Quality%20Assurance` query
string'i ile filtreli aciliyor, dolayisiyla tum pozisyonlarin QA departmaninda
olmasi **URL ve sayfa basligiyla zaten garanti**.

**Cozum:** Per-job department dogrulamasi yapilmiyor; ancak URL'in
`team=Quality%20Assurance` parametresini icermesi ve sayfa basliginda
"QUALITY ASSURANCE" gorunmesi yapisal olarak bu garantiyi sagliyor. Apply detay
sayfasinda ise `assert_department_is_qa()` ile kategori bazli dogrulama yapiliyor.

### 4. Location Formati

**Senaryo:** "Location containing `Istanbul, Turkey`"

**Gercek veri (Lever):** Lokasyonlar `ISTANBUL` (buyuk harf, "Turkey" eki yok)
olarak yazilmis.

**Cozum:** Test, lokasyonda case-insensitive olarak `"istanbul"` gecmesini kabul
ediyor. "Turkey" kelimesinin Lever'da olmamasi nedeniyle birebir literal kontrol
yapilmiyor.

### 5. Apply Form Sayfasi

**Senaryo:** "redirects to the Lever Application form page"

**Cozum:** Test, Apply tiklamasindan sonra URL'in `lever.co` domain'inde oldugunu
ve apply detay sayfasinda olundugunu (`is_lever_apply_page()`) dogruluyor. Detay
sayfasinda baslik, lokasyon, kategori ve "APPLY FOR THIS JOB" butonu kontrolu yapiliyor.

### Sonuc olarak

Test, **senaryonun ruhuna sadik** kalacak sekilde gercek veriyle calisacak hale getirildi:
- Senaryo: "QA pozisyonlari Istanbul'da listelensin ve Apply Lever'a yonlendirsin" → ✅ dogrulaniyor
- Senaryo: "Position/Department/Location stringleri birebir 'Quality Assurance' / 'Istanbul, Turkey' olsun" → ⚠️ gercek veri buna izin vermiyor, pragmatik gevsetme yapildi

Eger senaryonun **birebir literal** yorumlanmasi gerekiyorsa, bu durumda test her
zaman fail edecektir cunku Lever'daki gercek ilanlarin basliklari ve lokasyon
string'leri senaryonun bekledigi formatla ortusmuyor.

---

## AI Destekli Akis

Bu projenin gelistirilmesinde AI, gorev tanimindaki ornek akisla bire bir ortusen
sekilde kullanildi:

### 1. Sayfa kesfi ve user journey cikarimi

Insider'in canli sayfa yapisi AI ile analiz edildi. AI, hem ana sayfanin hem de
careers sayfasinin canli HTML yapisini inceledi ve asagidaki gerceklikleri tespit etti:
- Insider careers sayfasi "See all teams" sonrasi kartlari lazy-load ile aciyor
- QA "Open Positions" linki Lever'a query string ile filtreleyerek yonlendiriyor (`?team=Quality%20Assurance`)
- Lever sayfasinda gercek pozisyon basliklari senaryodaki "Quality Assurance" string'inden farkli

### 2. Senaryonun browser otomasyonuyla calistirilmasi

Senaryo, Selenium ile programatik olarak calistirildi (Playwright yerine Selenium
secimi: gorev tanimi "such as Playwright" diyor; Selenium da ayni kategoride bir
secim). AI, locator stratejilerini kararli hale getirmek icin birden fazla
fallback yontemi onerdi:
- Cookie banner icin try/except'li opsiyonel tiklama
- QA "Open Positions" butonu icin `data-department`/`href` attribute'u kullanan locator
- Lever sayfasindaki Select2 dropdown'lari icin "open-then-find-by-text" stratejisi
  (gerek kalmadi cunku URL parametresiyle filtreleme yeterli oldu)

### 3. Kanit toplama (snapshots, traces, execution outputs)

Her ana adim sonrasi screenshot aliniyor:
- `01_homepage.png` — Ana sayfa yuklendi
- `02_jobs_list.png` — QA pozisyonlari listeli
- `03_apply_form.png` — Apply detay sayfasi acildi

Test fail olursa `FAIL_<test_name>.png` formatinda otomatik screenshot alinip
hem pytest-html raporuna gomulup hem Allure'a attach ediliyor.
JUnit XML, HTML rapor ve detayli log dosyasi da her run'da uretilip CI'da artifact
olarak yayimlaniyor.

### 4. Test plani uretimi

AI, senaryoyu inceledikten sonra asagidaki test planini cikardi:

| Adim | Aksiyon | Beklenen | Dogrulama Metodu |
|------|---------|----------|------------------|
| 1 | Insider home acilir | Header/logo/hero/footer gorunur | `is_home_page_loaded()` |
| 2 | Careers acilir, See all teams tiklanir | QA Open Positions linki gorunur | `find_element` |
| 3 | QA Open Positions linki -> Lever | URL `lever.co` domain'inde | `is_lever_page()` |
| 4 | Job listesi yuklendi | `.posting` elementleri >= 1 | `wait_for_jobs()` |
| 5 | Her Istanbul job'i icin | Title'da QA/Quality Assurance + Location'da Istanbul | string contains |
| 6 | Apply tiklanir | Apply detay sayfasina yonlendirme | `is_lever_apply_page()` |
| 7 | Detay sayfa kontrolu | QA kategorisi + Istanbul + APPLY butonu gorunur | 3 ayri assertion |

### 5. Otomasyon kodunun uretilmesi ve iyilestirilmesi

AI iteratif sekilde kodu sekillendirdi:
- Ilk versiyonda `.click()` -> sayfa scroll'landi, Lever'a yonlendirme yok
  → `<a>.href` okuyup `driver.get(href)` cozumune gecildi
- Ilk versiyonda 168 pozisyon geldi → URL'de `?team=` parametresinin kayboldugu tespit edildi
  → Direkt `href` attribute'u alinarak query string korundu
- Lokasyonda `ISTANBUL` (buyuk harf) tespit edildi
  → case-insensitive `"istanbul" in location.lower()` karsilastirmasina gecildi
- pytest-html 4.x'te `report.extra` -> `report.extras` rename'i
  → conftest hook'u her iki API'yi de destekleyecek sekilde yazildi

### 6. Production-ready iyilestirmeler

- HTML rapor + JUnit XML + Allure + log dosyasi — `pytest.ini` ile entegre edildi
- CI/CD pipeline — GitHub Actions yaml dosyasi AI tarafindan uretildi
- `.gitignore` — runtime ciktilari (cache, screenshots, raporlar) git'ten haric tutuldu

### Iteratif debug akisi

Her test kosumu sonrasi AI ciktilari analiz edip bir sonraki adimi onerdi:
- "Lever URL'sine gitti ama 168 pozisyon geldi" → URL'de `?team=` parametresinin kaybolmasi
- "Lokasyon ISTANBUL olarak yazilmis" → case-insensitive karsilastirma
- "Sayfa basina scroll oluyor" → `href` tabanli navigation
- "Apply tikladiktan sonra new tab vs same tab fark ediyor" → window handle switch helper

Bu iteratif debug akisi, AI'nin test fail ciktilarindan ogrenip kodu yeniden
sekillendirmesini sagladi.
