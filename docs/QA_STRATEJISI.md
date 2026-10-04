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
gerçek müşteri verisi yok. 40 soruluk ölçüm deterministik araç asistanına aittir;
LLM/judge/kör hold-out değildir. Yer tutucu metrik yayımlanmaz.

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
