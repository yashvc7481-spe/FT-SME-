const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = 3000;

const frontendPath = path.join(__dirname, "frontend");

const mimeTypes = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon"
};

const server = http.createServer((req, res) => {

    let requestPath = req.url.split("?")[0];

    if (requestPath === "/") {
        requestPath = "/index.html";
    }

    let filePath = path.join(frontendPath, requestPath);

    if (!path.extname(filePath) && fs.existsSync(filePath + ".html")) {
        filePath = filePath + ".html";
    }

    fs.readFile(filePath, (error, content) => {

        if (error) {

            console.log("File not found:", filePath);

            res.writeHead(404, {
                "Content-Type": "text/plain"
            });

            res.end("404 - Page Not Found");

            return;
        }

        const ext = path.extname(filePath);

        const contentType =
            mimeTypes[ext] || "application/octet-stream";

        res.writeHead(200, {
            "Content-Type": contentType
        });

        res.end(content);
    });
});

server.listen(PORT, () => {

    console.log("");
    console.log("🛡️  CyberGuard SME");
    console.log("----------------------------");
    console.log(`🚀 Server running at:`);
    console.log(`http://localhost:${PORT}`);
    console.log("----------------------------");
    console.log("");
});