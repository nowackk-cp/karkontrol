# Projede yapılanlar

Bu günlük yalnızca gerçekleşen işleri ve gerçek doğrulama sonuçlarını içerir.
Tarihler Europe/Istanbul saat dilimine göredir.

## 2026-10-04

### 001 — Mevcut durum incelemesi

- Proje kökü ve üst dizin talimatları kontrol edildi; kökte yalnızca
  `KarKontrol_Proje_Plani.md` bulundu. Mevcut Git deposu veya uygulama yok.
- Planın fazları ve altın kuralları okundu.
- Python 3.12.10, Git 2.55.0, uv ve GitHub CLI bulundu.
- Git kullanıcı adı ve e-postası yapılandırılmamış; kimlik uydurulmayacak.
- Doğrulama: dosya listesi, komut yolları, sürüm ve Git kontrolleri çalıştırıldı.

### 002 — Kalıcı çalışma kuralları

- `AGENTS.md` oluşturuldu; tamamlanan her işlemin bu dosyaya hemen yazılması
  altın kural olarak eklendi.
- Soru sormadan yerel ilerleme, dürüst kalite ölçümleri, bağımsız altın veri,
  Decimal kullanımı ve bağlam devri kuralları eklendi.
- Doğrulama: kurallar mevcut proje planıyla karşılaştırıldı.

### 003 — Plan ve depo korumaları

- Ana plana işlem günlüğü kuralı 12. altın kural olarak eklendi.
- `.gitignore`, `.gitattributes`, `.env.example` ve Python sürüm dosyası oluşturuldu.
- Başvuruya yönelik özel proje planı yerelde tutulacak biçimde Git dışında bırakıldı.
- Python 3.13 / Django 5.2 LTS, uv, ruff ve pytest araçları yapılandırıldı.
- README'ye çalıştırma komutları ve projenin gerçek başlangıç durumu yazıldı.
- GitHub CLI oturumu doğrulandı; hedef `nowackk-cp/karkontrol` deposunun
  henüz bulunmadığı görüldü. Hesap anahtarları okunmadı veya dosyaya yazılmadı.
- Python/Django uyumluluğu resmî kaynaklardan kontrol edildi; GİB stopaj
  kaynağı araştırma için incelendi. Alan bilgisi henüz onaylanmış kural değildir.

### 004 — Django uygulama temeli

- `manage.py`, WSGI/ASGI girişleri ve ortak/yerel/test/üretim ayarları oluşturuldu.
- Mağaza, sipariş, rapor, abonelik ve asistan uygulama paketleri kaydedildi.
- Ana sayfa, Django oturum açma/POST ile çıkış ve veritabanı kontrolü yapan
  `/health/` uç noktası eklendi.
- Testler için ayrı bellek veritabanı; üretim için zorunlu anahtar/alan adı ve
  HTTPS güvenlik ayarları yazıldı. Üretim anahtarı üretilmedi veya paylaşılmadı.
- Motor paketi yalnızca yer tutucudur; altın veriden önce motor yazılmadı.
- Doğrulama: çalıştırma ve entegrasyon kontrolleri bir sonraki kayıtla raporlanacak.

### 005 — Başlangıç testleri ve kalite iş akışı

- Sağlık kontrolü, veritabanı arızası, giriş/çıkış, CSRF, dış adrese yönlendirme,
  admin erişimi ve HTML kaçışını denetleyen entegrasyon testleri yazıldı.
- Üretimde güvensiz anahtar, joker alan adı ve HTTPS/çerez ayarları test edildi.
- GitHub Actions için kilitli bağımlılık, lint, format, Django, migration ve
  test aşamaları ile HTML/XML rapor artifact'ı yapılandırıldı.
- Hata bildirimi ve PR şablonları eklendi; `BUGS.md` gerçek başlangıç sayısını içeriyor.
- Doğrulama: bağımlılık kurulumu henüz sürdüğü için test sonuçları bekleniyor.

### 006 — QA ve alan araştırma hazırlığı

