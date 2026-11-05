Title: Debugging performance with Xcode Instruments
Source: Apple Developer Documentation, Xcode
Instruments records what an app does while it runs, so a slowdown can be traced to a cause instead of guessed. Time Profiler shows which functions take the most CPU time; Leaks finds objects that are never freed; Allocations tracks memory growth over time. Run the app on a real device, reproduce the slow path, stop the recording, and read the heaviest stack first. Fix the heaviest item, then measure again.
