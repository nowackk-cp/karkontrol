# Bağlam devri — 2026-10-04 / v1.1.0 teslimi

Kullanıcı bütün planı tamamla, soru sorma, full computer use yetkisi verdi.
Her tamamlanan işlem projede yapılanlar.md'ye hemen yazılır; AGENTS.md geçerli.
Otomatik compact sonrası bu not, günlük ve Git durumundan devam edilir.

## Teknik teslim durumu

Yazılım, otomatik QA ve sürüm teslimi tamamlandı. Yeni kod işi veya açık PR yok.
v1.1.0 public: https://github.com/nowackk-cp/karkontrol/releases/tag/v1.1.0
Remote main/tag source ae5297f0858da645487b0fac5648372ce46621b4.
PR#6 uygulama, PR#10 ilk yeni set kanıtı normal required checks sonrası squash
merge edildi. Main quality + model-eval strict/enforce_admins=true; bypass yok.
Son main CI37176425935/Pages37176484284 SUCCESS; live HTTP200 doğruae5297f.
Yerel main üzerinde sonraki günlük/bağlam kayıtları vardır; source kod aynı.
Eski main14ea542 archive/main-v1-bookkeeping olarak korunur; reset/silme yok.

## Gerçek kalite kanıtı

316 core +12 bağımsız Chromium E2E; aynı12 akış iPhone13 tekrarında geçti.
Motor44/44=%100; motor değişmedi, Linux mutmut342/369=%92,68 kanıtı geçerli.
Son yerel genel satır+dal95,881%; eski v1 %97,67 tarihî kanıttır.
Qwen3-1.7B-Q8_0 / llama.cpp b11382 / temperature0 / Linux CPU:
- İlk37173824046 FAILED: v1 13/40, v2 34/40,5 kritik hata; rapor saklandı.
- Düzeltilmiş37174071378 ve main37175716006: v1 19/40, v2 40/40,
  0kritik;21 iyileşme0gerileme. Her prompt36 gerçek çağrı +4 ön red.
- Son PR#10 f6c1da3 quality55s, model37176164679 SUCCESS/4m43s.
- İlk ve TEK yeni set37175718839 SUCCESS/1m46s, v2 10/10,9 çağrı+1 ön red.
  PromptSHA89ab8fb2b790d66641a398fba9ea2aadcc13bf293d80e54be66ef6a1abc93ff5.
  SoruSHA6c96312a4ca8517e5f1277f6215b80017c60d4178404c9367ec14314b55c346d.
  Root soruları ancak eval sonrası okudu; prompt değişmedi, rerun yapılmadı.
  Aynı Qwen'in soruları niyet şablonu/kısmen doğal olmayan dildir; bağımsız insan
  holdout/genellenmiş kullanıcı doğruluğu değildir. İLK SETİ TEKRAR ÇALIŞTIRMA.
Raw data/evidence/llm-first.json, llm-corrected.json, holdout-first/ kalıcı.
Release10 ekin uzak digest/size değeri yerel dosyayla doğrulandı.

## Bağımsız kabul açık

40 senaryo XLSX'inde7 expected + reviewer/date/source BOŞ, counter0/40.
20 gerçek model hakem puanı12pass/8fail; insan puanları NULL.
Golden CLI exit1 SIP01; insan judge kalibrasyonu exit1 J01.
AI motor çıktısından veya AI hesabından insan golden/puan üretmek yasak.
Gerçek satıcı sözleşmesi kabulü yok. Resmî Amazon/FBA farkları belgeli.
Codex kullanıldı; Claude/ai-v1 izolasyonu ve motor öncesi insan seti geçmişe
 dönük yapılmış gibi gösterilmez. Özgün özel planın16 gerçek kutusu işaretlendi;
insan/historik/kişisel hesap görevleri açık olarak korunur. Bu yüzden özgün
bağımsız insan onaylı plan bütünü tamamlandı iddiası yok.

## Sunulan belgeler ve hesap işleri

CV proje bölümü/ön yazı docs/BASVURU_MATERYALI.md; kişisel CV dosyası yok.
Başvuru/e-posta/LinkedIn mesajı gönderilmedi. Hata Issue#7/8/9 CLOSED;
gerçek önceki fix commit/PR kanıtı geriye dönük kayıt olarak açıkça belirtilir.
Gerçek motor bug0; üç uygulama/model bug vardır. PR#4 kontrollü kırmızı demo.
GIF docs/assets/ci-kapisi.gif API kaydı animasyonudur; canlı ekran kaydı değildir.
GitHub nowackk-cp/nowackk-cp profil README yayımlandı, soncommitc3a5ea4.
Gerçek ad/bio mevcut. Profil pin/fotoğraf değişimi ve diğer repo secret taraması
 yapılmış gibi gösterilmez. In-app GitHub oturumu açık değildi.

## Ortam ve araçlar

Windows PowerShell/uv0.11.26/Python3.13.14/Django5.2.17. approval never;
sandbox_permissions verme. pytest python -m ile çağrılır. Subagent yetkisi yok.
Qwen1.834.426.016byte SHA256 doğrulandı .local/llm. Windows native runtime
CodeIntegrity3077/3033, ggml.dll exit0xC0E90002 ile engelli. Güvenliği değiştirme
ve DLL load/rename bypass yapma. Gerçek model Linux CI'da çalıştı; local offline.
8001 own server session24306 --noreload, /health OK. Browser NodeREPL
agent/browser/tab/fs mevcut; tabid2 store2 kâr raporu teslim sekmesidir.
Demo-satici/demo-only-pass-2026 sentetik hesap; kâr-20.01/hakediş34.74/netsatış124.99.
Güncel ekran reports/screens/profit-report-v1.1.png. Browser profil tabı da var.
Workbook outputs/remaining-acceptance/insan_inceleme.xlsx, release/data kopyası
aynı bytes; tüm renderler doğrulandı. Spreadsheet marker yalnız1 kez kullanıldı.
OpenAI Docs, Computer Use, Spreadsheet ve Browser skills/guidance okundu.
CU uygulama otomasyonu gerekmedi. .local/artifacts scriptleri Git dışında;
release digest kontrolü verify_release.py. reports/release-proof.json ham API kaydı.
apply_patch aynı dosyaya tek operasyon kabul eder; tüm patch atomiktir.
Günlük sonu105; teknik işi tekrar başlatma veya kör seti tekrar çalıştırma.
