# Güncel bağlam devri — 2026-10-04

Kullanıcı: soru sorma, bitene kadar devam et; her biten işi günlüğe hemen yaz.
Compact sonrası bu üst bölümü esas al; aşağıdaki eski notlar tarihî başlangıçtır.

## En son durum

- Public repo github.com/nowackk-cp/karkontrol. PR1/2 merged; main189b09b.
- Dal feat/profit-quality-mvp; PR3 açık/sohbete bağlı, son commit0554ab2.
- CI37170676379 SUCCESS: 252 birim/entegrasyon/eval +12 Chromium E2E,
  motor dalları44/44 (%100), toplam yaklaşık%98. Eval37170676353 SUCCESS.
- Mutation37170671098 motor çalışması tamamlandı; export adımı mutmut3.8'de
  olmayan junitxml komutu nedeniyle FAILED. Workflow o komuttan arındırıldı,
  gerçek .meta verisi ve results artifact'ı toplanacak; skor henüz raporlanmadı.
- Geçici nightly push tetikleyicisi yalnız bu geliştirme dalında; ölçüm sonrası kaldır.
- İşlem günlüğü044/045 sonrası yeni uzak kanıtlar sırada. No subagents.

Çalışan: kayıt/giriş; owner mağaza; atomic CSV/XLSX; iade; Decimal saf motor;
integer-cents ledger; SQL/window monthly; filtre/sayfalama/export; Demo Pro100
satır limiti/sahte ödeme3sonuç/idempotence; owner tools/guardrail asistan;
Amazon demoTRYUSD EUR sabit kur. Dış LLM/gerçek ödeme/canlıkur yok.
40 draftinput=30TRY+10Amazon; manual_review.csv beklenenlerBOŞ. İnsan golden,
Claude izolasyonu, kör holdout ve insan judge kalibrasyonu iddia edilmez.
40eval(12/8/6/6/4/4), reserved10 geliştiriciAI tarafından görüldü.
Kullanıcı plandaki600TL example anchor; finansmotor gerçekhata0, APP001/002 önceki.

Yerel server8001 --noreload session66831; Python değişince kendi PID/CommandLine
doğrulanarak restart. Eskiserver8000kullanma. demo-satici/demo-only-pass-2026;
store2 1kısmi iade, profit-20,01 payout34,74. Browser agent/browser/tab/fs zaten
bağlı ve belgeleri okunmuş. tools.mcp__node_repl__js reuse; selectedtab store2
assistant answered same amounts. Screenshot reports/screens/profit-report.png
1160px değişikliğinden önce; finalfresh screenshot/markDeliverable gerekli.
Browser plugin sadece tab kontrolü; pytest headless E2E ayrı repo testpaketi.
E2E session fixture yalnız test için DJANGO_ALLOW_ASYNC_UNSAFE açıp geri alır.

## Bitirilmesi gerekenler — erken durma

1. Mutation exportfix commit/push; gerçek metadata artifactından>=85%ölç;
   eksik anlamlı testleri survivor üzerinden ekle, eşdeğerleri dürüstbelgele.
2. FinansSQLabsolute-totalguard veFXDBconstraints testi; current252+12.
3. README/QA/veri/EVAL_RAPORU/AIçalışma/mimari/mülakat/CHANGELOG/status belgeleri
   güncelle (READMEhâlâ75testmotor yok diyor). İnsan kabul sınırları açık.
4. IntentionalCIblocked ayrıdemoPR oluştur, requiredquality kırmızıdoğrula,
   mergeengelini oku, kapat; AIhatası sayma. HercreatedPR attach.
5. PagesHTMLreports başarılımain CIartifactıyla yayın workflow/ghapiPages enable;
   gerçekURLkontrol, consent tekraristeyen gereksizduraklama yok userauthorizedall.
6. PR3exactfinalhead green kaliteolunca squashmerge mainpull; v0.2.0 ve
   demo v1.0.0release. Mutasyon/eval gerçeksayılarıetkiketlendir.
7. Finalbrowserdesktopmobile düzenkontrol screenshotdeliverable; bütün mantıksal
   işlemlerlog+DevamNotu; sonworkspaceclean/sunucuaçık; nihaiözetkanıtlar/limitation.

Mutmut3.8 source_paths engine/, tests unit/test_profit; -c mutmut_pytest.ini
-p no:django, errorraise-wording only excluded; all conditionsarithmeticincluded.
Linux2worker25min. Modülpytestlauncher kullan; WindowsAppControls değiştirme.
PowerShell multi-command errors must not be hidden by lastsuccessfulexitcode.

---

# Tarihî başlangıç notu (PR2 sonrası)

Tarih: 2026-10-04 (Europe/Istanbul). Proje: KârKontrol.

## Önce oku

`AGENTS.md`, `projede yapılanlar.md`, bu dosya, yereldeki
`KarKontrol_Proje_Plani.md` ve `git status --short`.

## Kullanıcı talimatı

Soru sormadan ilerle. Tamamlanan her işlemi hemen işlem günlüğüne yaz.
Bağlam dolduğunda otomatik compact sonrasında dosyalardan devam et.
Çağrılabilir bir manuel compact aracı bulunmadı.

## Hazır olanlar