- Risk öncelikleri, test katmanları, kapsam dışı işler ve kalite hedefleri yazıldı.
- GİB'in resmî bilgi notundan stopaj kaynak özeti çıkarıldı; belirsiz pazaryeri
  politikaları varsayım olarak ayrıldı. İnsan onayı yapılmış gibi sunulmadı.
- `KURALLAR_v1_TASLAK.md` oluşturuldu; nihai kurallardan ayrı adlandırıldı.
- 30 siparişlik senaryo matrisi hazırlandı; AI sayısal beklenen sonuç üretmedi.
- AI karar kaydı ve compact aracının bulunmadığı gerçeği belgelendi.
- Doğrulama: senaryolar ana plandaki A–G gruplarıyla karşılaştırıldı.

### 007 — Kurulum kilidi ve yerel Git

- İlk Python indirmesi uzun süre tamamlanmadı; eşzamanlı `uv sync` aynı Python
  dizini kilidinde 300 saniye bekleyip zaman aşımı verdi. Testler çalışmış sayılmadı.
- Yalnızca bu işte başlatılan indirme süreci durduruldu; Windows sertifika
  deposu ve sınırlı yeniden denemeyle indirme yeniden başlatıldı.
- Yerel depo `main` dalında başlatıldı. Commit kimliği, oturum açmış GitHub
  hesabındaki gerçek ad ve hesabın resmî noreply adresiyle yalnızca bu depoda ayarlandı.
- Doğrulama: GitHub hesap kimliği API'den okundu; mevcut başka depo değiştirilmedi.

### 008 — İlk commit'ler ve bağlam devri

- Kurallar/günlük ve Django temeli ayrı anlamlı commit'lerle yerel Git'e kaydedildi.
- `docs/DEVAM_NOTU.md` oluşturuldu; kullanıcı tercihi, gerçek ilerleme,
  aktif kurulum sorunu ve sonraki kontroller kaydedildi.
- Doğrulama: commit çıktıları kontrol edildi. Commit'ler henüz dış depoya gönderilmedi.

### 009 — Python yorumlayıcısını doğrulama

- Python indirmesi tamamlandı; uv sürüm bağlantısı oluştururken hata verdi.
- Kurulan Python'un doğrudan yolu incelendi ve `--version` ile **3.13.14**
  doğrulandı. Kayıp yorumlayıcı sanılarak yeniden indirme yapılmadı.
- Doğrudan yorumlayıcı yoluyla `.venv` oluşturuldu; geliştirme bağımlılıklarının
  kurulumu yeniden başlatıldı. Windows sertifika bayrağının yeni adı `--system-certs`.
- GitHub release sorgusu ağ zaman aşımı verdi; bu hata GitHub erişiminin tümü
  için genellenmedi (hesap API sorgusu başarıyla çalışmıştı).

### 010 — Kilit dosyası ve altın veri kabul koşulları

- uv bağımlılık çözümlemesi 49 paket için tamamlandı; `uv.lock` üretildi.
  Paket kurulumu ayrıca doğrulanacak.
- `.env`, veritabanı ve özel planın Git dışında kaldığı `git check-ignore` ile doğrulandı.
- `data/golden/README.md` ile bağımsız veri kabul koşulları ve beklenen sütunlar kaydedildi.
- uv kurulan Python 3.13.14'ü son kontrolde tanıdı; sürüm bağlantısı sorunu
  kalıcı yorumlayıcı kaybı oluşturmadı.

### 011 — Bağımlılık kurulumu ve ilk statik doğrulama

- Python 3.13.14 ortamına 23 çalışma/geliştirme paketi kuruldu; Django 5.2.17,
  pytest 9.1.1 ve ruff 0.16.10 kilit dosyasıyla sabitlendi.
- Python dosyaları derleme kontrolünden geçti; `git diff --check` hata vermedi.
- İlk ruff kontrolü bir uzun satır ve iki biçim farkı bildirdi. Formatter
  uygulandı; lint ve format kontrolleri tekrar çalıştırıldı.
- Bu biçim bulguları finansal motor hatası olarak sayılmadı.
### 012 — Çalıştırma ve test sonuçları

