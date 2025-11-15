## [Unreleased]

### Added
* new IPSet method `isIntersects(ipset)` to check if two IPSets intersect

### Changed
* expand IPSet argument type from `Sequence[str]` to `Iterable[str]` for better compatibility with type checking tools and synchronization with actual accepted types
* improve `__or__`(union) perfomance from O(k*log(n)) to O(k+n) by using a more efficient algorithm. its from 10% to 5k%(in case 10kk nets without overlapping)

### Fixed
* error if `__neq__` is called with non IPSet object


## v0.1.1 - 2025-05-08

### Fixed
* incorrect bytebuffer allocation in \_\_getstate__
