Title: SwiftUI @State and @Binding
Source: Apple Developer Documentation, SwiftUI
@State holds private, mutable state owned by one view. Changing it re-renders that view. @Binding does not own the value: a child view receives a binding to state owned by a parent, so the child can read and write it without owning it. Use @State in the view that owns the data, pass a binding down with a dollar sign, and keep the source of truth in one place.