- Ruff lint ve format kontrolleri temiz; Django sistem kontrolü sorun bulmadı,
  migration farkı yok. Yerel SQLite migration'ları başarıyla uygulandı.
- Windows uygulama denetimi `pytest` console launcher dosyasını engelledi
  (4551). Güvenlik ayarı değiştirilmeden standart `python -m pytest` kullanıldı.
- **22 test geçti**, iki worker ile pytest süresi **3,67 saniye**.
- HTML test raporu, JUnit XML, kapsam XML ve HTML kapsam raporu üretildi.
- Başlangıç altyapısı kapsamı **%91** (82/90 statement, 4/4 branch);
  henüz motor olmadığı için motor kapsamı veya finansal doğruluk iddia edilmedi.
- README, CI komutu ve devam talimatları Python modül çağrısıyla güncellendi.

### 013 — GitHub deposu

- Ana planda istenen `nowackk-cp/karkontrol` public deposu oluşturuldu.
- Depo açıklaması yazıldı; yerel `origin` bu depoya bağlandı.
- Doğrulama: GitHub CLI oluşturma komutu depo URL'sini başarıyla döndürdü:
  https://github.com/nowackk-cp/karkontrol.
- Başlangıç kontrolleri ve kilit dosyası ayrı `build:` commit'iyle kaydedildi.

### 014 — İlk yayın ve repo konuları

- `qa`, `test-automation`, `playwright`, `pytest`, `llm-eval`, `django` konuları eklendi.
  Konular yol haritasını tanımlar; tamamlanan özellik iddiası değildir.
- Dört küçük commit `origin/main` dalına gönderildi ve upstream kuruldu.
- Doğrulama: Git push başarılı; hemen sonraki sorguda workflow henüz listelenmedi.
  CI başarı iddiası eklenmedi; gerçek çalışma sonucu ayrıca izleniyor.

### 015 — Gerçek CI ve yerel HTTP doğrulaması

- GitHub run **37163642871** başarıyla tamamlandı. Lint, format, Django,
  migration farkı, testler ve artifact yükleme adımları başarılı.
- `quality` işi 15 saniye; run başlangıç/bitiş farkı 16 saniye. Bu ölçüm
  başlangıç altyapısına ait; sonraki finansal/E2E testlerin süresi değildir.
- 67.448 baytlık, süresi dolmamış `test-reports` artifact'ı API'den doğrulandı.
- Yerel Django sunucusu 127.0.0.1:8000 üzerinde başlatıldı. Gerçek HTTP ile
  ana sayfa, `/health/` ve giriş sayfası 200; health sonucu `status: ok`.
- Doğrulama bağlantısı: https://github.com/nowackk-cp/karkontrol/actions/runs/37163642871.

### 016 — Main kalite kapısı

- `main` dalı için güncel dal + başarılı `quality` kontrolü ve PR zorunlu kılındı.
- Kurallar yöneticilere de uygulanıyor; force push ve dal silme kapalı.
- Tek geliştiricili proje için insan onay sayısı 0; insan code review yapılmış
  gibi gösterilmedi. Sohbet çözümleme ve doğrusal geçmiş de zorunlu.
- Doğrulama: GitHub protection API başarıyla döndü; `admins: true`,
  `checks: [quality]`, `strict: true`, `force_push: false` doğrulandı.
- README'ye gerçek CI rozeti ve kanıt bağlantısı eklendi; devam notu güncellendi.

### 017 — Korumalı dal üzerinden belge güncellemesi

- Kanıt belgeleri `docs/bootstrap-evidence` dalına commit edilip gönderildi.
- PR #1 oluşturuldu ve Codex sohbetine bağlandı:
  https://github.com/nowackk-cp/karkontrol/pull/1.
- Yerel uygulamanın Codex tarayıcı panelinde açılması istendi; araç `queued`
  döndürdü. HTTP doğrulaması ayrı yapıldı; panelin görünür açıldığı varsayılmadı.
- Yereldeki ana planda biten teknik kurulum maddeleri işaretlendi; profil
  düzenleme ve insan doğrulaması gereken fazlar tamamlanmış sayılmadı.

