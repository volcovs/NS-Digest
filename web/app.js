const articlesContainer =
    document.getElementById("articles");

const loadingElement =
    document.getElementById("loading");

const errorElement =
    document.getElementById("error");

const countElement =
    document.getElementById("article-count");

const categoryFilter =
    document.getElementById("category-filter");

const refreshButton =
    document.getElementById("refresh-button");


let articles = [];

function articleDate(article) {
    return new Date(
        article.published_at ||
        article.fetched_at
    );
}

function createSectionHeading(title) {
    const heading =
        document.createElement("h2");

    heading.className =
        "feed-section-heading";

    heading.textContent = title;

    return heading;
}

async function loadNews() {
    showLoading();

    try {
        const response = await fetch("/api/news");

        if (!response.ok) {
            throw new Error(
                `API returned ${response.status}`
            );
        }

        const data = await response.json();

        articles = data.articles || [];

        renderArticles();

    } catch (error) {
        console.error(error);

        showError(
            "Unable to load neuroscience papers."
        );
    } finally {
        loadingElement.classList.add("hidden");
    }
}

function formatCategory(category) {
    if (!category) {
        return "Other";
    }

    return category
        .replaceAll("_", " ")
        .replace(
            /\b\w/g,
            character => character.toUpperCase()
        );
}


function formatDate(value) {
    if (!value) {
        return "Unknown date";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "Unknown date";
    }

    return new Intl.DateTimeFormat(
        undefined,
        {
            dateStyle: "medium",
            timeStyle: "short",
        }
    ).format(date);
}

function escapeHtml(value) {
    const div =
        document.createElement("div");

    div.textContent =
        String(value ?? "");

    return div.innerHTML;
}

function escapeAttribute(value) {
    return escapeHtml(value)
        .replaceAll('"', "&quot;");
}

function createArticleCard(article) {
    const card =
        document.createElement("article");

    card.className = "article-card";

    const score =
        Math.round(article.importance_score ?? 0);

    const category =
        formatCategory(article.category);

    const date =
        formatDate(
            article.published_at ||
            article.fetched_at
        );

    const keywords =
        article.keywords || [];

    card.innerHTML = `
        <div class="article-header">
            <span class="score">
                ${score}
            </span>

            <div class="article-meta">
                <span class="category">
                    ${escapeHtml(category)}
                </span>

                <span>
                    ${escapeHtml(article.source)}
                </span>

                <span>
                    ${escapeHtml(date)}
                </span>
            </div>
        </div>

        <h3>
            <a
                href="${escapeAttribute(article.url)}"
                target="_blank"
                rel="noopener noreferrer"
            >
                ${escapeHtml(article.title)}
            </a>
        </h3>

        ${
            article.summary
                ? `
                    <p class="summary">
                        ${escapeHtml(article.summary)}
                    </p>
                  `
                : ""
        }

        ${
            keywords.length
                ? `
                    <div class="keywords">
                        ${keywords.map(
                            keyword => `
                                <span class="keyword">
                                    ${escapeHtml(keyword)}
                                </span>
                            `
                        ).join("")}
                    </div>
                  `
                : ""
        }

        ${
            article.doi
                ? `
                    <p class="doi">
                        DOI:
                        <a
                            href="https://doi.org/${escapeAttribute(article.doi)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >${escapeHtml(article.doi)}</a>
                    </p>
                  `
                : ""
        }
    `;

    return card;
}

function renderArticles() {
    const selectedCategory =
        categoryFilter.value;

    let filtered = articles;

    if (selectedCategory !== "all") {
        filtered = articles.filter(
            article =>
                article.category === selectedCategory
        );
    }

    const important =
        [...filtered]
            .filter(
                article =>
                    (article.importance_score ?? 0) >= 60
            )
            .sort(
                (a, b) =>
                    (b.importance_score ?? 0) -
                    (a.importance_score ?? 0)
            )
            .slice(0, 10);

    const importantIds =
        new Set(
            important.map(
                article => article.id
            )
        );

    const latest =
        [...filtered]
            .filter(
                article =>
                    !importantIds.has(
                        article.id
                    )
            )
            .sort(
                (a, b) =>
                    articleDate(b) -
                    articleDate(a)
            );

    countElement.textContent =
        `${filtered.length} papers`;

    articlesContainer.innerHTML = "";

    if (filtered.length === 0) {
        articlesContainer.innerHTML = `
            <div class="empty">
                No papers found.
            </div>
        `;

        return;
    }

    if (important.length > 0) {
        articlesContainer.appendChild(
            createSectionHeading(
                "Important"
            )
        );

        for (const article of important) {
            articlesContainer.appendChild(
                createArticleCard(article)
            );
        }
    }

    articlesContainer.appendChild(
        createSectionHeading(
            "Latest"
        )
    );

    for (const article of latest) {
        articlesContainer.appendChild(
            createArticleCard(article)
        );
    }
}

function showLoading() {
    loadingElement.classList.remove(
        "hidden"
    );

    errorElement.classList.add(
        "hidden"
    );
}


function showError(message) {
    loadingElement.classList.add(
        "hidden"
    );

    errorElement.textContent =
        message;

    errorElement.classList.remove(
        "hidden"
    );
}


categoryFilter.addEventListener(
    "change",
    renderArticles
);


refreshButton.addEventListener(
    "click",
    loadNews
);


loadNews();
