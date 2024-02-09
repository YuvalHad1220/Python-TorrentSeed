// Import required modules
import sqlite3 from "sqlite3";
import mongoose from "mongoose";

// Define database paths and connection strings
const sqliteDbPath = "torrents_and_clients.db";
const mongoDbUri = "mongodb://localhost:27017/Bun-Torrent";

// Connect to the mongodb database asynchronously
async function connectToMongoDb() {
  try {
    await mongoose.connect(mongoDbUri);
    console.log("Connected to MongoDB successfully.");
  } catch (err) {
    console.error(`Error connecting to MongoDB: ${err}`);
    process.exit(1);
  }
}


async function main() {
  try {
    // Connect to both databases asynchronously
    await connectToMongoDb();
    const sqliteDb = new sqlite3.Database(sqliteDbPath);
    console.log("Connected to SQLite successfully.");

    // Define the torrent schema with additional fields
    const torrentSchema = new mongoose.Schema({
      _id: { type: mongoose.Types.ObjectId, required: true },
      name: { type: String, required: true },
      size: { type: Number, required: true },
      seeders: { type: Number, required: true }, // Set to 1
      leechers: { type: Number, required: true }, // Set to 1
      clientId: { type: mongoose.Types.ObjectId, required: true },
      downloaded: Number,
      uploaded: Number,
      downloadSpeed: { type: Number, required: true },
      uploadSpeed: { type: Number, required: true },
      isStartAnnounced: { type: Boolean, required: true },
      isFinishAnnounced: { type: Boolean, required: true },
      announceUrl: { type: String, required: true },
      infoHash: { type: mongoose.Schema.Types.Buffer, required: true },
      timeToAnnounce: { type: Number, required: true }, // Set to 0
      tempTakenDownload: { type: Number, required: true }, // Replace with actual value if available
      tempTakenUpload: { type: Number, required: true }, // Replace with actual value if available
    });

    const Torrent = mongoose.model("Torrent", torrentSchema);

    // Define the SQL query
    const sql = `SELECT * FROM TorrentSQL WHERE announce_url LIKE '%fuzer.me:2710/%'`;

    // Execute the query
    sqliteDb.all(sql, async (err, rows) => {
      if (err) {
        console.error(err);
        return;
      }

      // Loop through the rows and modify them
      console.log(rows.length);
      for (const row of rows) {
        const _id = new mongoose.Types.ObjectId();
        const clientId = new mongoose.Types.ObjectId("657860dc10fd5b9e69a64c0c");

        // Check if torrent with same name already exists in db
        const existingTorrent = await Torrent.findOne({ name: row.name });

        if (!existingTorrent) {
          // Create and save the new torrent to MongoDB
          const newTorrent = new Torrent({
            _id,
            name: row.name,
            size: row.size,
            seeders: 1, // Set to 1
            leechers: 1, // Set to 1
            clientId,
            downloaded: row.downloaded,
            uploaded: row.uploaded,
            downloadSpeed: row.download_speed,
            uploadSpeed: row.upload_speed,
            isStartAnnounced: row.is_start_announced === 1,
            isFinishAnnounced: row.is_finish_announced === 1,
            announceUrl: row.announce_url,
            infoHash: row.info_hash,
            timeToAnnounce: 0, // Set to 0
            tempTakenDownload: 0, // Replace with actual value if available
            tempTakenUpload: 0, // Replace with actual value if available
          });

          await newTorrent.save();
          console.log(`Added torrent ${row.name} to MongoDB.`);
        } else {
          
            console.log(`Skipping torrent ${row.name} as it already exists in MongoDB.`);
        }
      }
    });

  } catch (err) {
    console.error(err);
  }
}

main();
