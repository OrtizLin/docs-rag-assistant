Title: SwiftUI List performance for large data
Source: Apple Developer Documentation, SwiftUI
A List renders its rows lazily, so only the rows on screen are built, but a heavy row body still costs time when it scrolls into view. Give each row a stable identity with Identifiable, keep the row view small, and move expensive work out of the body. For very long data sets, prefer LazyVStack or LazyVGrid inside a ScrollView when the built-in List behaviour is not needed, and avoid recomputing the whole list for one small change.
