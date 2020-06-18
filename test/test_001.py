import kosis


def test_001():
    kosis.fetch_tree("age")
    kosis.fetch_tree("global")
    kosis.fetch_tree("issue")
    kosis.fetch_tree("local_org")
    kosis.fetch_tree("local_theme")
    kosis.fetch_tree("local_topic")
    kosis.fetch_tree("org")
    kosis.fetch_tree("topic")
    kosis.fetch_tree("yearbook")
