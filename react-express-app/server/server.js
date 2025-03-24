const express = require("express");
const mysql = require("mysql");
const cors = require("cors");
const path = require("path");

const app = express();

app.use(express.static(path.join(__dirname, "public")))
app.use(cors());
app.use(express.json());

const PORT = 5000

// const db

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});