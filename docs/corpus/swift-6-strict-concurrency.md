Title: Swift 6 strict concurrency and Sendable
Source: Apple Developer Documentation, Swift
Swift 6 language mode turns on strict concurrency checking: the compiler reports data races at build time instead of letting them fail at runtime. Values shared across tasks must be Sendable, meaning they can be passed safely between concurrency domains. Actor-isolated state is only touched from inside the actor, and global state must be protected or made Sendable. Turning the mode on for one target at a time keeps the migration manageable.
