import { Resend } from "resend";

const resend = new Resend(
    process.env.RESEND_API_KEY
);


function escapeHtml(value) {
    const text = String(value ?? "");

    return text
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
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
        "en",
        {
            dateStyle: "medium",
            timeStyle: "short",
            timeZone: "UTC",
        }
    ).format(date);
}


function createDigestHtml(articles) {
    const important =
        [...articles]
            .sort(
                (a, b) =>
                    (b.importance_score ?? 0) -
                    (a.importance_score ?? 0)
            )
            .slice(0, 10);

    const articleHtml =
        important
            .map(article => `
                <article
                    style="
                        margin-bottom: 28px;
                        padding-bottom: 20px;
                        border-bottom: 1px solid #e5e7eb;
                    "
                >
                    <div
                        style="
                            color: #6b7280;
                            font-size: 14px;
                            margin-bottom: 6px;
                        "
                    >
                        ${escapeHtml(article.source)}
                        ·
                        ${escapeHtml(
                            formatDate(
                                article.published_at ||
                                article.fetched_at
                            )
                        )}
                        ·
                        Score ${Math.round(
                            article.importance_score ?? 0
                        )}
                    </div>

                    <h2
                        style="
                            margin: 0 0 8px;
                            font-size: 20px;
                        "
                    >
                        <a
                            href="${escapeHtml(article.url)}"
                            style="
                                color: #111827;
                                text-decoration: none;
                            "
                        >
                            ${escapeHtml(article.title)}
                        </a>
                    </h2>

                    ${
                        article.summary
                            ? `
                                <p
                                    style="
                                        color: #4b5563;
                                        line-height: 1.6;
                                    "
                                >
                                    ${escapeHtml(
                                        article.summary
                                    )}
                                </p>
                            `
                            : ""
                    }

                    ${
                        article.keywords?.length
                            ? `
                                <p style="margin: 6px 0 0;">
                                    ${article.keywords
                                        .map(
                                            keyword =>
                                                `<span style="
                                                    display: inline-block;
                                                    background: #eef2ff;
                                                    color: #3730a3;
                                                    border-radius: 4px;
                                                    padding: 2px 8px;
                                                    margin: 0 4px 4px 0;
                                                    font-size: 12px;
                                                ">${escapeHtml(keyword)}</span>`
                                        )
                                        .join("")}
                                </p>
                            `
                            : ""
                    }

                    ${
                        article.doi
                            ? `
                                <p style="
                                    margin: 6px 0 0;
                                    font-size: 13px;
                                    color: #6b7280;
                                ">
                                    DOI:
                                    <a
                                        href="https://doi.org/${escapeHtml(article.doi)}"
                                        style="color: #4338ca;"
                                    >${escapeHtml(article.doi)}</a>
                                </p>
                            `
                            : ""
                    }
                </article>
            `)
            .join("");

    return `
        <!DOCTYPE html>

        <html>
        <body
            style="
                margin: 0;
                padding: 0;
                background: #f5f7fa;
                font-family:
                    Arial,
                    Helvetica,
                    sans-serif;
            "
        >
            <div
                style="
                    max-width: 700px;
                    margin: 0 auto;
                    padding: 40px 20px;
                "
            >
                <div
                    style="
                        background: #1e1b4b;
                        color: white;
                        padding: 28px;
                        border-radius: 10px 10px 0 0;
                    "
                >
                    <h1
                        style="
                            margin: 0;
                            font-size: 28px;
                        "
                    >
                        NS-Digest
                    </h1>

                    <p
                        style="
                            margin: 8px 0 0;
                            color: #c7d2fe;
                        "
                    >
                        Your weekly neuroscience literature digest
                    </p>
                </div>

                <div
                    style="
                        background: white;
                        padding: 28px;
                    "
                >
                    <p
                        style="
                            color: #4b5563;
                            line-height: 1.6;
                        "
                    >
                        Here are the most important neuroscience
                        papers and preprints from the past week.
                    </p>

                    ${articleHtml}

                    <p
                        style="
                            margin-top: 30px;
                            color: #9ca3af;
                            font-size: 13px;
                        "
                    >
                        Generated automatically by NS-Digest.
                    </p>
                </div>
            </div>
        </body>
        </html>
    `;
}

export default async (request) => {
    if (request.method !== "POST") {
        return new Response(
            JSON.stringify({
                error: "Method Not Allowed",
            }),
            {
                status: 405,
                headers: {
                    "Content-Type":
                        "application/json",
                },
            }
        );
    }

    try {
        const recipient =
            process.env.DIGEST_RECIPIENT;

        console.log("Sending digest to:", recipient);

        if (!recipient) {
            throw new Error(
                "DIGEST_RECIPIENT is not configured"
            );
        }

        /*
         * For the first version we reuse our own
         * articles API.
         */
        const siteUrl =
            process.env.URL ||
            "http://localhost:8888";

        const response =
            await fetch(
                `${siteUrl}/api/news?days=7&limit=100`
            );

        if (!response.ok) {
            throw new Error(
                `Articles API returned ${response.status}`
            );
        }

        const data =
            await response.json();

        const articles =
            data.articles || [];

        if (articles.length === 0) {
            return new Response(
                JSON.stringify({
                    message:
                        "No articles available for digest",
                }),
                {
                    status: 200,
                    headers: {
                        "Content-Type":
                            "application/json",
                    },
                }
            );
        }

        const html =
            createDigestHtml(articles);

        const { data: emailData, error } =
            await resend.emails.send({
                from:
                    process.env.DIGEST_FROM ||
                    "NS-Digest <onboarding@resend.dev>",

                to: [recipient],

                subject:
                    "NS-Digest — Weekly Neuroscience Digest",

                html,
            });

        if (error) {
            console.error(
                "Resend error:",
                error
            );

            return new Response(
                JSON.stringify({
                    error:
                        "Failed to send digest",
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

        return new Response(
            JSON.stringify({
                success: true,
                email_id: emailData?.id,
                articles: articles.length,
            }),
            {
                status: 200,
                headers: {
                    "Content-Type":
                        "application/json",
                },
            }
        );

    } catch (error) {
        console.error(
            "Digest error:",
            error
        );

        return new Response(
            JSON.stringify({
                error:
                    "Failed to generate digest",
                message:
                    error?.message ||
                    String(error),
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
