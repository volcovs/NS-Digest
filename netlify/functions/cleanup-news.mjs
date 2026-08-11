import { Dropbox } from "dropbox";

const dbx = new Dropbox({
    clientId: process.env.DROPBOX_APP_KEY,
    clientSecret: process.env.DROPBOX_APP_SECRET,
    refreshToken: process.env.DROPBOX_REFRESH_TOKEN,
});

const RETENTION_DAYS = 90;


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


function articlesPath() {
    const root = process.env.DROPBOX_ROOT?.trim() || "";

    return root
        ? normalizePath(`${normalizePath(root)}/articles`)
        : "/articles";
}


function jsonResponse(body, status = 200) {
    return new Response(
        JSON.stringify(body),
        {
            status,
            headers: {
                "Content-Type": "application/json",
            },
        }
    );
}


function getCutoffDate() {
    const cutoff = new Date();

    cutoff.setUTCDate(
        cutoff.getUTCDate() - RETENTION_DAYS
    );

    return cutoff;
}


function getFileDate(name) {
    /*
     * Expected filename:
     *
     * 2026-08-10.jsonl
     */

    const match =
        name.match(
            /^(\d{4}-\d{2}-\d{2})\.jsonl$/
        );

    if (!match) {
        return null;
    }

    const date =
        new Date(
            `${match[1]}T00:00:00Z`
        );

    if (Number.isNaN(date.getTime())) {
        return null;
    }

    return date;
}


async function listArticleFiles() {
    const entries = [];

    let response =
        await dbx.filesListFolder({
            path: articlesPath(),
        });

    entries.push(
        ...response.result.entries
    );

    while (
        response.result.has_more
    ) {
        response =
            await dbx.filesListFolderContinue({
                cursor:
                    response.result.cursor,
            });

        entries.push(
            ...response.result.entries
        );
    }

    return entries.filter(
        entry =>
            entry[".tag"] === "file"
    );
}


async function deleteFile(path) {
    await dbx.filesDeleteV2({
        path,
    });
}


export default async (request) => {
    if (request.method !== "POST") {
        return jsonResponse(
            {
                error: "Method Not Allowed",
            },
            405
        );
    }

    try {
        const cutoff =
            getCutoffDate();

        console.log(
            `Cleanup cutoff: ${cutoff.toISOString()}`
        );

        const files =
            await listArticleFiles();

        console.log(
            `Found ${files.length} article files`
        );

        const deleted = [];
        const kept = [];
        const skipped = [];

        for (const file of files) {
            const fileDate =
                getFileDate(file.name);

            /*
             * Never delete a file whose name
             * doesn't match our expected format.
             */
            if (!fileDate) {
                skipped.push({
                    name: file.name,
                    reason:
                        "Unrecognized filename",
                });

                continue;
            }

            if (fileDate < cutoff) {
                console.log(
                    `Deleting ${file.path_display}`
                );

                await deleteFile(
                    file.path_lower
                );

                deleted.push({
                    name: file.name,
                    date:
                        fileDate.toISOString(),
                });
            } else {
                kept.push({
                    name: file.name,
                    date:
                        fileDate.toISOString(),
                });
            }
        }

        return jsonResponse({
            success: true,

            retention_days:
                RETENTION_DAYS,

            cutoff:
                cutoff.toISOString(),

            found:
                files.length,

            deleted:
                deleted.length,

            kept:
                kept.length,

            skipped:
                skipped.length,

            deleted_files:
                deleted,

            skipped_files:
                skipped,
        });

    } catch (error) {
        console.error(
            "Cleanup error:",
            error
        );

        return jsonResponse(
            {
                error:
                    "Failed to clean up articles",

                message:
                    error?.message ||
                    String(error),
            },
            500
        );
    }
};
