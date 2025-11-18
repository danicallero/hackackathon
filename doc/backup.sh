#!/bin/sh

zstd -12 -T0 -o $ruta/backups/$(date +"%Y-%m-%d_%H-%M-%S")_db.sqlite3.zst $ruta/hackackathon/db.sqlite3