### 018 — Kalite kapısının gerçek durumu ve panel bağlantısı

- PR #1 üzerinde `quality` çalışırken GitHub `mergeStateStatus: BLOCKED`
  döndürdü; zorunlu kalite kapısının bekleyen kontrolde birleştirmeyi engellediği görüldü.
- Main koruması yeniden API'den okundu; `quality`, yönetici kuralları ve PR
  zorunluluğu hâlâ etkin. Git çalışma ağacı kontrolde temizdi.
- İşlem günlüğünü Codex dosya panelinde açma isteği de `queued` olarak alındı.
- Onaylı altın veri ve motor aşamaları hâlâ tamamlanmadı; mevcut test sayısı
  yalnızca başlangıç altyapısını kapsıyor.

### 019 — Üretim ayarlarının sistem kontrolü

- Gerçek anahtar kullanılmadan geçici test değerleriyle üretim ayarları için
  `manage.py check --deploy --settings config.settings.production` çalıştırıldı.
- Sonuç: **0 sorun, 0 susturulmuş kontrol**. Yerel sunucu ayarı değiştirilmedi;
  herhangi bir dış sunucuya uygulama dağıtılmadı.
- README ve günlük kanıtlarını içeren PR #1 açık; kayıtlar bu PR dalındadır.
  İlk main CI başarılıdır; son belge commit'inin CI sonucu ayrıca kontrol edilir.

### 020 — Çalışmaya devam ve başlangıç belgelerinin birleştirilmesi

- Talimatlar, devam notu, günlük, Git durumu ve mevcut kod tekrar incelendi.
- `uv sync --locked --extra dev` başarılı; mevcut ortamda 23 paket doğrulandı.
- PR #1'in doğru commit'indeki `quality: SUCCESS` kontrol edilerek korumalar
  aşılmadan squash merge yapıldı; main güncellendi ve `feat/store-order-import`
  çalışma dalı açıldı.
- Günlükte 011 numaralı kaydın sona kaydığı fark edildi; 19 kaydın tamamı
  içerikleri korunarak numara sırasına alındı.
- Sıradaki çalışma: mağaza sahipliği, komisyon doğrulama ve atomik/mükerrersiz
  sipariş aktarımı. Bağımsız altın veri ve motorun tamamlandığı iddia edilmeyecek.

### 021 — Mağaza ve sipariş veri sözleşmesi

- Mağaza sahipliği, demo TRY pazaryeri ve %0…100 komisyon doğrulaması eklendi.
- Sipariş satırı, fiyat/maliyet/indirim/KDV/komisyon Decimal alanları, iade adedi
  ve mağaza-sipariş-satır benzersizliği tanımlandı. Kâr motoru oluşturulmadı.
- İçe aktarma partisi için mağaza + dosya özeti benzersizliği tanımlandı.
- Mağaza oluşturma ve oturuma göre mağaza listesi; yükleme, filtre ve iade
  formları yazıldı. Sahiplik alanı kullanıcıdan alınmıyor.
- Excel desteği için openpyxl 3.1.5 ve XML ayrıştırma koruması için defusedxml
  0.7.1 kuruldu; uv kilidi güncellendi. Resmî openpyxl ve Django transaction
  belgeleri incelendi. Uygulama kontrolleri ilgili akış tamamlanınca çalıştırılacak.

### 022 — Atomik CSV/Excel sipariş aktarımı

- UTF-8/BOM CSV (virgül/noktalı virgül ayraç), tek sayfalı XLSX, iki tarih
  biçimi, Türkçe ürün adı ve boş satır desteği yazıldı.
- Sütun/satır/tutar/adet/iade/para birimi doğrulamaları; 5 MB dosya,
  25 MB açılmış Excel ve 5000 satır sınırları eklendi. Formüllü hücreler reddedilir.
- Tüm satırlar önce doğrulanır; kayıtlar tek transaction içinde yazılır.
  Aynı dosya veya başka dosyadaki aynı sipariş satırı mükerrer kayda yol açmaz.
  Mevcut satırla çelişki tüm yeni kayıtları ve import partisini geri alır.
