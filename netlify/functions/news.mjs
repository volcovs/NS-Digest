import { Dropbox } from "dropbox";

const dbx = new Dropbox({
    clientId: process.env.DROPBOX_APP_KEY,
    clientSecret: process.env.DROPBOX_APP_SECRET,
    refreshToken: process.env.DROPBOX_REFRESH_TOKEN,
});


function normalizePath(path) {
    path = path.replaceAll("\\", "/").trim();

    if (!path) {
        throw new Error("Dropbox path cannot be empty");
    }

    if (!path.startsWith("/")) {
        path = "/" + path;
    }

    while (path.includes("//")) {
        path = path.replaceAll("//", "/");
    }

    if (path.length > 1) {
        path = path.replace(/\/+$/, "");
    }

    return path;
}


async function readText(path) {
    const response = await dbx.filesDownload({
        path: normalizePath(path),
    });

    const result = response.result;

    if (result.fileBlob) {
        return await result.fileBlob.text();
    }

    if (result.fileBinary) {
        return Buffer
            .from(result.fileBinary)
            .toString("utf-8");
    }

    if (result.fileBuffer) {
        return Buffer
            .from(result.fileBuffer)
            .toString("utf-8");
    }

    throw new Error(
        `Unable to read Dropbox file. ` +
        `Available fields: ${Object.keys(result).join(", ")}`
    );
}


async function listArticleFiles(path) {
    const entries = [];

    let response = await dbx.filesListFolder({
        path,
    });

    entries.push(...response.result.entries);

    while (response.result.has_more) {
        response = await dbx.filesListFolderContinue({
            cursor: response.result.cursor,
        });

        entries.push(...response.result.entries);
    }

    return entries.filter(
        entry =>
            entry[".tag"] === "file" &&
            entry.name.endsWith(".jsonl")
    );
}


function parseDateFromFilename(filename) {
    const match =
        filename.match(/^(\d{4}-\d{2}-\d{2})\.jsonl$/);

    if (!match) {
        return null;
    }

    return new Date(
        `${match[1]}T00:00:00Z`
    );
}


function parseQuery(request) {
    const url = new URL(request.url);

    let limit =
        Number.parseInt(
            url.searchParams.get("limit") || "50",
            10
        );

    let days =
        Number.parseInt(
            url.searchParams.get("days") || "7",
            10
        );

    if (!Number.isFinite(limit)) {
        limit = 50;
    }

    if (!Number.isFinite(days)) {
        days = 7;
    }

    limit = Math.min(
        Math.max(limit, 1),
        200
    );

    days = Math.min(
        Math.max(days, 1),
        90
    );

    return {
        limit,
        days,
    };
}


function parseArticles(content) {
    const articles = [];

    for (const line of content.split("\n")) {
        if (!line.trim()) {
            continue;
        }

        try {
            articles.push(
                JSON.parse(line)
            );
        } catch (error) {
            console.error(
                "Invalid JSONL line:",
                error
            );
        }
    }

    return articles;
}


function articleDate(article) {
    return new Date(
        article.published_at ||
        article.fetched_at
    );
}


export default async (request) => {
    try {
        const {
            limit,
            days,
        } = parseQuery(request);

        const root =
            process.env.DROPBOX_ROOT?.trim() || "";

        const articlesPath = root
            ? `${normalizePath(root)}/articles`
            : "/articles";

        const files =
            await listArticleFiles(
                normalizePath(articlesPath)
            );

        const cutoff =
            new Date();

        cutoff.setUTCDate(
            cutoff.getUTCDate() - days
        );

        /*
         * Only download JSONL files whose date
         * is recent enough.
         */
        const relevantFiles =
            files.filter(file => {
                const date =
                    parseDateFromFilename(
                        file.name
                    );

                if (!date) {
                    return true;
                }

                return date >= cutoff;
            });

        const articles = [];

        for (const file of relevantFiles) {
            const content =
                await readText(
                    file.path_lower
                );

            articles.push(
                ...parseArticles(content)
            );
        }

        /*
         * Remove duplicate IDs.
         */
        const unique =
            new Map();

        for (const article of articles) {
            if (article.id) {
                unique.set(
                    article.id,
                    article
                );
            }
        }

        const result =
            Array.from(
                unique.values()
            );

        /*
         * Newest first.
         */
        result.sort(
            (a, b) =>
                articleDate(b) -
                articleDate(a)
        );

        /*
         * Return only the requested number.
         */
        const limited =
            result.slice(0, limit);

        return new Response(
            JSON.stringify({
                articles: limited,
                count: limited.length,
                days,
                limit,
            }),
            {
                status: 200,
                headers: {
                    "Content-Type":
                        "application/json",

                    "Cache-Control":
                        "public, max-age=300",
                },
            }
        );

    } catch (error) {
        console.error(
            "Dropbox/API error:",
            error
        );

        return new Response(
            JSON.stringify({
                error:
                    "Failed to retrieve articles",
            }),
            {
                status: 500,
                headers: {
                    "Content-Type":
                        "application/json",
                },
            }
        );
    }
};
