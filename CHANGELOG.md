## [Unreleased]

### Added
* new IPSet method `isIntersects(ipset)` to check if two IPSets intersect

### Updates
* expand IPSet argument type from `Sequence[str]` to `Iterable[str]` for better compatibility with type checking tools and synchronization with actual accepted types
* Fix: error if `__neq__` is called with non IPSet object


## v0.1.1 - 2025-05-08

### Updates
* Fix:  incorrect bytebuffer allocation in \_\_getstate__
