Title: Xcode code signing and provisioning
Source: Apple Developer Documentation, Xcode
Code signing proves an app comes from a known team and has not been changed since it was built. Xcode needs a signing certificate for the team and a provisioning profile that lists the app identifier and the devices or distribution method allowed. Automatic signing lets Xcode create and renew these for you; manual signing means you choose the certificate and profile yourself. A signing failure usually means the certificate, the profile, or the app identifier does not match.
