Title: SwiftUI NavigationStack
Source: Apple Developer Documentation, SwiftUI
NavigationStack manages a stack of views and a navigation path. NavigationLink pushes a view onto the stack, and navigationDestination(for:) maps a value type to the destination view for that value. Keep the path as state in the owning view so the stack can be driven programmatically and reset, instead of relying only on links created deep inside child views.
