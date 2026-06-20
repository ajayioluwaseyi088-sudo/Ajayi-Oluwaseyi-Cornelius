import pytest
from datetime import date
from your_main_file import (  # Replace with your actual file name
    ProductBatch, FarmProducer, Aggregator, Processor, Distributor, 
    LedgerEntry, SupplyChain, NafdacStandard, QualityInspector, 
    LedgerTamperingError, InvalidCustodyTransferError, audit_ledger_objects
)

# --- WEEK 1 & 2: CLASSES, OBJECTS & ENCAPSULATION ---

def test_01_batch_creation_success():
    batch = ProductBatch("NG-2026-12345678", "Rice", "grains", "Farm A", date.today(), 1000)
    assert batch.batch_id == "NG-2026-12345678"
    assert batch.current_weight_kg == 1000

def test_02_batch_id_regex_validation():
    with pytest.raises(ValueError, match="strictly match the format"):
        ProductBatch("BAD-ID-99", "Rice", "grains", "Farm A", date.today(), 1000)

def test_03_batch_negative_initial_weight():
    with pytest.raises(ValueError, match="Weight must be greater than 0"):
        ProductBatch("NG-2026-12345678", "Rice", "grains", "Farm A", date.today(), -50)

def test_04_batch_weight_increase_blocked():
    batch = ProductBatch("NG-2026-12345678", "Rice", "grains", "Farm A", date.today(), 1000)
    with pytest.raises(ValueError, match="cannot exceed initial"):
        batch.current_weight_kg = 1500

def test_05_ledger_entry_immutability():
    farm = FarmProducer("A1", "Farm", "Loc")
    agg = Aggregator("A2", "Agg", "Loc")
    entry = LedgerEntry("NG-2026-12345678", farm, agg, 500, "0"*64)
    with pytest.raises(AttributeError):
        entry.weight_kg = 600  # Trying to hack the weight should fail

# --- WEEK 3: INHERITANCE & ACTOR LOGIC ---

def test_06_actor_instantiation_types():
    farm = FarmProducer("A1", "Farm", "Loc")
    assert farm.actor_type == "FarmProducer"

def test_07_custody_transfer_success():
    farm = FarmProducer("A1", "Farm", "Loc")
    agg = Aggregator("A2", "Agg", "Loc")
    batch = ProductBatch("NG-2026-11111111", "Corn", "grains", "Farm A", date.today(), 100)
    batch.current_custodian = farm
    entry = farm.transfer_custody(batch, agg, 90)
    assert batch.current_custodian == agg
    assert batch.current_weight_kg == 90
    assert entry.from_actor == farm

def test_08_custody_transfer_unauthorized():
    farm = FarmProducer("A1", "Farm", "Loc")
    thief = Aggregator("A2", "Thief", "Loc")
    batch = ProductBatch("NG-2026-11111111", "Corn", "grains", "Farm A", date.today(), 100)
    batch.current_custodian = farm
    with pytest.raises(InvalidCustodyTransferError):
        thief.transfer_custody(batch, farm, 100) # Thief doesn't own it

def test_09_processor_split_batch():
    proc = Processor("P1", "Proc", "Loc")
    batch = ProductBatch("NG-2026-22222222", "Tomatoes", "perishables", "Farm", date.today(), 100)
    batch.current_custodian = proc
    subs = proc.split_batch(batch, [("NG-2026-22222223", 40), ("NG-2026-22222224", 40)])
    assert len(subs) == 2
    assert batch.current_weight_kg < 1  # Original batch is exhausted

def test_10_processor_split_exceeds_weight():
    proc = Processor("P1", "Proc", "Loc")
    batch = ProductBatch("NG-2026-22222222", "Tomatoes", "perishables", "Farm", date.today(), 100)
    with pytest.raises(ValueError):
        proc.split_batch(batch, [("NG-2026-33333333", 150)])

# --- WEEK 4: POLYMORPHISM, MAGIC METHODS & DUCK TYPING ---

def test_11_ledger_eq_magic_method():
    farm = FarmProducer("A1", "Farm", "Loc")
    agg = Aggregator("A2", "Agg", "Loc")
    entry1 = LedgerEntry("NG-2026-11111111", farm, agg, 500, "0"*64)
    assert entry1 == entry1

def test_12_supply_chain_len():
    chain = SupplyChain("NG-2026-00000000")
    assert len(chain) == 0

def test_13_supply_chain_contains():
    chain = SupplyChain("NG-2026-00000000")
    assert "NG-2026-00000000" in chain

def test_14_supply_chain_append_mismatch():
    chain = SupplyChain("NG-2026-00000000")
    farm = FarmProducer("A1", "Farm", "Loc")
    entry = LedgerEntry("NG-2026-99999999", farm, farm, 10, "0")
    with pytest.raises(ValueError, match="mismatch"):
        chain.append_entry(entry)

def test_15_duck_typing_audit_success():
    class FakeDuck:
        previous_hash = "abc"
        current_hash = "def"
    assert audit_ledger_objects([FakeDuck()]) is True

def test_16_duck_typing_audit_fail():
    class BadDuck:
        wrong_attr = "abc"
    assert audit_ledger_objects([BadDuck()]) is False

# --- SYSTEM INTEGRITY & QUALITY CONTROL ---

def test_17_certificate_issuance():
    nafdac = NafdacStandard()
    inspector = QualityInspector("I1", "Insp", [nafdac])
    batch = ProductBatch("NG-2026-12345678", "Rice", "grains", "Farm", date.today(), 100)
    cert = inspector.issue_certificate(batch, nafdac)
    assert cert.is_valid is True
    assert cert.grade == "A"

def test_18_certificate_unauthorized_inspector():
    inspector = QualityInspector("I1", "Insp", []) # No accreditations
    batch = ProductBatch("NG-2026-12345678", "Rice", "grains", "Farm", date.today(), 100)
    with pytest.raises(PermissionError):
        inspector.issue_certificate(batch, NafdacStandard())

def test_19_chain_integrity_pass():
    farm = FarmProducer("A1", "Farm", "Loc")
    agg = Aggregator("A2", "Agg", "Loc")
    batch = ProductBatch("NG-2026-11111111", "Rice", "grains", "Farm", date.today(), 100)
    batch.current_custodian = farm
    entry = farm.transfer_custody(batch, agg, 100)
    
    chain = SupplyChain("NG-2026-11111111")
    chain.append_entry(entry)
    assert chain.verify_integrity() is True

def test_20_chain_integrity_tamper_detected():
    farm = FarmProducer("A1", "Farm", "Loc")
    agg = Aggregator("A2", "Agg", "Loc")
    batch = ProductBatch("NG-2026-11111111", "Rice", "grains", "Farm", date.today(), 100)
    batch.current_custodian = farm
    entry = farm.transfer_custody(batch, agg, 100)
    
    chain = SupplyChain("NG-2026-11111111")
    chain.append_entry(entry)
    
    # Hack the ledger
    chain.entries[0]._weight_kg = 50 
    
    with pytest.raises(LedgerTamperingError):
        chain.verify_integrity()
