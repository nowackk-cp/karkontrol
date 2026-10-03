# QA stratejisi

Durum: başlangıç taslağı, 2026-10-04.

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
Motor aşamasında kurallara dayanan birim/sınır testleri, Hypothesis değişmezleri
ve insan doğrulamalı 30 sipariş mutabakatı gelir. Entegrasyonda dosya → DB →
rapor zinciri, E2E'de yalnızca kritik kullanıcı akışları test edilir.

Altın beklenenler motor çıktısından alınmaz. Hesaplama testleri finansal
alanları tam `Decimal` eşitliğiyle karşılaştıracak. Property testinin motorun
formülünü tekrarlaması tek başına bağımsız doğrulama sayılmaz.

## Şimdilik kapsam dışında

Gerçek ödeme, canlı kur API'si, pazaryeri bağlantısı, reklam/taksit gideri ve
gerçek müşteri verisi yok. LLM eval ve mutasyon skoru motor tamamlandıktan
sonra ölçülecek; yer tutucu sayılar veya ölçülmemiş başarı yüzdeleri yayımlanmaz.

## Başlangıç kalite kapısı

Lint → format → Django sistem kontrolü → migration farkı → birim ve
entegrasyon testleri. Raporlar artifact olarak saklanır. Motor geliştirilince
dal kapsamı ≥ %90 ve Linux mutasyon skoru ≥ %85 hedefleri eklenir; bunlar
başlangıç uygulaması için ölçülmüş sonuç değildir.
