# Передача разработки Wi-Fi QCA9377 —2026-10-09

## Задание и полномочия

Владелец выбрал продолжение нынешнего QCA9377 и передачу незавершённой части
независимому разработчику. Dell, Mac и Yukabox принадлежат владельцу. Требуется
довести физический Dell до WPA2-PSK/CCMP подключения к `iPhone (9)`, действующей
аренды IP и защищённого запроса Dell→Yukabox→Dell. Сохранить город19 и кота.
Наличие программного теста не заменяет аппаратного результата.

Репозиторий: https://github.com/yukakust/rabbit-stack . Исходная ревизия передачи:
`ef62f43` (полный commit записан в манифесте архива). Доступ к закрытому репозиторию
и своим компьютерам предоставляет сам владелец; передача задания не меняет
полномочия аккаунтов. Архив содержит исходники и публичные доказательства,
не готовый установочный пакет. Внешнему разработчику ничего автоматически
не отправлено.

Mac: `/Users/yukakust/rabbit-stack`, командный пункт и локальная подпись.
Yukabox: `/home/yuka/rabbit-world`, native C/ASAN/UBSAN/COFF/EFI/QEMU. Dell:
существующее bare-metal UEFI-окружение; Linux на Dell не устанавливается.
Точная SSH-конфигурация и доступ к Yukabox остаются у владельца.

## С чего начинать

1. Прочитать свежий `docs/CONNECTED-NATIVE-MAC-HANDOFF.md`; старые записи
   исторические, последнее фактическое состояние имеет приоритет.
2. Сопоставить манифест архива с исходниками. Отделить зафиксированные scopes
   от незавершённых локальных черновиков. Собственные изменения вести в новой
   изолированной версии; frozen и подписанные исходники не редактировать.
3. Первый результат разработчика: проверяемая совместная реализация постоянного
   RX/TX, модулей TLS/RSN и управления временем жизни, с измерением полной
   сборки. Пока получить этот результат на Yukabox, без подписи и записи Dell.
4. До физической доставки согласовать с владельцем единственный контроллер,
   свежее состояние и точный прошедший проверки кандидат. Номер66 пока лишь
   следующий возможный номер: он не зарезервирован, пакета/подписи66 нет.

## Что действительно подтверждено

Сохранённый state:
`experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json`.
При сверке этой передачи: `counter=19`, `engine.native_counter=65`,
`native_pending=null`, `hardware_trial_pending=null`. SHA256:
`6ef131faabd28de3a752cae6ccdf7a2fdb18709ee8382e6f07e69ea5f31d9dda`.
Это сохранённое состояние, а не новая квитанция от Dell.

Физическая65: `experiments/native-wifi-qca9377-inventory65-root-route-v1/`
и `evidence/physical65/`. Точная APPLIED65 квитанция и публичный CPU/GetInfo
сняты. Intel i5-8500T, CPUID1 `0x906ea`, RDSEED есть, hypervisor не заявлен,
SRBDS_CTRL не заявлен. GetInfo перечислил CTR256/raw. После закрытия известные
и неопределённые pools0, closed=true. GetRNG/RDSEED не вызывались; сильный
источник случайности ещё не одобрен и не проверен на железе.

Историческая физическая64:
`experiments/native-wifi-qca9377-filter64-root-route-v1/evidence/native64-final/`.
Все12 частей прошивки были приняты, запуск/WMI/ECHO+реальный DMA/HTT3.56 op3
подтверждены. Новый бюджет ожидания ECHO уже успешно проверен: не начинать
работу с повторного исправления старого таймаута63. Пассивный поиск завершился
без целевого beacon, но постоянный RX_RING_CFG тогда отсутствовал: это
не доказательство отсутствия точки доступа. Старые ресурсы/сессия64 закрыты
и архивированы; не возобновлять retired64/завершённый controller65. Не считать
старую работающую прошивку или RAM-asset живыми в текущем65 без свежих данных.

Во время сверки процесс continue65.py не найден. Это не полный перечень
всех Bluetooth-клиентов: перед аппаратной работой проверить общую блокировку
`state.lock`, процессы и фактические сохранённые контроллеры.

## Опорные компоненты

Все пути ниже относительно `experiments/`, с префиксом
`native-wifi-qca9377-`. Читать README, freeze, входные hashes и evidence,
а не судить о готовности по имени каталога.

