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

### 032 — Uzak kalite kapısının doğrulanması

- PR #2'nin son kod/belge commit'i 72398004020000623b10443af31ff55ee39faffe
  için GitHub run **37165639061** başarıyla tamamlandı.
- PR kontrolü `quality: SUCCESS`, durum OPEN/CLEAN; birleştirme engeli kalktı.
  PR henüz birleştirilmedi ve yönetici korumaları aşılmadı.
- Kanıt: https://github.com/nowackk-cp/karkontrol/actions/runs/37165639061.
- Git çalışma ağacı kontrol sırasında temiz; bütün tamamlanan işler günlüğe
  ve devam notuna kaydedildi. Kodun bağımsız altın mutabakatı iddia edilmez.

### 033 — Sipariş akışının ana dala alınması

- PR #2, son başlığı 8611d7a ve başarılı quality kontrolü doğrulandıktan sonra
  squash ile birleştirildi. Ana dal fast-forward güncellendi;
  `feat/profit-quality-mvp` dalında kalan uygulama işlerine başlandı.
- Kullanıcının bitene kadar devam et talimatıyla demo finans politikaları
  açık varsayımlarla uygulanacak. İnsan denetimli altın veri veya gerçek LLM
  değerlendirmesi yapılmadan bu kanıtların elde edildiği iddia edilmeyecek.

### 034 — Demo finans sözleşmesi ve saf motor

- Kargo eşikleri, desi, satır ücret dağıtımı, kupon finansmanı, kısmi/tam iade,
  KDV ve stopaj politikaları KURALLAR_v1.md içinde açıkça belirlendi.
- Django'dan bağımsız Decimal motoru eklendi; en büyük kalan dağıtımı,
  sipariş başına ücret ve nakit/kâr çapraz kontrolü uygulandı.
- Bu aşamada motor testleri henüz çalıştırılmadı; insan doğrulamalı altın set
  üretilmedi. Tarihî taslak yeni sözleşmeye yönlendirildi.

### 035 — Finans kayıtları, döviz girdileri ve sahte abonelik

- Finans sonuçlarını SQL'de tamsayı kuruş olarak saklayan model, atomik sipariş
  yeniden hesabı, aylık/window SQL raporu ve yeniden oluşturma komutu eklendi.
- Amazon demo, sabit USD/EUR kuru ve desi/ağırlık/maliyet KDV girdileri eklendi.
  Aktarım ve iade akışına hesaplama bağlandı; migrasyon ve testler sırada.
- Ücretsiz 100 satır limiti, Demo Pro ve başarılı/reddedilen/zaman aşımı
  simülasyonu eklendi. Ödeme tekrarları kullanıcı+UUID ile tekilleşir;
  gerçek ödeme veya dış API çağrısı yoktur.

### 036 — Kâr ekranı, dışa aktarım ve araç asistanı

- Filtrelenmiş kâr/hakediş/net satış kartları, satır kalemleri, aylık SQL
  raporu, sayfalama ve CSV dışa aktarım eklendi. CSV kimlik alanlarında
  elektronik tablo formül enjeksiyonuna karşı metin öneki kullanılır.
- Oturum sahibine bağlı özet, ürün sıralaması, iade ve kural araçlarıyla
  anahtarsız asistan eklendi. Sayılar araç beyaz listesiyle doğrulanır;
  dış LLM başarısı veya judge kalibrasyonu iddia edilmez.
- İlk migrasyonlar yerelde başarıyla uygulandı; mevcut üç siparişin
  finans kayıtları rebuild_reports ile oluşturuldu. Ekran/test doğrulaması sırada.

### 037 — İlk regresyon ve finans testlerinin eklenmesi

- Yeni modeller/aktarımı takiben mevcut 75 test yeniden geçti (2,39 saniye).
- Kullanıcının 600 TL örneği, eşik ±1 kuruş, desi, iade, satır dağıtımı,
  para türü/sonluluk doğrulaması ve sabit döviz birim testleri eklendi.
- Fraction/tamsayı aritmetiğiyle ikinci hesap yolu ve Hypothesis nakit eşitliği,
  kuruş koruma testleri eklendi. Bu testler insan altın veri yerine sunulmaz.
- Formatlama ilk lint hatalarının çoğunu giderdi; kalan uzun metinler bölündü.
  Yeni testlerin sonucu sonraki doğrulamada kaydedilecek.

### 038 — Motor doğrulaması ve uygulama kalite kapsamı

- 138 test geçti; motorun ölçülen satır ve dal kapsamı %100. Yeni uygulama
  ekranlarının testleri henüz eklenmediği anda toplam kapsam %78 idi.
