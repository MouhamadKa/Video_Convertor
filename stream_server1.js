const http=require('http');
const fs=require("fs");
const path=require("path");


const server = http.createServer((req, res) => {
    res.setHeader("Access-Control-Allow-Origin", "*"); 
    if (req.method === 'GET') {
        const filepath = path.resolve('./media/' + req.url);
        fs.stat(filepath, (err, stat) => {
            if (err) {
                res.writeHead(404);
                return res.end("File not found");
            }

            const fileSize = stat.size;
            const range = req.headers.range;

            const contentType = path.extname(filepath) === '.mpd' ? 'application/dash+xml' : 'video/mp4';

            if (range) {
                const parts = range.replace(/bytes=/, "").split("-");
                const start = parseInt(parts[0], 10);
                const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
                const chunksize = (end - start) + 1;
                const file = fs.createReadStream(filepath, { start, end });
                const head = {
                    'Content-Range': `bytes ${start}-${end}/${fileSize}`,
                    'Accept-Ranges': 'bytes',
                    'Content-Length': chunksize,
                    'Content-Type': contentType,  // Use dynamic content type based on file extension
                };
                res.writeHead(206, head);
                file.pipe(res);
            } else {
                const head = {
                    'Content-Length': fileSize,
                    'Content-Type': contentType,  // Use dynamic content type based on file extension
                };
                res.writeHead(200, head);
                fs.createReadStream(filepath).pipe(res);
            }
        });
    } else {
        res.writeHead(400);
        res.end("Bad request");
    }
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server listening on port: ${PORT}`);
});