- Liste/ürün-tarih filtresi, dosya yükleme, sentetik CSV şablonu ve iade adedi
  güncelleme uç noktaları eklendi. Her uç noktada oturumdan mağaza sahipliği kontrol edilir.
- Finansal girişler doğrulama ve kayıt öncesinde Decimal'e çevrilir; binlik
  ayraç ve ikiden fazla ondalık reddedilir. Motor kâr sonucu hesaplamaz.
- Doğrulama: davranış testleri ve ekran kontrolleri sonraki kayıtlarda raporlanacak.

### 023 — Mağaza, yükleme ve iade ekranları

- Mağaza listesi/oluşturma, sipariş listesi, tarih-ürün filtresi, dosya yükleme
  ve iade düzenleme şablonları eklendi; kritik öğeler data-testid taşıyor.
- Sipariş fiyatı Türkçe iki ondalık/binlik biçimiyle gösterilir; açıklamalar ve
  dosya hataları kullanıcıya görünür. Hazır olmayan kâr/hakediş raporu rakam üretmez.
- Yalnızca DEBUG ortamında çalışan, mevcut hesabın parolasını değiştirmeyen
  tekrar çalıştırılabilir `seed_demo` komutu yazıldı; tüm veriler sentetik.
- Doğrulama: migration, sunucu ve kullanıcı akışı testleri henüz çalıştırılmadı.

### 024 — Migration ve veri güvenliği testleri

- Store, OrderLine ve ImportBatch başlangıç migration'ları üretildi.
- Liste 50 satırlık sayfalama kazandı; filtre parametreleri sayfa geçişinde korunur.
  Yerel tarih alanlarının HTML date değeri ISO biçimine düzeltildi.
- CSV/XLSX, 30 satır, Türkçe ve Decimal koruma, tekrar aktarım, çelişkide rollback,
  geçersiz girdiler, kaynak sınırları, mağaza izolasyonu, iade, filtre/sayfalama
  ve demo hesabı korumalarını denetleyen entegrasyon testleri yazıldı.
- İlk lintte iki uzun metin ve migration import sırası bulundu; düzenlendi.
  Sayısal beklenen değerler kaynak dosyanın girişlerini denetler; altın kâr verisi değildir.

### 025 — İlk test turu ve APP-001 düzeltmesi

- Django kontrolü ve migration farkı kontrolü başarılı; ilk test turu
  **70 geçti, 2 başarısız** (72 test, pytest süresi 3,28 saniye).
- Başarısızlık: yabancı mağazanın liste/şablon uç noktasına POST, 404 yerine
  405 dönüyordu. Veri sızıntısı veya parasal hata değil, yanıt tutarlılığı sorunu.
- Test beklentileri korunarak oturum → sahiplik → HTTP metodu kontrol sırası
  ortak decorator ile düzeltildi. `BUGS.md` içine APP-001 olarak gerçek kanıt yazıldı.
- Formatter uzun test imzasını düzenledi; bütün kontroller tekrar çalıştırılacak.

### 026 — Başarılı test turu ve yerel veri kurulumu

- Test beklentileri değiştirilmeden **72 test geçti** (iki worker, 3,07 saniye).
- Ruff lint temiz; 58 Python dosyası format kontrolünden geçti.
- Uygulama toplam dal dahil kapsamı %96; kâr motoru kapsamı değildir.
  HTML/XML/JUnit raporları güncellendi.
- Store ve OrderLine/ImportBatch migration'ları yerel veritabanına başarıyla uygulandı.
- DEBUG ortamında `seed_demo` çalıştırıldı; sentetik mağaza ve iki sipariş
  satırı kuruldu. Hesap: demo-satici; yalnızca demo parolası: demo-only-pass-2026.
- Sonraki doğrulama: gerçek tarayıcıda giriş, mağaza, filtre ve aktarım ekranları.

### 027 — Gerçek tarayıcı akışları ve ekran kanıtı

- Browser becerisiyle 127.0.0.1:8001 üzerinde giriş, demo mağaza listesi,
  ürün filtresi ve 1.234,56 ₺ biçimi gerçek tarayıcıda doğrulandı.
