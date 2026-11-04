Title: Swift concurrency: async/await and Task cancellation
Source: Apple Developer Documentation, Swift concurrency
async functions suspend instead of blocking a thread, and await marks the suspension point. A Task can be cancelled, but cancellation is cooperative: the task must check Task.isCancelled or call try Task.checkCancellation(), which throws CancellationError. UI updates must happen on the main actor, so mark UI-facing code @MainActor or hop back to the main actor before touching the interface.
