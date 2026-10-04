# Kapsam ve kabul durumu

2026-10-04, v1.1.0 kabul araçları geliştirmesi. Kullanıcının kesintisiz tamamlama talimatıyla
işlevsel ürün ve otomatik kalite katmanları tamamlandı; bağımsız insan veya
harici hizmet gerektiren kanıtların yokluğu gizlenmez.

| Plan fazı | Uygulanan çıktı | Kabul sınırı |
|---|---|---|
| 0 Kurulum | Python/Django/SQLite/uv, lint/test/CI, protected main | Çalışıyor |
| 1 Kurallar | Tarihli resmî kaynak özeti ve demo-v1/v2 sözleşmesi | AI yazımı; gerçek sözleşme/insan onayı yok |
| 2 Altın veri | 40 siparişlik XLSX, CSV aktarımı, kuruş mutabakat komutu | İnsan hesaplı golden beklenenler yok |
| 3 Motor | Django bağımsız Decimal motoru | Codex tarafından yazıldı; Claude/ayrı agent izolasyonu yok |
| 4 QA | Unit/boundary/Fraction/property/SQL/integration/mutmut | Teknik doğrulama; insan golden kabulü ayrı |
| 5 CI | Protected PR, test/coverage/E2E gate, artifact/Pages | Uzak kanıtlar günlüğe kaydedilir |
| 6 UI | Auth, stores, import, report, return, fake subscription | 12 bağımsız E2E çalışır |
| 7 Asistan | Gerçek Qwen, v1/v2 SQL eval, hakem ve ilk yeni set10/10 | İnsan kalibrasyonu yok; aynı model yazarlı sentetik set bağımsız insan hold-out değildir |
| 8 Amazon | Sabit USD/EUR/TRY, 10 girdi, eski TRY regresyonu | Sentetik ücretler ve vergi sözleşmesi |
| 9 Cilalama | Mimari, QA/eval/mülakat/CV notları, gerçek kayıt GIF'i, sürüm | Başvuru/mesaj gönderimi yapılmaz |

Bu tablo “bütün insan onaylı plan bitti” iddiası taşımaz. Yazılım demo kabulü
ile bağımsız finans kabulü farklıdır. Eksik insan kanıtları için sahte Excel,
hakem puanı, bug veya metrik oluşturulmaz.

Son yerel kabul:316 test,12 E2E, motor44/44dal. Motor değişmediği için
önceki mutasyon342/369=%92,68 kanıtı geçerlidir. Gerçek Qwen run37174071378:
v1%47,5, v2%100, kritik hata0.20 gerçek hakem puanı mevcut; insanla uyumu
bilinmiyor. Windows native model çalışması Code Integrity tarafından engellendi;
model Linux CI'da çalışır, yerel ürün offline backend ile kullanılabilir.

İlk ve tek yeni set run37175718839 SUCCESS/10/10;9 model çağrısı ve1 ön red.
Prompt/question SHA256 doğrulandı ve prompt değiştirilmedi. Soruların bir kısmı
şablon dili olduğundan bu sonuç bağımsız insan hold-out başarısı sayılmaz.
Ham sorular/cevaplar/hash'ler data/evidence/holdout-first altında korunur.

Gerçek Amazon/FBA tarifeleri incelendi ve demo farkları belgelenmiştir.
Satıcıya özel sözleşme, insan golden/hakem puanları ve geçmişe dönük Claude
izolasyonu full computer use yetkisinden doğmaz. Eksikler kabul araçlarınca
raporlanır; otomatik olarak insan onayı verilmiş sayılmaz.