- Sentetik `Tarayıcı Demo Mağazası` kuruldu; %150 komisyonla formda kalındığı,
  %20 ile kaydın oluşturulduğu görüldü. Yerel veri dışında dış etkisi yok.
- Ekrandan örnek CSV indirildi ve dosya seçiciyle yüklendi: 1 satır aktarıldı.
  Aynı dosya tekrar yüklendi: 0 eklendi, 1 atlandı; satır sayısı 1 kaldı.
- 2 adetlik satıra 3 iade reddedildi; 1 iade kabul edilip listede gösterildi.
- Ekran kanıtı `reports/screens/store-orders.png` olarak kaydedildi; demo
  sekmesi kullanıcıya bırakıldı. Bu kontroller, repo içindeki bir Playwright
  E2E test paketi tamamlanmış gibi sayılmadı.
- Git diff kontrolündeki günlük sonu boş satırı temizlendi; kayıtlar korunuyor.

### 028 — Adet sınırı regresyonu (APP-002)

- Son girdi incelemesinde çok uzun adet için kontrol eksikliği görüldü.
  Eklenen regresyon testi 5000 basamaklı girdide gerçekten başarısız oldu:
  ImportValidationError yerine Python'un 4300 basamak sınırından ValueError çıkıyordu.
- Parser, dönüşümden önce 10 basamak ve ardından 2147483647 sınırıyla
  düzeltildi. Python güvenlik sınırı değiştirilmedi; test beklentisi korundu.
- BUGS.md'ye APP-002 gerçek çıktıyla eklendi. Finansal motor hatası değildir.
- Son tam test/lint/format turu yeniden çalıştırılacak.

### 029 — Son kalite turu ve güncel kullanım belgeleri

- Adet sınırında izin verilen 2147483647 ve reddedilen 2147483648 de test edildi.
- **75 test geçti**, pytest süresi **3,09 saniye**, uygulama toplam kapsamı **%96**.
  Ruff temiz; Django/migration kontrolleri temiz. Raporlar güncellendi.
- Bu oturumda başlatılan 8001 sunucusu port/PID/komutuyla doğrulanarak
  durduruldu ve son parser koduyla aynı portta yeniden başlatıldı.
- README, dosya sözleşmesi, QA stratejisi ve AI karar kaydı güncellendi.
- Önceki %91/22 test başlangıç kanıtı tarihiyle korundu; yeni %96/75 test
  motor doğruluğu veya altın mutabakat sonucu gibi sunulmadı.
- İlk belge patch'i bir satır eşleşmediği için uygulanmadı; dosya tekrar
  okunup doğru bağlamla patch uygulandı. Hiçbir kullanıcı dosyası silinmedi.

### 030 — Küçük commit'ler ve devam notu

- Veri modelleri/bağımlılıklar, aktarım/ekranlar/testler, APP-002 düzeltmesi ve
  kullanım belgeleri dört anlamlı commit'e ayrıldı.
- Yeniden başlatılan güncel sunucuda sekme reload edildi; 1 satır ve 1 iade
  durumu korunuyor. Tarayıcı sekmesi çıktı olarak bırakıldı.
- Devam notu gerçek 75 test/%96 kapsam, demo akışı, sunucu portu ve kalan
  altın veri/motor/E2E/SQL/billing/asistan işleriyle güncellendi.
- Başlangıç PR #1'in birleştirildiği kayıtlar güncellendi; yeni PR/CI kontrolü sırada.

### 031 — Sipariş akışları PR'ı

- `feat/store-order-import` dalı GitHub'a gönderildi; PR #2 oluşturuldu ve
  Codex sohbetine bağlandı: https://github.com/nowackk-cp/karkontrol/pull/2.
- PR açıklaması somut önce/sonra davranışı, atomiklik/izolasyon, 75 test,
  kapsam, gerçek tarayıcı kontrolleri ve kalan kapsam sınırlarıyla yazıldı.
- Devam notuna PR bağlantısı eklendi. Son commit'in CI sonucu bekleniyor;
  yerel test başarısı uzak CI başarısıyla karıştırılmıyor.