- SQL/window toplamları, filtre/sayfalama, döviz, tekrar ödeme, ücretsiz limit
  geri alma, iade hesabı ve asistan izolasyonu için entegrasyon testleri eklendi.
- Playwright bağımlılığı ve Chromium kurulumu başlatıldı. Mutmut 3.8.0 için
  resmî yapılandırma/fork gereksinimi incelendi; Linux CI üzerinde çalışacak.

### 039 — Finans entegrasyonu ve tarayıcı otomasyonunun hazırlanması

- 165 birim/entegrasyon testi geçti (3,10 saniye); iade, sabit kur, izolasyon,
  SQL/window, abonelik tekilleştirme ve limitte atomik geri alma doğrulandı.
- Hesap oluşturma eklendi; ana sayfa çalışan raporlara göre güncellendi.
- Page Object Model ile 12 bağımsız Playwright senaryosu yazıldı. Beş rapor
  satırının kontrolü kullanıcı kaynaklı 600 TL örneğine dayanır; altın veri
  E2E'si gibi sunulmaz. Chromium kurulumu bitince otomasyon çalıştırılacak.

### 040 — İnsan inceleme girdileri ve E2E kurulum kontrolü

- İlk E2E çağrısı Chromium indirmesi sürerken başlatıldığı için üç kurulum
  hatası verdi; uygulama testi sonucu sayılmadı. Kurulumun tamamlanması beklenecek.
- E2E fixture'ları için Django async kontrol istisnası yalnız test kapsamına
  eklendi; uygulama/üretim ayarlarına taşınmadı. Lint ve format temiz.
- 30 TRY + 10 Amazon sentetik girdi ve sonuçları BOŞ insan inceleme CSV'si
  üreten script eklendi. Bu girdiler nakit eşitliği regresyonunda kullanılır;
  insan altın mutabakatı iddia edilmez. Hesap oluşturma testleri de eklendi.

### 041 — Gerçek E2E sonucu ve asistan değerlendirme kapısı

- Kurulum tamamlandıktan sonra E2E session fixture sırası düzeltildi;
  Django async istisnası test DB kurulumu öncesinde yalnız test oturumunda açıldı.
  İki yanlış test seçicisi mevcut store-save/return-save adlarına düzeltildi.
- **12 Playwright testi geçti (7,91 saniye).** Uygulama beklentileri değiştirilmedi.
- 40 soruluk (12 sayısal, 8 sıralama, 6 kural, 6 veri yok/kapsam dışı,
  4 belirsiz, 4 güvenlik) set ve bağımsız SQL/guardrail kontrolleri eklendi.
  Ayrılmış 10 soru geliştiren AI tarafından görülmüştür; kör hold-out değildir.
- CI'ye E2E ve motor dal kapsamı >=%90 kapısı; haftalık eval ve gecelik
  Linux mutmut workflow'u eklendi. Uzak sonuçları henüz alınmadı.

### 042 — Eval envanter kontrolü ve veritabanı sınırları

- 40 sorunun tamamı yanıt/SQL kontrolünden geçti; envanter testi ayrılmış soru
  sayısının 10 yerine 9 olduğunu yakaladı (251 geçti, 1 başarısız). E-40 etiketi
  reserved yapılarak veri hatası düzeltildi; beklenen sayı gevşetilmedi.
- Ölçülen toplam satır+dal kapsamı %98, motor dalları 44/44; başarılı tam
  test çalışması henüz bu düzeltmeden sonra alınacak.
- Desi/kur/maliyet KDV için DB kısıtları; toplam mutlak kuruş sınırı eklenerek
  filtre ve SQL window toplamlarında tamsayı taşması önlendi.
- Yeni pazaryeri kabul kontrol listesi yazıldı.

### 043 — Tam test sonucu ve kullanım metinleri

- **252 test geçti (6,76 saniye)**; motor dal kapısı 44/44 = %100.
  Migrasyonlar ve Django sistem kontrolü temiz. 40 soru doğru niyet/araç/SQL
  sonucunu verdi; bu deterministik asistan ölçümüdür, LLM skoru değildir.
- 40 sentetik girdi ve boş inceleme şablonu diske üretildi. Sipariş para birimi,
  rapor bağlantıları ve yeni aktarım alanları kullanıcı ekranlarına yansıtıldı.
- Bir patch tablo satırı eşleşmediğinden reddedildi; satır tam bağlamıyla
  yeniden düzenlendi. Toplam sınır kontrolünün büyük dosyalarda bir kez yapılması
  için hesap servisinde enforce_totals seçeneği uygulandı.

### 044 — Güncel ekranların gerçek tarayıcı kontrolü

