# Bağlam devri — 2026-10-04

Kullanıcı: soru sorma, bitene kadar devam et; tamamlanan her işi hemen
`projede yapılanlar.md`ye yaz. AGENTS.md kalıcı altın kuraldır. Otomatik compact
sonrası bu not/günlük/Git durumundan devam et; tamamlanan işleri tekrarlama.

## Son durum

İşlevsel finans demosu tamamlandı. Repo https://github.com/nowackk-cp/karkontrol.
PR1/2/3/5 merged; uzak main c65cc65. v0.2.0 ve v1.0.0 demo release yayımlandı.
Son yerel günlük/bağlam kayıtları main üzerindeki bookkeeping commit'lerinde
korunur; ürünün test edilmiş public kaynakları origin/main ve v1.0.0 etiketindedir.
PR4 kasıtlı kırmızı CI demosu kapatıldı, birleştirilmedi. Stopaj normal motorda%1.

261 core test;12 desktop E2E; aynı12 iPhone13 E2E. 40/40 araç asistanı soru
kontrolü. Engine44/44dal%100. Toplam satır+dal%97,67 (rapor%98).
Mutmut3.8 gerçek342/369=%92,68;27 survived, other0. Exception raise satırları
hariç; koşullar/aritmetik dahil, globals/dataclass defaults mutmut3 kapsamı dışında.
Test boşluğu kalan kuruş sırası/maliyet KDV'sinde bulundu; kontroller eklendi,
gerçek motor bug diye sayılmadı. APP001/002 önceki gerçek hatalar BUGS.md'de.

Main kanıtları: CI37171612643, eval37171612606, mutation37171615550 SUCCESS.
Pages37171673012 SUCCESS. https://nowackk-cp.github.io/karkontrol/ ve
/reports/tests.html, /htmlcov/index.html, /reports/e2e.xml HTTP200 doğrulandı.
PR4 CI37171652470 FAILURE (4failed/257passed), mergeState BLOCKED;
protection required quality/strict/enforce_admins=true. Merge denemesi/bypass yok.

## Çalışan kapsam ve dürüst sınırlar

Auth/kayıt, mağaza owner izolasyonu, CSV/XLSX atomik import, iade,
Decimal saf motor, integer-cents ledger, SQL/window aylık görünüm,
filtre/sayfalama/CSV export, Free100/DemoPro fake ödeme3sonuç/idempotency,
owner tools/guardrail deterministik asistan, Amazon TRY/USD/EUR sabit kur.

Ücretler sentetik; gerçek ödeme/LLM/canlıkur/pazaryeri API'si yok.
data/draft 30TRY+10Amazon sadecegirdi; manual_review.csv beklenenlerBOŞ.
İnsan golden, Claude izolasyonu, judge kalibrasyonu, kör holdout iddiası yok.
Reserved10 soruyu geliştirenAI gördü. Kullanıcının600TL örneği ayrı kaynak anchor.
İşlevsel demo kabulü bu bağımsız insan kabulünden ayrıdır. docs/PROJE_DURUMU.md.

## Kalan doğrulama ve gelecekteki kabul

1. Son main CI37172029658 ve takip Pages sonucu kontrol ediliyor; başarılı
   sonuç root günlüğe kaydedilince işlevsel demo işi tamamdır.
2. İnsan golden hesapları, gerçek LLM/judge kalibrasyonu ve kör hold-out ayrı
   kabul işleridir; kullanıcıyı soruyla durdurmadan bunların yokluğu açık belirtildi.
3. Bu sürümde yeni kod gerekmiyor. Yeni istek olmadıkça test/özellik işini baştan
   çalıştırma. Son yerel bookkeeping commit'i public kaynak değişikliği değildir.

## Yerel ortam/tarayıcı

Python3.13.14 uv0.11.26 Django5.2.17; .venv/uv.lock.
8001 --noreload güncel sunucu execsession58801. Eski8000kullanma.
Demo demo-satici/demo-only-pass-2026. store2 kısmi iade1; profit-20,01TL,
payout34,74TL; toolasistan aynı tutarlar. DB sentetik,seedidempotent.
Python/şablon değişimi sonrası kendi PID+CommandLine doğrula/restart/reload.
Django cached template reload tek başına yetmeyebilir.

Browser skill/docs zaten okundu. tools.mcp__node_repl__js kalıcı agent/browser/tab/fs
bağları var, selectedtab store2reports. Screenshot güncel1160px:
C:/Users/emrep/OneDrive/Desktop/proje/reports/screens/profit-report.png.
tab.markDeliverable() çağrıldı; finalöncesiyineçağır ve screenshotfinalembed.
Node tool image sonuçlarını text(object) ile basma; content.image bloklarını image() ile ilet.
Repo pytest headless Chromium testleri ayrı; plugin yalnız selectedtab kontrolü.
Mobil screenshots reports/mobile-e2e. E2E asyncunsafe yalnız sessiontestfixture.

No subagents (user/AGENTS yetkisi yok). Windows approval never, sandbox_permissions verme.
Modül pytestlauncher kullan; güvenlik politikasını değiştirme. PowerShell ardışık
komutlarda hatayı son success ile gizleme. Her mantıksal biten işi logla.
