Title: Xcode error: No such module
Source: Apple Developer Documentation, Xcode
No such module usually means the module cannot be found for the current target, not that the code is wrong. Check, in order: the file or framework is a member of the target being built, the import name matches the product or module name, framework search paths include the framework location, and the scheme builds the right target. If the setup looks right, clean the build folder and delete derived data, then rebuild, because a stale build cache is a common cause.
