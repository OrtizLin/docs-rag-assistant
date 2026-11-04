Title: App Transport Security (ATS)
Source: Apple Developer Documentation, App Transport Security
App Transport Security requires secure network connections by default, which in practice means HTTPS with modern TLS. Exceptions are configured in Info.plist under NSAppTransportSecurity, and should be scoped to a specific domain that genuinely cannot use HTTPS yet. Do not allow arbitrary loads globally in a shipping app: it disables the protection for every connection, not just the one that needed it.
