from shared.id_generator.id_generator import IdGenerator


def test_id_generator_different_seed():
    """
    Test the IdGenerator class with different seeds.
    """
    id_generator = IdGenerator()

    id1 = id_generator.generate_id("test_seed_1")
    id2 = id_generator.generate_id("test_seed_2")

    assert id1 != id2


def test_id_generator_generate_id(snapshot):
    """
    Test the IdGenerator class.
    """
    id_generator = IdGenerator()

    id_generated = id_generator.generate_id("test_seed")

    assert id_generated == snapshot


def test_id_generator_generate_random_id():
    """
    Test the IdGenerator class for generating random IDs.
    """
    id_generator = IdGenerator()

    random_id_1 = id_generator.generate_random_id()

    random_id_2 = id_generator.generate_random_id()

    assert random_id_1 != random_id_2
