from data_agent.ingestion.id.id_generator import IdGenerator


def test_id_generator_different_seed():
    """
    Test the IdGenerator class with different seeds.
    """
    id_generator = IdGenerator()

    id1 = id_generator.generate_id("test_seed_1")
    id2 = id_generator.generate_id("test_seed_2")

    assert id1 != id2


def test_id_generator(snapshot):
    """
    Test the IdGenerator class.
    """
    id_generator = IdGenerator()

    id_generated = id_generator.generate_id("test_seed")

    assert id_generated == snapshot
