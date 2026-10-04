# Bağlam devri — 2026-10-04 / v1.1 kabul işleri

Kullanıcı bütün planı tamamla, soru sorma, full computer use yetkisi verdi.
Her tamamlanan mantıksal işi projede yapılanlar.md'ye hemen yaz. AGENTS geçerli.
Otomatik compact sonrası bu not/Git/günlükten devam et. Subagent yetkisi yok.

## Şu anda aktif iş

Branch feat/remaining-acceptance, remote source4fe480f. PR#6 DRAFT, attached.
Repo github.com/nowackk-cp/karkontrol. v1.1.0 paket/lock hazır, release yok.
Main hâlâc65cc65/v1.0.0; bu branch eski local3 bookkeeping commit'ini de taşır.
PR son source4fe480f quality37174580100SUCCESS, offline eval37174580073SUCCESS;
required model-eval37174580104 çalışıyor. GitHub main required contexts artık
quality + model-eval, strict=true, admins policy korunur. Tüm PR'larda LLM çalışır.
Son local log080 + mevcut belge değişimleri henüzcommitlenmedi.

## Yapılanlar ve gerçek kanıt

316 core test,12 E2E geçti; engine44/44dal100%. Motor hiç değişmedi;
önceki mutmut342/369=%92,68 kanıtı geçerli. Yeni toplam coverage yaklaşık96%.
Gerçek Qwen3-1.7B-Q8_0 + llama.cppb11382 Linux CPU temperature0:
- İlk run37173824046FAILED: v1%32,5, v2%85,5kritikfail; rapor korunur.
- Düzeltilmiş run37174071378SUCCESS: v1%47,5(19/40),v2%100(40/40),
  21iyileşme0gerileme. Herprompt36gerçekçağrı4uygulamaöncesirefusal.
-20gerçekjudge12pass8fail. İnsan puanlar NULL; kalibrasyon yapılmadı.
Raw data/evidence/llm-first.json,llm-corrected.json; data/draft/judge_review.json.
APP003 modelEylül11 seçimi gerçek hata; JSONdates kullanıcının month/yıl enum'una
bağlandı. Model sadece araçseçer; rakamlarıserverrender. SerbestLLMfinans cevabı değil.

40senaryo XLSX hazırdata/draft/insan_inceleme.xlsx; expected7/reviewer/date/source
BOŞ. outputs/remaining-acceptance/insan_inceleme.xlsx finalexport/renderverified.
check_golden CLI exit1SIP01missinghuman; evaluate_judge--human-review exit1J01missing.
Bu insan verisini AI ile doldurupgolden/puan diyemezsin.
Amazon resmîsayfa+16Nisan2026FBA PDF tarihlerleincelendi; demo perorder80TRY
ile gerçekperunit/kategori/iadefarkları docs/GERCEK_TARIFE_INCELEMESI.md.
Gerçek satıcı sözleşmesi/humanfinanskabulü/geriye dönükClaudeizolasyonu eksik.

## Kalan otomatik iş / sıradaki adımlar

1.37174580104 tam4fe480fmodelCI sonuç/artefact verify. Başarısonra PRreadymerge.
2.Son log/docREADMErequiredcontexts kayıtlarıfinalsmallcommitpushgerekiyor;
   modelCI tümPRhercommit yenidençalışır. Bitene kadar kullanıcıyı soruyla durdurma.
3.Holdoutworkflow .github/workflows/holdout.yml yalnızmanual, main'e girince
   ghworkflowrun holdout.yml --ref main BİR KEZ. Yeni10Qwen soru promptv2hash
   sabitkenüretilir ve soru içerikrootagösterilmeden eval çalışır. Sonuç ister
   başarısızolsun korunur; holdoutsonrasıpromptdeğiştirme, başarıavlamak içinrerun yok.
   SetAIauthoredsameQwen; bağımsızhumanholdoutdiye sunma. Orijinalreserved10seen.
4.Holdoutilkbaşarılı/başarısızartifact indir, evidencecopydocs/logkayıtlarıkoru.
5.v1.1.0 releasecorrectmaincommit, CI/PagesHTTP200currenthead, localcleanGit.
   Finaldegerçekkazanımlarveinsanverisieksikleri açık. Bütüninsanplanbitti iddiası yok.
6.Son log/DEVAM bookkeepinginlocalcommitolmasıkorumalimainPRdöngüsünüönler;
   öncekiprojedetümkaynakpublicdurumuyayımlandıktanlocalfinalkayıtlarayrıcommit.

## Ortam / sunucu / tarayıcı

WindowsPowerShell uv0.11.26Python3.13.14Django5.2.17. approvalnever;
sandbox_permissions verme. pytestmodülçağrısı, nativeconsolelauncherkullanma.
Qwen1.834.426.016byte SHA256verified .local/llm;Windowsllama-server.exe
0xC0E90002ileggml.dllCodeIntegrityEnterprise3077/3033engeli. Güvenliği değiştirme,
DLLload/renameileengeli aşma. GerçekLLMLinuxrunnerdaçalıştı. LocalUIoffline.
8001sunucusession24306 --noreload, ownPID17048stoprestartverified. Healthok.
Browsernodepersistenttabstore2reports, ownerdemo-satici/passworddemo-only-pass-2026,
profit-20.01payout34.74. tab.reloadverified. Browser skillpreviouslyread.
Nodeimageoutputsimage(c)forward, rawbase64 text()yok. tab.markDeliverablefinal.
Latestreportimage reports/screens/profit-report.png fromprevious v1 samefinance.
Workbookpreview verified noerrorsclippedcounterfixed. Spreadsheet skillalreadyread;
artifactbundleJSbuilder.local/artifacts/build_review.mjs ignore;markeroncecompleted.
NoactualCUappautomationneeded;computer-useSKILL+guidance/API/confirmationsread.

## Tool/edit notes

apply_patch allhunksatomic. NEVER addbogusplaceholderhunks; 2patchesfailed
completelydueto docs# / logfileanchorincorrect; rerunvalidthirdsucceeded.
Forlongwholerewrite readGetContentoutputJSnormalizeCRLF andapplyminus/plusfull.
PRbodyfilesreports/acceptance-pr-final.md;noJSON.stringify shellescaping.
Loglatest080butrunfurtheractionsimmediatelyrecord081+. Keep progressupdates60sec.
