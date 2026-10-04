# Kanıtlanmış hatalar

Kâr motoru uygulandı; doğrulanmış motor hatası **0**.
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

## APP-002 — Çok uzun adet girdisi doğrulama yerine istisna üretiyor

- Önem: orta; hatalı dosyada kullanıcıya düzgün hata verilemiyor.
- Test: `tests/integration/test_stores_orders.py::test_very_long_quantity_returns_validation_error_without_partial_records`.
- Beklenen: 5000 basamaklı adet için satır numaralı `ImportValidationError`, kayıt yok.
- Gerçekleşen: Python tamsayı dönüşüm sınırından yakalanmamış `ValueError`.
- Kök neden/kaynak: Codex'in bu oturumda yazdığı parser, basamak sayısını
  kontrol etmeden `int()` çağırıyordu.
- Düzeltme: dönüşüm öncesi 10 basamak, ardından taşınabilir 32 bit tamsayı sınırı.
  Sistem sınırı yükseltilmedi, regresyon beklentisi değiştirilmedi.
- TL etkisi: yok; veritabanına yazma öncesinde ortaya çıkar, motor hatası sayılmaz.

## APP-003 — LLM yanlış ayı seçip yanlış aralık için veri yok diyor

- Önem: orta; rapor tutarları değiştirilmez fakat asistan yanlış dönemi gösterir.
- Kanıt: gerçek Qwen eval run37173824046, v2 E-01/E-02/E-10.
- Kullanıcı sorusu: “2026 Eylül net kârım ne?”; beklenen ay9, SQL net kâr-60,00 TL.
- Gerçekleşen: model month11 seçti; Kasım verisi boş olduğu için “veri yok”.
  Bu eksik cevap için bir parasal fark sayısı uydurulmaz; rapor ledger'i doğrudur.
- Kök neden: AI araç seçimine tarih sayısı dönüşümü de bırakılmıştı.
- Düzeltme: JSON şeması kullanıcının açık Türkçe ayına/yılına sabitlenir;
  geçerli aralıkta olsa bile farklı model tarihi uygulama tarafından reddedilir.
- Regresyon: test_turkish_month_is_constrained_before_model ve
  test_valid_but_wrong_month_is_rejected. Gerçek model yeniden ölçümü ayrıca kaydedilir.
- Bu kayıt finans motor hatası sayısına dahil değildir.
