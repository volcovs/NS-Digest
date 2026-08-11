from nsdigest.processing.classify import classify


def test_classifies_bci():
    assert (
        classify(
            "Brain-computer interface for neural decoding",
            "A BCI that decodes motor intent.",
        )
        == "bci"
    )


def test_classifies_machine_learning():
    assert (
        classify(
            "A transformer model for classification",
            "Deep learning with feature extraction.",
        )
        == "machine_learning"
    )


def test_classifies_clinical():
    assert (
        classify(
            "Biomarkers of Alzheimer's disease in patients",
            None,
        )
        == "clinical"
    )


def test_unmatched_is_other():
    assert classify("Dendritic spine turnover in zebrafish", None) == "other"
