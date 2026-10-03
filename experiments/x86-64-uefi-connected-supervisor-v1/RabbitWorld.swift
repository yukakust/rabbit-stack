import AppKit
import AVFoundation
import Speech
import CoreBluetooth
import Darwin

struct Connection: Decodable { let url: String; let token: String; let pid: Int32 }
struct Configuration: Decodable { let python: String; let server: String; let state: String; let connection: String; let path: String }

final class Application: NSObject, NSApplicationDelegate, CBCentralManagerDelegate {
    var window: NSWindow!
    let input = NSTextField(string: "")
    let stateLabel = NSTextField(labelWithString: "Подключаю управление миром…")
    let speechLabel = NSTextField(labelWithString: "Напиши, что хочешь увидеть, или нажми «Говорить».")
    let output = NSTextView()
    let send = NSButton(title: "Изменить мир", target: nil, action: nil)
    let microphone = NSButton(title: "Говорить", target: nil, action: nil)
    let speechSetup = NSButton(title: "Настроить голос", target: nil, action: nil)
    let bluetoothSetup = NSButton(title: "Настроить Bluetooth", target: nil, action: nil)
    var bluetooth: CBCentralManager?
    let resume = NSButton(title: "Продолжить передачу", target: nil, action: nil)
    let history = NSPopUpButton()
    let restore = NSButton(title: "Вернуть версию", target: nil, action: nil)
    var connection: Connection?
    var config: Configuration!
    var serverProcess: Process?
    var versions: [[String: Any]] = []
    var timer: Timer?
    var engine: AVAudioEngine?
    var request: SFSpeechAudioBufferRecognitionRequest?
    var task: SFSpeechRecognitionTask?
    var recognizer: SFSpeechRecognizer?
    var listening = false
    var speechGeneration = 0
    var submittedGeneration = -1
    var speechDeadline: Timer?
    var tapInstalled = false

