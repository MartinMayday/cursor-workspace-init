/**
 * Main entry point for test repository v00.
 */

const express = require('express');
const app = express();
const PORT = 3000;

app.get('/', (req, res) => {
  res.send('Hello from test repository v00!');
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

