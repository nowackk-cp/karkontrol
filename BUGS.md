# Kanıtlanmış hatalar

Henüz kâr motoru uygulanmadı; doğrulanmış motor hatası **0**.
Kurulum sorunları motor hatası veya satıcıya parasal etkisi olan hata sayılmaz.

Her kayıt: kimlik, önem, kırılan test, beklenen değerin bağımsız kaynağı,
gerçekleşen değer, TL farkı, kök neden ve düzeltme kanıtı içermelidir.
Kasıtlı mutasyonlar AI hatası diye kaydedilmez.

## APP-001 — Yabancı mağazada HTTP yanıtı tutarsızlığı

- Önem: düşük; veri sızıntısı veya finansal hesap hatası bulunmadı.
- Yakalayan test: `tests/integration/test_stores_orders.py::test_foreign_store_routes_return_404`;
  `post-list` ve `post-sample` senaryoları.
- Beklenen: oturum sahibine ait olmayan mağazanın bütün uç noktaları HTTP 404.
- Gerçekleşen: yalnızca okunabilen iki uç noktaya POST gönderilince HTTP 405.
- Kaynak/kök neden: Codex'in bu oturumda yazdığı view'larda HTTP metodu
  denetimi mağaza sahipliği kontrolünden önce çalışıyordu.
- Düzeltme: oturum kontrolünden sonra, metodun önünde ortak sahiplik decorator'ı.
  Test beklentileri değiştirilmedi. Sonuçlar işlem günlüğünde kaydedilir.
- TL etkisi: yok; bu kayıt motor hatası sayısına dahil değildir.
