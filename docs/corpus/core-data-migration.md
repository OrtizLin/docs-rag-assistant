Title: Core Data lightweight migration
Source: Apple Developer Documentation, Core Data
When the data model changes, an old store must be migrated to the new model. A lightweight migration handles simple changes automatically: adding an attribute, renaming with a renaming identifier, or changing an optional flag. Create a new model version, set it as current, and let the persistent container migrate the store when it loads. Heavier changes, such as splitting an entity, need a mapping model and a manual migration.