- Yerel 8001 sunucusu yalnız kendi manage.py süreci doğrulanarak güncel
  kodla yeniden başlatıldı. 252 test tekrar geçti; lint/migrasyon farkı temiz.
- Tarayıcıda mevcut kısmi iadeli siparişin satır/kart/aylık sonuçları eşleşti:
  net kâr -20,01 TL, hakediş 34,74 TL. Asistan aynı rapor tutarlarını döndürdü.
- Tam sayfa ekran görüntüsü reports/screens/profit-report.png kaydedildi.
  Desktop rapor tablosunun görünürlüğü için içerik genişliği 1160px'e çıkarıldı;
  dar ekranda yatay tablo kaydırması ve tek sütun kartlar korunur.

### 045 — Uzak inceleme ve ilk mutasyon çalışmasının hazırlanması

- Çalışan finans/abonelik/asistan/E2E kodu 42e8f9e commit'iyle GitHub dalına
  gönderildi. Commit öncesi format kontrolü yeni migrasyonda bir biçim farkı
  gösterdi; bu fark takip commit'inde gideriliyor, temiz format iddia edilmiyor.
- Nightly workflow'una yalnız geliştirme dalı için geçici push tetikleyicisi
  eklendi; Linux mutmut ölçümü ana dala almadan önce alınacak ve tetikleyici
  ölçümden sonra kaldırılacak. PR açıklaması somut sonuç/sınırlarla hazırlandı.

### 046 — Uzak CI ve eval kanıtı, mutasyon çıktı düzeltmesi

- PR #3 oluşturuldu ve sohbete bağlandı. Başlık0554ab2 için CI run37170676379
  SUCCESS; 252 test, 12 E2E ve kapsam kapısı Linux üzerinde geçti.
- Assistant eval run37170676353 SUCCESS. Mutasyon run37170671098 hesaplamayı
  bitirdi ancak mutmut3.8'de bulunmayan junitxml export komutunda başarısız oldu.
  Unsupported komut kaldırıldı; results ve .meta artifact'ı alınacak.
- Yeni devam notu çalışan kapsam, testler, sunucu/tarayıcı ve gerekli kalan
  işleri içeriyor. Eski PR2 sonrası notlar tarihî olarak işaretlendi.

### 047 — Mutasyon ilk sayımı ve teknik belgeler

- İlk mutmut logu: 369/369 mutant tamamlandı, 335 öldürüldü ve 34 yaşadı;
  ham skor 335/369 = %90,79. Export başarısızlığı ölçüm başarısı gibi sunulmadı.
- Kur/ücret DB kısıtları ve zıt işaretli toplamda SQL taşma koruması için
  anlamlı entegrasyon testleri eklendi; sonuçları bir sonraki koşuda alınacak.
- Mimari, 40 soruluk gerçek eval kapsamı/sınırları ve dürüst mülakat demo
  notları yazıldı. LLM/judge/kör hold-out eksikliği açıkça belirtildi.

### 048 — Doğrulanmış mutasyon artifact'ı ve eşik kapısı

- Mutation run37170823038 SUCCESS. Artifact indirildi; .meta exit kodları
  gerçekten 335 killed/34 survived, 369 toplamı doğruluyor (%90,79).
- SQL/DB yeni 7 testi geçti. Gecelik ölçüme boş seti ve <%85 skoru reddeden
  metadata kapısı eklendi; timeout/hata öldürülen sayılmaz.
- Dört survivor örneğini incelemek için geçici diff export'u eklendi;
  nihai workflow'da hard-coded mutant kimlikleri bırakılmayacak.
- QA stratejisi yeni gerçek kanıtlarla güncellendi. İki belge patch'i yanlış
  bağlam yüzünden reddedildi; doğru bağlamla uygulandı, veri kaybı yok.

### 049 — Yayın raporu hazırlığı ve kapsam durumu

- Başarılı main CI artifact'ını GitHub Pages'e taşıyan rapor workflow'u
  hazırlandı; canlı yayın sonucu henüz alınmadı. Rapor giriş sayfası gerçek
  coverage JSON'unu ve kaynak commit/run bilgisini gösterir.
- Paket sürümü 0.2.0'a çıkarıldı; proje fazları çalışan çıktı ve insan/harici
  hizmet kabul sınırlarıyla PROJE_DURUMU.md içinde açıklandı.
- HTML/JSON/YAML/INI satır sonları Git'te LF olacak şekilde tanımlandı.

### 050 — Pages yapılandırması ve güncel veri/provenans belgeleri

- GitHub Pages için workflow tabanlı yayın kaynağı yapılandırıldı. İlk yayın
  main'deki başarılı CI sonrası yapılacak; hazırlık canlı site başarısı sayılmaz.
