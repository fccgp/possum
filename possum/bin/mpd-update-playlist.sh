#!/bin/bash

mpc clear
mpc update
mpc listall > /home/pos/Playlists/toute_la_musique.m3u
mpc load toute_la_musique
#mpc playlist
mpc play
#mpc repeat
#mpc random

