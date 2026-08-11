from nsdigest.sources.rss import RSSSource

# --- Preprint servers ---

ArxivNeurons = RSSSource(
    name="arXiv q-bio.NC",
    feed_url="http://export.arxiv.org/rss/q-bio.NC",
)

ArxivSignalProcessing = RSSSource(
    name="arXiv eess.SP",
    feed_url="http://export.arxiv.org/rss/eess.SP",
)

ArxivNeuralComputing = RSSSource(
    name="arXiv cs.NE",
    feed_url="http://export.arxiv.org/rss/cs.NE",
)

ArxivMachineLearning = RSSSource(
    name="arXiv cs.LG",
    feed_url="http://export.arxiv.org/rss/cs.LG",
)

BioRxivNeuroscience = RSSSource(
    name="bioRxiv Neuroscience",
    feed_url="http://connect.biorxiv.org/biorxiv_xml.php?subject=neuroscience",
)

# --- Journals ---

NatureNeuroscience = RSSSource(
    name="Nature Neuroscience",
    feed_url="https://www.nature.com/neuro.rss",
)

JournalOfNeuroscience = RSSSource(
    name="Journal of Neuroscience",
    feed_url="https://www.jneurosci.org/rss/current.xml",
)

eLifeNeuroscience = RSSSource(
    name="eLife Neuroscience",
    feed_url="https://elifesciences.org/rss/subject/neuroscience.xml",
)

PLOSComputationalBiology = RSSSource(
    name="PLOS Computational Biology",
    feed_url="https://journals.plos.org/ploscompbiol/feed/atom",
)

NeuroImage = RSSSource(
    name="NeuroImage",
    feed_url="https://rss.sciencedirect.com/publication/science/10538119",
)

FrontiersInNeuroscience = RSSSource(
    name="Frontiers in Neuroscience",
    feed_url="https://www.frontiersin.org/journals/neuroscience/rss",
)

FrontiersInHumanNeuroscience = RSSSource(
    name="Frontiers in Human Neuroscience",
    feed_url="https://www.frontiersin.org/journals/human-neuroscience/rss",
)

eNeuro = RSSSource(
    name="eNeuro",
    feed_url="https://www.eneuro.org/rss/current.xml",
)

NatureCommunicationsNeuroscience = RSSSource(
    name="Nature Communications (Neuroscience)",
    feed_url="https://www.nature.com/subjects/neuroscience/ncomms.rss",
)

# --- Neurotechnology / BCI ---

JournalOfNeuralEngineering = RSSSource(
    name="Journal of Neural Engineering",
    feed_url="https://iopscience.iop.org/journal/rss/1741-2552",
)


SOURCES = [
    # Preprints
    ArxivNeurons,
    ArxivSignalProcessing,
    ArxivNeuralComputing,
    ArxivMachineLearning,
    BioRxivNeuroscience,
    # Journals
    NatureNeuroscience,
    JournalOfNeuroscience,
    eLifeNeuroscience,
    PLOSComputationalBiology,
    NeuroImage,
    FrontiersInNeuroscience,
    FrontiersInHumanNeuroscience,
    eNeuro,
    NatureCommunicationsNeuroscience,
    # Neurotech / BCI
    JournalOfNeuralEngineering,
]