- Yayın yalnız bu reponun main push CI sonucunu kullanır; PR/fork artifact'ı
  yayımlanmaz. İşlevsiz manual dispatch kaldırıldı.
- Aktarım sözleşmesi kur/desi/kota/hesap atomikliğiyle; AI karar kaydı yeni
  yaklaşım ve gerçek metriklerle güncellendi. Golden README boş beklenen
  şablona yönlendirir, motordan önce insan veri commit'i koşulunun sağlanmadığını açıklar.

### 051 — Yaşayan mutantların anlamlı incelenmesi

- Run37171024566 artifact'ı aynı369/335/34 sayımını ve dört örnek diff'i verdi.
- En büyük kalan sıralamasını kaldıran mutant ve maliyet KDV'sinde bölmeyi
  çarpmaya çeviren mutant mevcut testlerden kaçıyordu: bu test boşluğu olarak
  kaydedildi, çalışan motor hatası diye sayılmadı.
- Ağırlığa göre kalan kuruş, sıfır ağırlık tie, maksimum adet/satır sınırı ve
  kullanıcı kaynaklı örneğin KDV kalemleri için anlamlı kontroller eklendi.
- shipping validate(gross,None) mutantı yalnız hata alan adını değiştirir;
  eşdeğer finans davranışı olarak raporlanır, yapay skor için gizlenmez.

### 052 — Kullanım ve sürüm dokümantasyonu

- Yeni mutant kontrolleri dahil65 motor birim/property testi geçti (0,68 saniye).
- README artık çalışan ürün, kurulum, 12 E2E, gerçek CI/mutasyon/eval kanıtları,
  demo hesabı, insan kabul sınırları ve üretim ayrımını anlatıyor.
- CHANGELOG başlangıç ve0.2.0 finans demo kapsamıyla eklendi. Pages bağlantısı
  hazırlanmış yayın adresidir; canlı yayın doğrulaması henüz sonraki adımdadır.

### 053 — Mutasyon inceleme raporu ve geçici işlerin kaldırılması

- Yeni testlerle Linux run37171192788 SUCCESS; sonuç artifact'ı indirildi.
  Güncel sayım raporun sonuç alanından alınarak aşağıdaki kayıtta kesinleştirilecek.
- İncelenen gerçek test boşlukları ve metrik sınırlamaları MUTASYON_RAPORU.md'ye
  yazıldı. Yaşayan mutantlar gerçek AI bug sayılmadı.
- Geçici geliştirme dalı push tetikleyicisi ve hard-coded survivor export
  kimlikleri kaldırıldı; nightly yalnız schedule/elle tetikleme ve genel metadata
  >=%85 kapısıyla çalışacak. Sürüm sonrası main'de bir kez daha ölçülecek.

### 054 — Güncel mutasyon sonucunun kesinleştirilmesi

- Artifact commit40c5442: **342 killed /369 toplam = %92,68**, 27 survived,
  diğer durum0. Ek kontroller yedi mutantı daha yakaladı; yaşayanları çıkarmadan
  ham skor raporlandı. README ve mutasyon raporu bu gerçek sayımla güncellendi.

### 055 — Güncel tam yerel kalite sonucu

- Lint ve106 Python dosyasının format kontrolü temiz. **261 test geçti**
  (6,70 saniye); JSON/HTML/JUnit raporları gerçek sonuçlarla yeniden üretildi.
- Yeni DB sınır testleri ve güçlendirilmiş iki motor testi toplam envantere
  eklendi. Son motor dal ölçümü44/44; eski252 sayısı tarihî CI kanıtı olarak korunur.

### 056 — Mobil kabul ve son demo görünümü

- Aynı12 E2E iPhone13 emülasyonunda da geçti (7,32 saniye); ekran görüntüleri
  reports/mobile-e2e içinde. Mobil kartlar tek sütun, menü satıra yayılıyor.
- --noreload sunucunun şablon önbelleği eski860px CSS'i tuttuğu görüldü;
  yalnız kendi sunucu süreci yeniden başlatılıp reload sonrası1160px görünüm
  ve güncel ekran görüntüsü doğrulandı. Son sunucu session58801, port8001.
- Rapor sekmesi çıktı olarak bırakıldı. Bu işlem yeni finans hesabı değiştirmedi.

### CI-DEMO — Bilinçli hatalı değişiklik

- Yalnız test/ci-gate-demo dalında stopaj %1 yerine %2 yapıldı; beklenen
  değer/test değiştirilmedi. Bu kalite kapısı gösterimidir, gerçek AI bug değildir.
- Dal hiçbir zaman birleştirilmeyecek; kırmızı required quality ve merge
  engeli doğrulanınca PR kapatılacak. Normal main motoru korunur.
