Aetheria Web MUD - Website Starter
==================================

Contents:
- frontend/index.html, style.css, client.js, animations.js
- database/schema.sql, database/seed_world.sql
- backend/requirements.txt

Quick local run:
1. Put these folders into your Aetheria project root.
2. Create/configure the aetheria_mud database using the SQL files.
3. In backend/, create a venv and install requirements.txt.
4. Configure DB_CONFIG in your existing backend/server.py.
5. Start the Python WebSocket server on localhost:8765.
6. In a second terminal: cd frontend && python -m http.server 8080
7. Browse to http://localhost:8080.

The client expects the documented JSON protocol:
- Browser sends {"command":"..."}; first command is the character name.
- Server messages have type text, vitals, room, or anim.
- For a public Nginx deployment, the server must be behind /ws and the browser page must use HTTPS/WSS.

Important:
This is a frontend starter based on the backend protocol printed in the supplied PDF. It does not include a replacement server.py. Verify that your current backend matches the protocol before public deployment. Character names are not authenticated in the supplied prototype.