- Kalıcı altın kural ve işlem günlüğü.
- Python 3.13/Django 5.2/uv yapılandırması.
- Django paketleri, ana sayfa, giriş/çıkış, DB sağlık kontrolü.
- Ayrı test/yerel/üretim ayarları; üretimde zorunlu güvenlik değişkenleri.
- Oturum/CSRF/admin/sağlık testleri; üretim güvenlik testi.
- CI dosyası, Issue/PR şablonları, dürüst BUGS başlangıcı.
- QA stratejisi, kaynak araştırma özeti, kural ve 30 senaryo taslağı.
- Store/OrderLine/ImportBatch modelleri ve migration'ları.
- Mağaza oluşturma, kullanıcı izolasyonu, atomik CSV/XLSX aktarımı, mükerrer
  önleme, tarih/ürün filtresi, sayfalama ve iade adedi ekranları.
- Yalnızca DEBUG ortamında çalışan, tekrar kullanılabilir sentetik demo komutu.

## Aktif doğrulama

Python 3.13.14 ve Django 5.2.17 kuruldu; `uv.lock` hazır. Başlangıçta indirme,
sürüm bağlantısı ve kilit sorunu yaşandı; yorumlayıcı ve ortam sonradan doğrulandı.

İlk kurulumda 22 test/%91 kapsam vardı. Son turda **75 test geçti** (3,09 saniye,
iki worker); uygulama toplam kapsamı **%96**. Motor kapsamı ölçülmedi.
Ruff lint/format, Django check, migration drift ve yerel migrate başarılı.
Windows console launcher engeli nedeniyle
`uv run python -m pytest` kullan; sistem güvenlik politikasını değiştirme.
Raporlar `reports/tests.html`, `reports/junit.xml`, `reports/coverage.xml`,
`htmlcov/index.html` içinde ve Git dışında.

## Sıra

1. Nihai alan kurallarını ve insan doğrulamalı altın veriyi tamamla.
2. Yalnızca kuralları gören ayrı motor oturumu ve gerçek `ai-v1` etiketi.
3. Mutabakat/property/entegrasyon testleri; gerçek hatalar ve motor kalite kapısı.
4. E2E, asistan eval ve yeni pazaryeri modülü.

## Kanıt sınırları

Henüz onaylı `KURALLAR_v1.md`, `altin_set.csv/xlsx`, motor, mutasyon sonucu,
LLM eval, ödeme entegrasyonu veya E2E paketi yok. İnsan kontrolü yapılmamış AI
hesaplarını elle doğrulanmış altın veri diye sunma. Başvuru notlarını içeren
ana plan `.gitignore` ile yerelde tutulur.

## Güncel GitHub / servis kanıtı

- Public depo: https://github.com/nowackk-cp/karkontrol.
- İlk CI başarılı: https://github.com/nowackk-cp/karkontrol/actions/runs/37163642871.
  `quality` işi 15 saniye, toplam run 16 saniye; rapor artifact'ı doğrulandı.
- `main` korumalı: güncel dal, `quality`, PR zorunlu; yönetici muafiyeti yok.
  İnsan onay sayısı 0; force push ve dal silme kapalı.
- Bu nedenle sonraki kod değişikliklerini ayrı dal ve PR üzerinden gönder.
- Güncel sunucu http://127.0.0.1:8001/ adresinde. Demo hesabı `demo-satici` /
  `demo-only-pass-2026`. Seed yalnızca DEBUG altında çalışır.
- Browser becerisiyle giriş, mağaza, filtre, dosya yükleme/tekrar yükleme ve
  iade doğrulandı; ekran kanıtı `reports/screens/store-orders.png` (Git dışında).
  Sonraki oturumda sunucu durumunu kontrol et; eski 8000 bootstrap sürecine güvenme.
- Başlangıç altyapısı tamamlandı; sıradaki asıl faz, kesin kurallar ve bağımsız
  insan doğrulamalı altın veri. Motorun önce yazılmaması kuralını koru.

Başlangıç PR #1, başarılı CI'nin doğru commit'i doğrulandıktan sonra squash merge edildi.
Güncel çalışma dalı: `feat/store-order-import`; bunun PR/CI durumunu GitHub'dan kontrol et.
PR #2: https://github.com/nowackk-cp/karkontrol/pull/2. Oluşturulduğunda açık;
merge varsayma. Başarılı kontrolün PR'ın en son commit'ine ait olduğunu doğrula.
Uzak CI kanıtı: run 37165639061, commit 72398004020000623b10443af31ff55ee39faffe,
`quality: SUCCESS`. Sonraki sadece belge commit'lerinde de son kontrolü yeniden doğrula.
Son üretim kontrolü `check --deploy --settings config.settings.production`
geçici test ortam değişkenleriyle 0 sorun verdi. Dış sunucuya dağıtım yapılmadı.

## Veri akışı sınırları ve kanıtlar

- Dosya sözleşmesi: `docs/VERI_AKTARIMI.md`. CSV UTF-8, tek sayfalı XLSX,
  TRY, Decimal, 5 MB dosya / 25 MB açılmış XLSX / 5000 satır.
- Kimlik mağaza+numara+satır; farklı içerikte çelişki tüm transaction'ı geri alır.
- APP-001 (sahiplik/HTTP kontrol sırası) ve APP-002 (çok uzun adet ValueError)
  gerçek testlerle bulundu ve beklentiler değiştirilmeden düzeltildi.
  Bunlar motor hatası/finansal doğruluk kanıtı değildir.
- Otomatik Playwright suite, SQL kâr raporu, billing ve asistan hâlâ bekliyor.
