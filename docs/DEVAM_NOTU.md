# Bağlam devri — 2026-10-04 / v1.1 son kabul

Kullanıcı bütün planı tamamla, soru sorma, full computer use yetkisi verdi.
Her tamamlanan işlem kökteki projede yapılanlar.md dosyasına hemen yazılır.
AGENTS.md geçerli. Subagent yetkisi yok. Otomatik compact sonrası bu not,
günlük ve Git durumundan devam et; tamamlanan işleri yeniden yapma.

## Aktif iş

GÜNCEL EK: PR#6 ca995a6 required kontrolleri geçti ve26a174a olarak main'e
birleştirildi. Branch artık feat/holdout-evidence (origin/main26a174a tabanlı).
İlk ve tek holdout37175718839 SUCCESS/10/10/9model+1önred; prompt sabit,
SHA89ab8fb2, sorularSHA6c96312a. data/evidence/holdout-first kalıcı kopya hazır.
Günlük096'ya kadar. Issue#7/8/9 gerçek geçmiş bug kayıtları kapatıldı.
Main CI37175715954/LLM37175716006/Pages37175771165 SUCCESS, liveHTTP200 doğru26a.
Son evidence/docs commit'ini PR olarak gönder, required checks sonrası merge;
v1.1.0 release+assets ve final kaynak CI/Pages doğrula. HOLDOUT RERUN YOK.
Aşağıdaki eski Aktif iş satırları önceki checkpoint'tir; bu güncel ek önceliklidir.

Branch feat/remaining-acceptance, PR#6 ready ve attached.
https://github.com/nowackk-cp/karkontrol/pull/6
Efd464e quality, offline eval ve gerçek model run37174900112 SUCCESS.
Son QA/CV/GIF belgeleri ve günlük085–087 henüz commit/push bekliyor.
Son belge commit'ini push et; zorunlu quality + model-eval geçince PR'ı
normal squash ve --match-head-commit ile birleştir. Admin bypass yapma.
Paket ve uv.lock v1.1.0 hazır; release/tag henüz yok. Main c65cc65/v1.0.0.

## Kalan otomatik teslim

1. Son belgeler lint/format/diff temiz. Yeni kaynak başlığında required CI geçsin.
2. PR#6 merge sonrası holdout.yml --ref main yalnız BİR KEZ çalıştır.
   Prompt v2 SHA256 sabit; yeni10 soruyu eval bitmeden root görmez.
   İlk sonuç başarı/başarısızlık fark etmeksizin korunur. Prompt ayarı/rerun yok.
   AI yazarlı aynı Qwen seti bağımsız insan hold-out diye sunulmaz.
3. Artifact'i indir, kalıcı evidence ve doküman/günlük kaydı ekle.
4. v1.1.0 release doğru main commit'inde yayımla; human workbook/judge ve gerçek
   eval/ilk holdout kanıtı release assets olarak verilebilir. Main CI ve Pages
   güncel kaynakta SUCCESS/HTTP200 doğrula. Başvuru/mesaj gönderme.
5. Son DEVAM/günlük yerel bookkeeping commit'iyle temiz Git bırak; her günlük
   için yeni PR ve model run döngüsüne girme. Eski local main üç bookkeeping
   commit ileride: squash sonrası diverge olursa eski branch'i silme/resetleme;
   arşiv adıyla koruyup origin/main'den yeni main aç.

## Kanıt ve sınırlar

316 core +12 bağımsız E2E geçti; aynı12 akış iPhone13 tekrarında da geçti.
Motor değişmedi:44/44 dal, mutmut342/369=%92,68 önceki Linux kanıtı geçerli.
Gerçek Qwen3-1.7B-Q8_0 + llama.cpp b11382, temperature0 Linux CPU:
- İlk run37173824046 FAILED: v1 13/40, v2 34/40,5 kritik hata; rapor saklanır.
- Düzeltilmiş run37174071378 SUCCESS: v1 19/40, v2 40/40,0 kritik hata;
  21 iyileşme,0 gerileme. Her prompt36 model çağrısı +4 güvenlik ön reddi.
-20 gerçek model hakem puanı12 pass/8 fail; insan puanları NULL.
- APP003 yanlış Eylül→Kasım seçimi: literal yıl/ay JSON enum'a bağlandı.
- Model araç seçer; finans rakamlarını sunucu oluşturur. Serbest LLM finans hesabı değil.
Raw data/evidence/llm-first.json, llm-corrected.json; judge data/draft'ta.
40 XLSX senaryosunda7 expected +reviewer/date/source BOŞ; counter0/40.
Golden CLI exit1 SIP01, human judge CLI exit1 J01: insan kabulü eksik.
İnsan expected/puanlarını AI ile doldurmak yasak. Gerçek satıcı sözleşmesi yok.
Resmî Amazon/FBA incelemesi ve demo farkları docs/GERCEK_TARIFE_INCELEMESI.md.
CV proje bölümü/ön yazı docs/BASVURU_MATERYALI.md; kişisel geçmiş uydurulmadı.
PR#4 gerçek API kaydı data/evidence/ci-gate.json ve4 kare GIF docs/assets'te;
GIF kayıt animasyonudur, canlı ekran kaydı değildir. Gerçek motor bug sayısı0.

## Ortam

Windows PowerShell, uv0.11.26/Python3.13.14/Django5.2.17. approval never;
sandbox_permissions verme. pytest python -m ile çağrılır.
Qwen weights SHA256 doğrulandı .local/llm; Windows native llama-server ggml.dll
CodeIntegrity3077/3033, exit0xC0E90002 ile engelli. Güvenliği değiştirme/bypass yok.
Gerçek LLM Linux CI'da çalışır. 8001 kendi server session24306 --noreload;
local UI offline backend. Browser NodeREPL agent/browser/tab/fs mevcut;
tab store2 assistant ekranında. Demo-satici/demo-only-pass-2026 sentetik hesap.
Kâr-20.01/hakediş34.74/netsatış124.99 rapor ve asistan eşitliği doğrulandı.
Workbook output outputs/remaining-acceptance/insan_inceleme.xlsx, render/doğrulama
geçti, human fields boş. Spreadsheet marker yalnız1 kez yapıldı; tekrar etme.
OpenAI Docs, Computer Use, Spreadsheet ve Browser skill/guidance zaten okundu.
CU uygulama otomasyonu gerekmedi. Node görsellerinde image(c), base64 text yok.
apply_patch aynı dosyaya tek operasyon kabul eder; tüm patch atomiktir.
