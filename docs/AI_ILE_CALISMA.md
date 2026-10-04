# AI ile çalışma kaydı

## 2026-10-04 — Kesintisiz demo tamamlama

Kullanıcının “bitene kadar durma” talimatı, bağımsız insan onayı yokken bütün
geliştirmeyi durdurma yaklaşımını değiştirdi. Demo sözleşmesi açık varsayımlarla
uygulandı; golden sonuç hücreleri boş kaldı. Motor `demo-v1`, asistan `tools-v1`;
AI hesabı insan kanıtı olarak sunulmadı.

| Öneri/karar | Sonuç | Gerekçe |
|---|---|---|
| Atomik import ve siparişin tamamını yeniden hesaplama | Kabul | Yarım kayıt ve çok satırlı ücret hatalarını önler |
| SQL'de integer cents | Kabul | SQLite Decimal toplamasında float riskini kaldırır |
| Kalan kuruşu rastgele dağıtma | Ret | Tekrar hesaplamada aynı sonuç gereklidir |
| Platform kuponunu satıcı indirimiyle birleştirme | Ret | Finansmanı farklıdır, gelir/komisyon farklı davranır |
| 12 kritik E2E + geniş unit/property katmanı | Kabul | Para ve sahiplik riskine odaklanır |
| Logo rengi için otomasyon | Ret | Kritik akış kabulünü güçlendirmez |
| Motor çıktısından golden beklenti üretme | Ret | Aynı hata iki tarafta görünmez olur |
| Bir hatalı testte bekleneni değiştirme | Ret | Envanterde9 reserved hata olduğunda veri10'a tamamlandı |
| Anahtarsız araç asistanı | Kabul | Kullanıcı verisi/kâr hesapları yerelde ve doğrulanabilir kalır |
| Bu sonucu LLM/judge/kör holdout diye sunma | Ret | Bu ölçümler yapılmadı |
| Kasıtlı CI demo hatasını gerçek AI bug sayma | Ret | Gate kanıtı ile bug kaydı farklıdır |

İlk mutasyon ölçümü 335/369=%90,79; yaşayan mutantlar raporda korunur.
Şeffaf araç/kapsam/kanıt sınırı projenin kabul kuralıdır.

## 2026-10-04 — Başlangıç

Araç: Codex. Bu çalışmanın Claude Code ile yapıldığı iddia edilmez.
Kullanıcı talebi: projeye başla; her tamamlanan işlemi `projede yapılanlar.md`
dosyasına yaz ve bunu altın kural olarak ekle; soru sormadan ilerle;
bağlam dolduğunda compact yap.

| Karar | Sonuç | Gerekçe |
|---|---|---|
| Python 3.13 + Django 5.2 altyapısı | Kabul | Ana planla uyumlu |
| İnsan kontrolü olmayan AI altın hesapları | Ret | Bağımsız kâhin kuralını ihlal eder |
| Ölçülmemiş CI/kapsam/mutasyon rozeti | Ret | Gerçek kanıt yok |
| Giriş ve sağlık kontrolü testleri | Kabul | Çalışır altyapı ve güvenlik doğrulanır |
| Üretim ve yerel ayarları ayırma | Kabul | Yerel kolaylıklar üretime taşınmaz |
| Kaynaklardan alan araştırma özeti | Kabul, taslak | İnsan yazarlığı/onayı iddia edilmez |

### Bağlam devamlılığı

Compact işlemi uygulamanın otomatik bağlam yönetimine bağlıdır; bu oturumda
çağrılabilir bir compact aracı bulunmadı. `AGENTS.md`, işlem günlüğü ve
`DEVAM_NOTU.md` dosyaları sonraki oturumların aynı işten devam etmesini sağlar.

### Motor bağımsızlığı

Henüz motor üretilmedi, `ai-v1` etiketi konmadı. Kurallar ve bağımsız altın set
tamamlandığında ayrı oturumda yalnızca onaylı kurallar gösterilecek. Gerçek
prompt ve ilk sürüm o aşamada kaydedilecek.

## 2026-10-04 — Veri akışları

Kullanıcı talebi: "devam et projeye". Önceki soru sormadan ilerleme ve her
işlemi günlüğe yazma talimatı korunur. İnsan doğrulamalı altın veri bulunmadığı
için finansal motor yerine bağımsız mağaza/aktarım altyapısı geliştirildi.

| Öneri/iş | Karar | Kanıt/gerekçe |
|---|---|---|
| Mağaza sahipliğini POST alanından alma | Ret | Oturum sahibinden belirlenir |
| Kısmi dosya aktarımını kabul etme | Ret | Yanlış sipariş toplamı riski |
| Mükerrerleri dosya hash'iyle tek başına önleme | Ret | Farklı dosyada aynı satır için DB benzersizliği de gerekli |
| Testi 404 yerine 405 kabul edecek şekilde gevşetme | Ret | APP-001 sahiplik sırası düzeltilerek çözüldü |
| Çok uzun adet için Python dönüşüm sınırını artırma | Ret | APP-002 girdi sınırıyla çözüldü |
| UI'da hazır olmayan kârı 0 gösterme | Ret | Kâr/hakediş henüz hesaplanmıyor |
| Sentetik demo ve gerçek tarayıcı akışı | Kabul | Yerel kullanım ve kullanıcı akışı doğrulaması |

Son doğrulama: 75 test geçti, uygulama toplam kapsamı %96. Browser becerisiyle
giriş, mağaza, filtre, örnek dosya/tekrar aktarım ve iade gerçek tarayıcıda
doğrulandı. Bu kontroller otomatik Playwright test paketi diye raporlanmaz.
