## OOP Concepts Demonstrated (Weeks 1 - 5)

| Week | Concept | How It Is Implemented in the Project |
| :--- | :--- | :--- |
| **Week 1** | **Classes & Objects** | Every entity in the supply chain (ProductBatch, QualityInspector) is a class. All classes include comprehensive docstrings and implement `__str__` and `__repr__` for clear string formatting. |
| **Week 2** | **Encapsulation** | `LedgerEntry` is strictly immutable. Fields like `_current_hash` are private and only accessible via `@property` getters (no setters). `ProductBatch` uses a `@batch_id.setter` to validate the `NG-YYYY-XXXXXXXX` regex pattern. |
| **Week 3** | **Inheritance & ABC** | `SupplyChainActor` and `QualityStandard` inherit from Python's `ABC` (Abstract Base Class) module. They define `@abstractmethod` functions. Concrete classes like `FarmProducer` and `NafdacStandard` inherit from these and implement the required logic. |
| **Week 4** | **Polymorphism & Duck Typing** | Polymorphism is demonstrated via magic methods: `LedgerEntry` uses `__eq__`, `__lt__`, and `__hash__`. `SupplyChain` uses `__len__`, `__contains__`, and `__iter__`. Duck Typing is proven in `audit_ledger_objects()`, which processes any object with `previous_hash` and `current_hash` attributes. |
| **Week 5** | **UML Modeling** | System designed with structural relationships: **Composition** (`SupplyChain` controls `LedgerEntry`), **Aggregation** (`SupplyChainActor` holds a temporary reference to `ProductBatch`), and **Realization** (Actors realize the `SupplyChainActor` interface). |
