# QA stratejisi

Durum: çalışan demo kalite kapıları, 2026-10-04.

## Öncelik

| Risk | Etki (1–5) | Olasılık (1–5) | Önce doğrulanacak davranış |
|---|---:|---:|---|
| Yanlış kâr / hakediş | 5 | 4 | Bağımsız altın veriyle sıfır tolerans |
| İade / indirim karışıklığı | 5 | 4 | Satır ve adet bazında hesap |
| Kuruş farkı | 4 | 5 | Decimal, satır yuvarlaması ve yarım kuruş |
| Mükerrer içe aktarma | 5 | 3 | Tekrar yüklemede aynı toplam |
| Kısmi veri kaydı | 5 | 3 | Hatalı dosyada atomik geri alma |
| Mağazalar arası veri sızıntısı | 5 | 3 | Oturumdan sahiplik; URL ile atlatılamaz |
| Hatalı oturum akışı | 4 | 3 | CSRF, güvenli yönlendirme, çıkış |
| Asistanın uydurduğu rakam | 5 | 3 | SQL araç sonucu ve sayısal doğrulayıcı |

## Doğrulama katmanları

Altyapıda giriş/çıkış, güvenlik ayarları ve servis kontrolü test edilir.
Motor aşamasında kurallara dayanan birim/sınır testleri, Fraction referansı ve
Hypothesis değişmezleri çalışır. İnsan doğrulamalı 30+10 sipariş mutabakatı henüz
kabul edilmemiştir. Entegrasyonda dosya → DB →
rapor zinciri, E2E'de yalnızca kritik kullanıcı akışları test edilir.

Altın beklenenler motor çıktısından alınmaz. Hesaplama testleri finansal
alanları tam `Decimal` eşitliğiyle karşılaştıracak. Property testinin motorun
formülünü tekrarlaması tek başına bağımsız doğrulama sayılmaz.

## Şimdilik kapsam dışında

Gerçek ödeme, canlı kur API'si, pazaryeri bağlantısı, reklam/taksit gideri ve
gerçek müşteri verisi yok. Offline araç ölçümü ve gerçek Qwen ölçümü ayrı
raporlanır. Bağımsız insan golden ve hakem kabulü eksiktir. Yeni set protokolü
AI yazarlıdır; bağımsız insan hold-out kabulü değildir. Yer tutucu metrik yayımlanmaz.

## Başlangıç kalite kapısı

Lint → format → Django sistem kontrolü → migration farkı → birim ve
entegrasyon/eval → motor dal kapsamı ≥ %90 → 12 Chromium E2E.
Raporlar artifact olarak saklanır. Linux gecelik mutasyon kapısı ≥ %85'tir;
yalnız exit1 gerçekten öldürülen sayılır. Hatalı/boş ölçüm başarılı sayılmaz.

## Uygulanan veri akışı testleri

2026-10-04: toplam 75 test; CSV ve XLSX, 30 satırlık sentetik girdi,
DB benzersizlikleri, çelişkide transaction rollback, aynı dosya/farklı biçimde
mükerrerlik, kullanıcı izolasyonu, komisyon ve iade sınırları, tarih/ürün
filtreleri ve sayfalama doğrulandı. Genel uygulama kapsamı %96.

Beklenen fiyatlar yalnızca dosyadaki girdinin veritabanında korunmasını
doğrular; bağımsız altın kâr bekleneni değildir. Gerçek tarayıcı kontrolleri
ayrıca işlem günlüğünde kayıtlıdır. Bu paragraf PR2 sonrası tarihî başlangıç kanıtıdır.

## Finans demo sürümü kanıtları

252 test ve 12 E2E Linux CI'de geçti:
[run37170676379](https://github.com/nowackk-cp/karkontrol/actions/runs/37170676379).
Motor dal kapsamı 44/44 (%100); genel satır+dal kapsamı yaklaşık %98.
Mutmut3.8 ilk tamamlanmış ve artifact'ı alınmış ölçüm 335/369=%90,79:
[run37170823038](https://github.com/nowackk-cp/karkontrol/actions/runs/37170823038).
34 survivor saklanır, gizlenmez. Exception raise satırlarının mesajları mutasyondan
hariçtir; bütün koşullar/hesaplar dahil. Mutmut3 globals ve dataclass varsayılanlarını
mutate etmez; bu sınır metrikle birlikte değerlendirilir. Detaylar ayrı mutasyon raporunda.

Katmanlar teknik riskleri tamamlar. Aynı AI'ın sözleşme ve test yazması alan
hatasının iki tarafa da taşınmasını engellemez; insan inceleme seti boş kalır.

## v1 demo son kabulü

261 unit/integration/property/eval +12 E2E; mobilde aynı 12 akış da geçti.
Toplam satır+dal kapsamı %97,67 (raporda yuvarlanmış %98), motor 44/44.
Güçlendirilmiş mutasyon 342/369=%92,68, yaşayan 27. Main fc27163 üzerinde
[CI](https://github.com/nowackk-cp/karkontrol/actions/runs/37171612643),
[eval](https://github.com/nowackk-cp/karkontrol/actions/runs/37171612606) ve
[mutation](https://github.com/nowackk-cp/karkontrol/actions/runs/37171615550) geçti.
[Canlı HTML raporlar](https://nowackk-cp.github.io/karkontrol/) HTTP200 doğrulandı.
[Kırmızı kapı kanıtı](CI_KAPISI_KANITI.md) dört testi başarısız olan PR'ın
birleştirilmeden kapatıldığını gösterir. Bilinçli hata gerçek motor bug sayılmaz.

## v1.1 gerçek model ve kabul araçları

316 core test ve 12 bağımsız E2E geçti; aynı 12 akış mobilde de geçti.
Motor değişmediği için 44/44 dal ve 342/369 mutasyon kanıtı geçerlidir.
Qwen3-1.7B-Q8_0 Linux CPU üzerinde v1 19/40, v2 40/40;
her prompt 36 model çağrısı ve 4 güvenlik ön reddi içerir. Sayısal beklenti
bağımsız SQL sorgusundan doğrulanır. Model yalnız aracı seçer; cevap tutarını
sunucu oluşturur. [Gerçek ölçüm](https://github.com/nowackk-cp/karkontrol/actions/runs/37174071378).

İlk başarısız model raporu saklanır; Eylül→Kasım seçimi APP-003 olarak kayıtlıdır.
20 gerçek hakem puanı vardır; insan puanları olmadan %85 kalibrasyon iddia edilmez.
Prompt SHA256 sabitken 10 yeni soruluk set üreten manual workflow tek ölçüm içindir;
ilk sonuç korunur ve sonuç görüldükten sonra prompt bu sete göre ayarlanmaz.
40 finans senaryosunun insan beklenenlerini ve kaynaklarını doldurmadan
`scripts/check_golden.py` başarısız olur. [Kabul komutları](KABUL_CALISTIRMA.md).
Main için quality ve model-eval zorunludur; yöneticiler de kurala tabidir.
