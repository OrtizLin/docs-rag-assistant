Title: SwiftData @Model and @Query
Source: Apple Developer Documentation, SwiftData
In SwiftData, a model is a class marked @Model, and its stored properties become the persisted fields. A view reads models with @Query, which keeps the list in sync as the underlying data changes, and writes go through a ModelContext, typically from the view environment. Keep the model class focused on persisted state, and put derived or presentation logic in the view or a separate type.
