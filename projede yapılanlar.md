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

### 011 — Bağımlılık kurulumu ve ilk statik doğrulama

- Python 3.13.14 ortamına 23 çalışma/geliştirme paketi kuruldu; Django 5.2.17,
  pytest 9.1.1 ve ruff 0.16.10 kilit dosyasıyla sabitlendi.
- Python dosyaları derleme kontrolünden geçti; `git diff --check` hata vermedi.
- İlk ruff kontrolü bir uzun satır ve iki biçim farkı bildirdi. Formatter
  uygulandı; lint ve format kontrolleri tekrar çalıştırıldı.
- Bu biçim bulguları finansal motor hatası olarak sayılmadı.
