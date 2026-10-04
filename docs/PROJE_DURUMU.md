# Kapsam ve kabul durumu

2026-10-04, v1.0.0 demo sürümü. Kullanıcının kesintisiz tamamlama talimatıyla
işlevsel ürün ve otomatik kalite katmanları tamamlandı; bağımsız insan veya
harici hizmet gerektiren kanıtların yokluğu gizlenmez.

| Plan fazı | Uygulanan çıktı | Kabul sınırı |
|---|---|---|
| 0 Kurulum | Python/Django/SQLite/uv, lint/test/CI, protected main | Çalışıyor |
| 1 Kurallar | Tarihli resmî kaynak özeti ve demo-v1/v2 sözleşmesi | AI yazımı; gerçek sözleşme/insan onayı yok |
| 2 Altın veri | 30 TRY +10 Amazon sentetik girdi, boş inceleme şablonu | İnsan hesaplı golden beklenenler yok |
| 3 Motor | Django bağımsız Decimal motoru | Codex tarafından yazıldı; Claude/ayrı agent izolasyonu yok |
| 4 QA | Unit/boundary/Fraction/property/SQL/integration/mutmut | Teknik doğrulama; insan golden kabulü ayrı |
| 5 CI | Protected PR, test/coverage/E2E gate, artifact/Pages | Uzak kanıtlar günlüğe kaydedilir |
| 6 UI | Auth, stores, import, report, return, fake subscription | 12 bağımsız E2E çalışır |
| 7 Asistan | Owner tools, sayı guardrail, 40 soru/SQL eval | Deterministik; LLM/judge/kör hold-out değil |
| 8 Amazon | Sabit USD/EUR/TRY, 10 girdi, eski TRY regresyonu | Sentetik ücretler ve vergi sözleşmesi |
| 9 Cilalama | Mimari, kullanım, QA/eval/mülakat notları, sürüm | Başvuru/mesaj gönderimi yapılmaz |

Bu tablo “bütün insan onaylı plan bitti” iddiası taşımaz. Yazılım demo kabulü
ile bağımsız finans kabulü farklıdır. Eksik insan kanıtları için sahte Excel,
hakem puanı, bug veya metrik oluşturulmaz.

İşlevsel kabul: 261 test, 12 E2E, mobilde aynı 12 akış, motor 44/44 dal,
mutasyon 342/369=%92,68 ve 40/40 deterministik asistan sorusu. Pages raporları
canlı ve HTTP200. Kırmızı PR engeli doğrulandı. Detaylar günlüktedir.