    func applicationDidFinishLaunching(_ notification: Notification) {
        do {
            let resource = Bundle.main.url(forResource: "Configuration", withExtension: "json")!
            config = try JSONDecoder().decode(Configuration.self, from: Data(contentsOf: resource))
        } catch { fatalError("Missing local controller configuration") }
        let menu = NSMenu()
        let appItem = NSMenuItem(); let appMenu = NSMenu()
        appMenu.addItem(NSMenuItem(title: "Закрыть Rabbit World", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))
        appItem.submenu = appMenu; menu.addItem(appItem)
        let editItem = NSMenuItem(title: "Правка", action: nil, keyEquivalent: ""); let edit = NSMenu(title: "Правка")
        edit.addItem(NSMenuItem(title: "Вырезать", action: #selector(NSText.cut(_:)), keyEquivalent: "x"))
        edit.addItem(NSMenuItem(title: "Копировать", action: #selector(NSText.copy(_:)), keyEquivalent: "c"))
        edit.addItem(NSMenuItem(title: "Вставить", action: #selector(NSText.paste(_:)), keyEquivalent: "v"))
        editItem.submenu = edit; menu.addItem(editItem); NSApp.mainMenu = menu
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 780, height: 560),
                          styleMask: [.titled, .closable, .miniaturizable, .resizable], backing: .buffered, defer: false)
        window.title = "Rabbit — управление миром"
        window.center()
        let stack = NSStackView(); stack.orientation = .vertical; stack.spacing = 14; stack.alignment = .leading
        stack.translatesAutoresizingMaskIntoConstraints = false
        window.contentView!.addSubview(stack)
        NSLayoutConstraint.activate([stack.leadingAnchor.constraint(equalTo: window.contentView!.leadingAnchor, constant: 22),
            stack.trailingAnchor.constraint(equalTo: window.contentView!.trailingAnchor, constant: -22),
            stack.topAnchor.constraint(equalTo: window.contentView!.topAnchor, constant: 22),
            stack.bottomAnchor.constraint(equalTo: window.contentView!.bottomAnchor, constant: -22)])
        input.placeholderString = "Например: кот идёт быстрее; добавь мышку; сделай фон синим"
        input.font = .systemFont(ofSize: 17); input.target = self; input.action = #selector(sendText)
        input.translatesAutoresizingMaskIntoConstraints = false
        stateLabel.font = .boldSystemFont(ofSize: 17)
        speechLabel.lineBreakMode = .byWordWrapping; speechLabel.maximumNumberOfLines = 3
        stack.addArrangedSubview(stateLabel); stack.addArrangedSubview(input); stack.addArrangedSubview(speechLabel)
        input.widthAnchor.constraint(equalTo: stack.widthAnchor).isActive = true
        let buttons = NSStackView(views: [send, microphone, resume]); buttons.spacing = 10
        stack.addArrangedSubview(buttons)
        let setup = NSStackView(views: [bluetoothSetup, speechSetup]); setup.spacing = 10
        stack.addArrangedSubview(setup)
        send.target = self; send.action = #selector(sendText)
        microphone.target = self; microphone.action = #selector(toggleSpeech)
        speechSetup.target = self; speechSetup.action = #selector(configureSpeech)
        bluetoothSetup.target = self; bluetoothSetup.action = #selector(configureBluetooth)
        resume.target = self; resume.action = #selector(resumeRequest)
        restore.target = self; restore.action = #selector(restoreVersion)
        let versionsRow = NSStackView(views: [history, restore]); versionsRow.spacing = 10
        history.widthAnchor.constraint(greaterThanOrEqualToConstant: 320).isActive = true
        stack.addArrangedSubview(versionsRow)
        let scroll = NSScrollView(); scroll.hasVerticalScroller = true; scroll.borderType = .bezelBorder
        output.isEditable = false; output.font = .systemFont(ofSize: 14); output.isRichText = false
        output.autoresizingMask = [.width]; scroll.documentView = output
        scroll.translatesAutoresizingMaskIntoConstraints = false; stack.addArrangedSubview(scroll)
        scroll.widthAnchor.constraint(equalTo: stack.widthAnchor).isActive = true
        scroll.heightAnchor.constraint(greaterThanOrEqualToConstant: 240).isActive = true
        window.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps: true)
        window.makeFirstResponder(input)
        startController()
        timer = Timer.scheduledTimer(withTimeInterval: 2, repeats: true) { [weak self] _ in self?.refresh() }
        if CommandLine.arguments.contains("--request-permissions") { authorizeSpeech { _ in } }
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }
    func applicationWillTerminate(_ notification: Notification) { cancelSpeech() }

    func startController() {
        if let data = try? Data(contentsOf: URL(fileURLWithPath: config.connection)),
           let existing = try? JSONDecoder().decode(Connection.self, from: data),
           kill(existing.pid, 0) == 0 {
            connection = existing; refresh(); return
        }
        let process = Process(); process.executableURL = URL(fileURLWithPath: config.python)
        process.arguments = [config.server, "--state", config.state, "--connection", config.connection]
        var environment = ProcessInfo.processInfo.environment; environment["PATH"] = config.path
        process.environment = environment
        let log = URL(fileURLWithPath: config.connection).deletingLastPathComponent().appendingPathComponent("server.log")
        try? FileManager.default.createDirectory(at: log.deletingLastPathComponent(), withIntermediateDirectories: true)
        FileManager.default.createFile(atPath: log.path, contents: nil)
        if let handle = try? FileHandle(forWritingTo: log) { process.standardOutput = handle; process.standardError = handle }
        do { try process.run(); serverProcess = process }
        catch { stateLabel.stringValue = "Не удалось запустить управление: \(error.localizedDescription)" }
    }

    func api(_ endpoint: String, body: [String: Any]? = nil, completion: @escaping ([String: Any]?, String?) -> Void) {
        guard let connection = connection, let url = URL(string: connection.url + endpoint) else {
            completion(nil, "Сервис управления ещё запускается."); return
        }
        var call = URLRequest(url: url); call.timeoutInterval = 8
        call.setValue("Bearer " + connection.token, forHTTPHeaderField: "Authorization")
        if let body = body {
            call.httpMethod = "POST"; call.setValue("application/json", forHTTPHeaderField: "Content-Type")
            call.httpBody = try? JSONSerialization.data(withJSONObject: body)
        }
        URLSession.shared.dataTask(with: call) { data, response, error in
            let value = data.flatMap { try? JSONSerialization.jsonObject(with: $0) as? [String: Any] }
            let status = (response as? HTTPURLResponse)?.statusCode ?? 0
            DispatchQueue.main.async {
                if let error = error { completion(nil, error.localizedDescription) }
                else if status < 200 || status >= 300 { completion(nil, value?["error"] as? String ?? "Ошибка управления") }
                else { completion(value, nil) }
            }
        }.resume()
    }

    func refresh() {
        if connection == nil, let data = try? Data(contentsOf: URL(fileURLWithPath: config.connection)) {
            connection = try? JSONDecoder().decode(Connection.self, from: data)
        }
        api("/status") { [weak self] value, error in
            guard let self = self else { return }
            guard let value = value else { self.stateLabel.stringValue = error ?? "Сервис пока не отвечает"; return }
            let busy = value["busy"] as? Bool ?? false
            let pending = value["pending"] as? Bool ?? false
            let world = value["world"] as? [String: Any] ?? [:]
            self.stateLabel.stringValue = "Мир \(world["counter"] ?? "?") · " + (busy ? "выполняю запрос" : (pending ? "нужно продолжить операцию" : "готов к изменениям"))
            self.send.isEnabled = !busy && !pending && self.task == nil
            self.microphone.isEnabled = !busy && !pending && (self.task == nil || self.listening)
            self.resume.isEnabled = !busy && value["active"] is String
            self.restore.isEnabled = !busy && !pending
            let labels = ["PLANNING": "Продумываю изменение", "CHECKING-CANDIDATE": "Проверяю кандидат",
                "CHECKING-ENGINE": "Проверяю обновление движка", "DELIVERING-ENGINE": "Передаю движок",
                "CHECKING-WORLD": "Проверяю мир", "DELIVERING-WORLD": "Передаю мир", "APPLIED": "Применено",
                "PENDING": "Результат пока неизвестен", "UNSUPPORTED": "Пока не поддерживается", "FAILED": "Проверка не пройдена", "REJECTED": "Отклонено", "UNCHANGED": "Уже так"]
            let requests = value["requests"] as? [[String: Any]] ?? []
            var entries: [String] = []
            for item in requests.reversed() {
                let status = item["status"] as? String ?? ""
                let intent = item["intent"] as? String ?? ""
                let explanation = item["explanation"] as? String ?? ""
                let error = item["error"] as? String ?? ""
                var line = intent + "\n" + (labels[status] ?? status)
                if !explanation.isEmpty { line += " — " + explanation }
                if !error.isEmpty { line += "\n" + error }
                entries.append(line)
            }
            self.output.string = entries.joined(separator: "\n\n")
            if let error = value["server_error"] as? String { self.speechLabel.stringValue = error }
            let selected = self.history.indexOfSelectedItem
            let selectedID = selected >= 0 && selected < self.versions.count ? self.versions[selected]["id"] as? String : nil
            let versions = value["versions"] as? [[String: Any]] ?? []
            if versions.map({ $0["id"] as? String }) != self.versions.map({ $0["id"] as? String }) {
                self.versions = versions; self.history.removeAllItems()
                for (index, item) in versions.enumerated() {
                    self.history.addItem(withTitle: "\(index + 1). " + (item["request"] as? String ?? "Версия"))
                }
                if let selectedID = selectedID, let index = versions.firstIndex(where: { $0["id"] as? String == selectedID }) {
                    self.history.selectItem(at: index)
                } else if !versions.isEmpty { self.history.selectItem(at: versions.count - 1) }
            }
        }
    }

    func submit(_ intent: String, source: String) {
        guard !intent.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        send.isEnabled = false; microphone.isEnabled = false
        let identity = UUID().uuidString.replacingOccurrences(of: "-", with: "").lowercased()
        api("/request", body: ["id": identity, "intent": intent, "source": source]) { [weak self] _, error in
            if let error = error { self?.speechLabel.stringValue = error }
            self?.refresh()
        }
    }
    @objc func sendText() { submit(input.stringValue, source: "text") }
    @objc func resumeRequest() {
        api("/resume", body: [:]) { [weak self] _, error in if let error = error { self?.speechLabel.stringValue = error }; self?.refresh() }
    }
    @objc func restoreVersion() {
        let index = history.indexOfSelectedItem
        guard index >= 0 && index < versions.count, let version = versions[index]["id"] as? String else { return }
        api("/restore", body: ["version": version]) { [weak self] _, error in if let error = error { self?.speechLabel.stringValue = error }; self?.refresh() }
    }

    func authorizeSpeech(_ completion: @escaping (Bool) -> Void) {
        SFSpeechRecognizer.requestAuthorization { status in
            guard status == .authorized else {
                DispatchQueue.main.async { self.speechLabel.stringValue = "Разреши распознавание речи для Rabbit World в настройках конфиденциальности."; completion(false) }; return
            }
            AVCaptureDevice.requestAccess(for: .audio) { allowed in
                DispatchQueue.main.async {
                    if !allowed { self.speechLabel.stringValue = "Разреши доступ к микрофону для Rabbit World в настройках конфиденциальности." }
                    completion(allowed)
                }
            }
        }
    }
    @objc func configureBluetooth() {
        speechLabel.stringValue = "Разреши Rabbit World использовать Bluetooth для передачи на Dell. Затем нажми «Продолжить передачу»."
        bluetooth = CBCentralManager(delegate: self, queue: .main)
    }
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        switch central.state {
        case .poweredOn: speechLabel.stringValue = "Bluetooth доступен. Сохранённую операцию можно продолжить."
        case .unauthorized: speechLabel.stringValue = "Разреши Bluetooth для Rabbit World в настройках конфиденциальности macOS."
        case .poweredOff: speechLabel.stringValue = "Включи Bluetooth на Mac, затем продолжи сохранённую операцию."
        case .unsupported: speechLabel.stringValue = "Bluetooth недоступен на этом Mac."
        default: speechLabel.stringValue = "Проверяю доступ к Bluetooth…"
        }
    }
    @objc func configureSpeech() {
        speechLabel.stringValue = "macOS запросит доступ к распознаванию речи и микрофону. Этот шаг не записывает голос и не отправляет изменения."
        authorizeSpeech { [weak self] allowed in
            if allowed { self?.speechLabel.stringValue = "Голос настроен. Нажми «Говорить», произнеси просьбу и нажми «Закончить фразу». Для русского используется служба распознавания Apple, если она недоступна на Mac." }
        }
    }
    @objc func toggleSpeech() {
        if listening { finishSpeech(); return }
        authorizeSpeech { [weak self] allowed in if allowed { self?.startSpeech() } }
    }
    func startSpeech() {
        cancelSpeech(); speechGeneration += 1
        let generation = speechGeneration
        guard let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "ru-RU")), recognizer.isAvailable else {
            speechLabel.stringValue = "Русское распознавание сейчас недоступно. Можно продолжать текстом."; return
        }
        self.recognizer = recognizer
        let audio = AVAudioEngine(); let request = SFSpeechAudioBufferRecognitionRequest()
        request.shouldReportPartialResults = true
        request.requiresOnDeviceRecognition = recognizer.supportsOnDeviceRecognition
        self.request = request; engine = audio
        let node = audio.inputNode; let format = node.outputFormat(forBus: 0)
        if format.sampleRate == 0 || format.channelCount == 0 { speechLabel.stringValue = "Микрофон недоступен."; cancelSpeech(); return }
        node.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in request.append(buffer) }
        tapInstalled = true
        task = recognizer.recognitionTask(with: request) { [weak self] result, error in
            DispatchQueue.main.async {
                guard let self = self, self.speechGeneration == generation, self.submittedGeneration != generation else { return }
                if let result = result {
                    self.input.stringValue = result.bestTranscription.formattedString
                    if result.isFinal && self.submittedGeneration != generation {
                        self.submittedGeneration = generation
                        let text = result.bestTranscription.formattedString
                        self.cancelSpeech(); self.speechLabel.stringValue = "Услышал: " + text
                        self.submit(text, source: "voice"); return
                    }
                }
                if let error = error {
                    self.cancelSpeech(); self.speechLabel.stringValue = "Речь не распознана: \(error.localizedDescription). Изменения не отправлены."
                }
            }
        }
        do {
            audio.prepare(); try audio.start(); listening = true
            microphone.title = "Закончить фразу"; send.isEnabled = false
            speechLabel.stringValue = "Слушаю. После фразы нажми «Закончить фразу». " + (request.requiresOnDeviceRecognition ? "Распознавание на Mac." : "Распознавание службой Apple.")
            speechDeadline = Timer.scheduledTimer(withTimeInterval: 40, repeats: false) { [weak self] _ in self?.finishSpeech() }
        } catch { cancelSpeech(); speechLabel.stringValue = "Не удалось включить микрофон: \(error.localizedDescription)" }
    }
    func finishSpeech() {
        speechDeadline?.invalidate(); speechDeadline = nil
        engine?.stop()
        if tapInstalled { engine?.inputNode.removeTap(onBus: 0); tapInstalled = false }
        request?.endAudio(); listening = false; microphone.title = "Говорить"
        speechLabel.stringValue = "Завершаю распознавание…"
        speechDeadline = Timer.scheduledTimer(withTimeInterval: 10, repeats: false) { [weak self] _ in
            guard let self = self, self.task != nil else { return }
            self.cancelSpeech(); self.speechLabel.stringValue = "Распознавание не завершилось. Можно повторить фразу или отправить текст."
        }
    }
    func cancelSpeech() {
        speechDeadline?.invalidate(); speechDeadline = nil
        engine?.stop()
        if tapInstalled { engine?.inputNode.removeTap(onBus: 0); tapInstalled = false }
        task?.cancel(); task = nil; request = nil; engine = nil; recognizer = nil
        listening = false; microphone.title = "Говорить"
    }
}

if CommandLine.arguments.contains("--diagnostics") {
    let r = SFSpeechRecognizer(locale: Locale(identifier: "ru-RU"))
    let value: [String: Any] = ["speechAuthorization": SFSpeechRecognizer.authorizationStatus().rawValue,
        "microphoneAuthorization": AVCaptureDevice.authorizationStatus(for: .audio).rawValue,
        "russianRecognizerAvailable": r?.isAvailable ?? false, "onDeviceRecognition": r?.supportsOnDeviceRecognition ?? false]
    let data = try! JSONSerialization.data(withJSONObject: value, options: [.sortedKeys])
    print(String(data: data, encoding: .utf8)!)
} else {
    let app = NSApplication.shared
    let delegate = Application(); app.delegate = delegate; app.setActivationPolicy(.regular); app.run()
}
