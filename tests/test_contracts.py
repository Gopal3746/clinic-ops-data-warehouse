from clinic_ops.contracts import LANDING_TABLES, SOURCE_ENTITIES


def test_every_source_entity_has_landing_table():
    pairs = {(source, entity) for source, entities in SOURCE_ENTITIES.items() for entity in entities}
    assert pairs == set(LANDING_TABLES)
