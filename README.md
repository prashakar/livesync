# **LiveSync**

*LiveSync* is a peer-to-peer TCP file synchronization program. It allows you to sync multiple files across all your PC's. Think of it as DropBox but peer-to-peer :)

##Usage

*Ensure all dependencies are installed before proceeding.*

Start the tracking server:

	python3.5 livesync_server.py [your private IP address] [desired port]

The tracking server should now be in listening state.

Now let's set-up a client or 'peer':

	python3.5 livesync_client.py

When prompted, enter your IP address.

Great! You should now see a welcome message from the tracking server.

Here's how you sync files. You get two directories to work with:

**livesync_send** - place any file you want to share among all your peers in here!

**livesync_received** - any shared files will show up here

## Dependencies

*LiveSync* is built with Python3.5 and requires the *watchdog* package. Here's how to get started.

Debian Linux:

```bash
apt-get install python3-pip
pip3 install setuptools
pip3 install watchdog

```

## Meta

Prashakar Prabagaran – prashakarp@gmail.com

[LiveSync repo on GitHub](https://github.com/prashakar/livesync)
[Personal Website](http://www.prashakar.com)