| Scope | Назначение / граница доказательства |
|---|---|
| `htt-data-path-v1` | HTTop3, descriptor-v1, RX2048/fill1023,33 дополнительных DMA плюс14CE:47 владельцев; программные producer-проверки |
| `htt-warm-stop-v1` | Доказательство остановки target до unmap/free; положительные и отрицательные software-модели |
| `htt-protected-tx-v1` | Защищённый Ethernet TX, реальные modeled DMA+HTT joins; физически не подтверждён |
| `htt-authenticated-ll-rx-v1`, `rx-pn-ledger-v1` | Проверка RAW RX, MIC/FCS/PN/RSC/эпохи до принятия кадра |
| `station-wire-v1`, `station-native-glue-v1`, `station-integration-v1` | WMI AUTH/ASSOC, AID/PEER_MAP и PTK/GTK SEC joins; установка ключей сама по себе не открывает IP |
| `bss-selection-v1` | Точный SSID/BSSID/канал/RSN/скорости/свежесть и совместимость |
| `trusted-rdseed-v2` | Исправленная bounded CF/deadline/source lifetime модель; hardware-source ещё не одобрен |
| `dual-native-parent-v1`, `dual-module-loader-v1` | Общий mapped/counter ledger, реальные EFI owned arenas, две роли/точные hashes/close-unload; нет generic host authority |
| `module-ble-transport-v1`, `module-mac-sender-v1` | Отложенное принятие public signed chunks вне ATT, сохранённая сессия и точный80B receipt; не provisioning |
| `tls-internal-identity-v1` | MbedTLS3.6.7, ключ P256 создаётся внутри child, public fullSPKI/QR; OVMF проверен с synthetic source |
| `tls-cipher-pump-v1`, `qr-paint-only-v1` | Bounded ciphertext/ACK и public QR paint; доверие задаётся реальным typed child, не сетью |
| `mac-tls-client-v1`, `pair-auth-mac-v1` | Проверенные Python fixture TLS13/fullSPKI и public RABPAIR1 builder; не читают настоящий пароль/ключ владельца |
| `network-entropy-v1`, `network-wan-v1` | Hardened lwIP NO_SYS, fallible RNG, DHCP/ARP/TCP/DNS и отзыв IP; ещё не реальные HTT кадры Dell |
| `tls-wan-verification-v1`, `https-protocol-v1` | Проверка CA/name/trustedUTC и bounded fresh nonce HTTP; host/fixture proof, не Dell WAN |

TLS identity PE: file136704/mapped180224, SHA256
`c43a6787487716f192ad1a33bf35058beda4ee1d2d728f4dadf2baf1feeba770`;
это программный результат, не установленный модуль Dell.

## Незавершённые черновики — обязательно проверить заново

- `persistent-parent-v1`: город+47 владельцев+stop+owned beacon.
  В `consumers.c` capability поля ещё закрыты нулём. Есть source-bound proposal
  rates/PSK/CCMP и новая проверка SERVICE_READY PHY bit2/band/power. Связать
  их с фактически включённой реализацией, не с битом от точки доступа.
  `full_measure.py` лишь принудительно линкует методы для измерения размера;
  это не вызовы рабочего state machine и не native admission. Старые
  ARCHITECTURE заметки об установке двух протоколов не заменяют новый direct DN.
- `mature-async-station-bridge-v1`: genuine mature handshake модель подготовлена,
  но окончательный полный replay/COFF/freeze не завершён. Удерживаемый M4 должен
  дождаться PTK/GTK joins; retransmit не переустанавливает ключи/не сбрасывает
  deadline. Async ABI отдельно от старой frozen child-v2.
- `tls-parent-lease-v1`: typed parent/source/child spans и owner RABPAIR1
  AUTH черновики, без окончательного общего доказательства.
- `identity-wan-measure-v1`: попытка совместить private identity и WAN CA/name/time
  в пределах image cap; README скопирован из identity и не доказывает новый WAN.
- `supplicant-native-v2`: старый локальный source scope, часть зависимостей
  mature-сборок; архивирован как черновая зависимость, не новый результат.

Архив включает эти текущие source-only drafts. Генерируемые `runs/`, executables,
RAM-файлы прошивки, приватная конфигурация Mac/SSH и секреты не включены.
Не хватает текущего compiler/trace closure — восстановить и проверить на
Yukabox до admission, не заменять неизвестные inputs моделями или Booleans.

## Порядок завершения

1. Соединить parent, обе роли child и реальные lifetime/epoch/owner интерфейсы.
   Учесть единый mapped ledger, реальные DMA owners, SERVICE_READY full-reorder,
   refill/backpressure, остановку до и после публикации CFG, безопасный отказ.
   Разделить тяжёлую отрисовку и обслуживание сети. Все executable modules
   должны быть включены в проверенный code-set до source approval/QR.
