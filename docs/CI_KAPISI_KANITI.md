# Kırmızı PR kalite kapısı

Kontrollü gösterim:
[PR #4](https://github.com/nowackk-cp/karkontrol/pull/4), kaynak2aa69c9.
Motorun stopajı %1 yerine bilinçli %2 yapılmıştır. Test/golden beklentisi
değiştirilmemiş, hata gerçek AI bug gibi sunulmamıştır.

[CI37171652470](https://github.com/nowackk-cp/karkontrol/actions/runs/37171652470)
`quality: FAILURE` verdi. PR API'si `mergeStateStatus: BLOCKED` döndürdü.
Main branch protection API'si required quality, strict güncellik ve
enforce_admins=true durumunu doğruladı. Hatalı PR birleştirilmeden kapatıldı;
başarısız kalite durumunda merge komutu denenmedi ve yönetici bypass kullanılmadı.

Normal [PR #3](https://github.com/nowackk-cp/karkontrol/pull/3) bütün kontrolleri
geçtikten sonra başlık711d329 şartıyla birleştirilmiştir. Main motoru %1
stopaj kullanır. Bu kayıt yayın kapısının işlediğini gösterir; insan code review
ve bağımsız finans golden kabulünün yerine geçmez.
