## [Unreleased]

### Added
* new IPSet method `isIntersects(ipset)` to check if two IPSets intersect
* python 3.14 support

### Changed
* expand IPSet argument type from `Sequence[str]` to `Iterable[str]` for better compatibility with type checking tools and synchronization with actual accepted types
* improve `__or__`(union) perfomance from O(k*log(n)) to O(k+n) by using a more efficient algorithm. its from 10% to 5k%(in case 10kk nets without overlapping)
* improve `__sub__`(subtract) perfomance from O(k*log(n)) to O(k+n) by using a more efficient algorithm. its from 10% to 5k%(in case 10kk nets without overlapping). Performance has also been improved for the `__xor__` operation

### Fixed
* error if `__neq__` is called with non IPSet object
* inheritance. the object returned by the mutable operations was the original Ctype

## v0.1.1 - 2025-05-08

### Fixed
* incorrect bytebuffer allocation in `__getstate__`