2. Проверить настоящие RX и пассивный поиск13 каналов2.4GHz. Только фактический
   beacon с точными байтами `iPhone (9)`, совместимый WPA2-PSK/CCMP; выбрать
   лучший RSSI среди совместимых. Прочитать настоящее hardware/rate/RSN evidence.
3. Проверить сильный entropy source в текущем trusted bare-metal окружении.
   Не читать не заявленный MSR, не выдавать CPU flags/GetInfo labels за качество
   entropy. Reviewed trusted-only RDSEED-v2 branch описан в основном handoff;
   никакой source approval по сетевому Boolean.
4. Создать private Dell identity, показать полный SPKI QR, получить физическую
   сверку владельцем; owner-signed одноразовый RABPAIR1 связывает target,epoch,
   code-set,DellSPKI,clientSPKI,nonce и parent-issued lifetime. Затем настоящий
   TLS13 без0RTT/resumption и локальный защищённый ввод пароля на Mac.
5. Mature supplicant: реальные AUTH/ASSOC/AID/PEER_MAP/EAPOL, publication+DMA,
   PTK/GTK и свежие HTT SEC_IND, M4 completion, локальный controlled port.
   Затем lwIP на owned authenticated HTT frames, DHCP/ARP, conflict/lease/renew
   и отзыв IP/port на разрыв связи.
6. HTTPS с настоящими CA/name/trustedUTC. Минимальный Yukabox loopback9784,
   отдельный Tailscale Funnel10000; не менять443/8443. Свежий nonce Dell,
   проверенный ответ и тот же nonce/request в серверном логе. Закрыть временный
   endpoint после проверки. Лишь затем отключить Wi-Fi automation.

## Проверки и неизменяемые условия

Каждый кандидат: source/admission, ASAN/UBSAN, COFF, повторяемые EFI, normal/EMPTY
QEMU и текущий world19 на Yukabox. Negative cases: wrong/duplicate/expired
responses, missing DMA/credits, epoch mismatch, buffers exhausted, malformed
RX/descriptors, partial/ambiguous stop, source/TLS failure, QR/key substitution,
AUTH replay, bad password/MIC/key reinstall, DHCP wrong ACK/conflict/expiry,
bad CA/name/time and repeated nonce. Программные модели помечать отдельно.

File cap262144bytes и mapped cap4MiB сохраняются, общий module image ledger
включает parent+children. Это не общий предел всей RAM: bounded external
arenas/pools имеют явных владельцев; переиспользование только после завершения
обращений. Образ, child hashes, owner/target, ABI, epoch и signing inputs
должны совпадать с exact проверенным кандидатом.

Подпись только локально на Mac владельца, один раз для точного пакета после
свежих квитанций и закрытия ресурсов. BLE строго один контроллер/state.lock;
при обрыве точная сохранённая сессия/остаток, без новой подписи.
Не перезагружать Dell. Не менять USB/bootstrap/OTP/firmware flash. Не покупать
оборудование. Не экспортировать owner key, private Dell key или Wi-Fi password;
никаких credentials по открытому BLE.

## Разделение работ и приёмка передачи

Разработчик возвращает новый scoped diff/commit, точные source/compiler hashes,
results и логи, явные программные/аппаратные факты и список недостающих proof.
Первый milestone — прошедший совместные программные gates unsigned candidate.
Владелец сохраняет подпись и контролирует QR/password; разработчик не получает
приватные ключи. Если физический этап выполняет владелец, требуется конкретный
проверенный кандидат и понятный план восстановления, не команда «попробуй».

Предыдущий агент был остановлен автоматической проверкой с сообщением
«possible cybersecurity risk», без точного tool/line. Передача существующих
исходников независимому человеку не снимает ограничение этого чата. Не
запускать блокированную работу здесь через другого агента/переименование.
Подробности: `docs/WIFI-INTEGRATION-REVIEW-STOP-2026-10-09.json`.

Окончательная приёмка: действующая аренда IP на физическом Dell, настоящий обмен
с точкой доступа и защищённый Dell→Yukabox→Dell со свежим совпадающим nonce.
После этого — видеоканал Unreal и соседний современный район Олимпа по
`docs/CONNECTED-WORLD-CONTROL-PLAN.md`. Сейчас Wi-Fi/IP/WAN не подтверждены.
