# Olympus Ground Control

Ground station code that interfaces with the Quail GSE board to provide the ground control interface for olympus 

## Quickstart

### Setup

Make sure you're using at least python version 3.7. Heads up that installing it on ubuntu with pip isn't as simple as it should be.  I recomend using a virtual enviroment.

Run `pip install -r requirements.txt` to install the dependancies

### Usage

To launch dev server `adev runserver demo.py --port 8080 --livereload`

To launch "deployment" server `python demo.py`

## Feature rundown

### Dashboard Page(s)

![Dashboard Page](imgs/dashboard.png)

### Slate Page

Shows a live updating view of the raw slate. Useful for debugging

### Configuration

This page allows you to authenticate you browser using the password `MAGIC` to send commands to quail. Otherwise you're an observer who can't influence quail (except to add ing to server load). There's also a buttong allowing you to reboot quail and send raw commands (eg `{'slate.quail.battery.Voltage.ofs': 0.0}` to remove voltage taring)

### Stream integration

In addition to the pages listed in the sidebar the server also exposes the `/mass_graph` `ox_graph` and `fuel_graph` pages that are useful for embedding into a live stream

## Architecture

### Description

The repo functions basically as a http server that serves the webui to any browser. It relays data and commands to the quail and back. It uses socketio to communicate to the browser and a mixture of UDP and TCP to talk to quail. 


### Dataflow
![Network Diagram](imgs/network.drawio.svg)


### Physical Conenctions
![Physical Connections](imgs/physical.drawio.svg)


### Code Structure


### TODOs

- Bug in graph rescaling on changed units: Autorescaling doesn't work poperly on graphs with converted units
- Make units changing safer: Currently we don't assert at all what unit we are converting from etc. Once quail reports all units we should turn this on
- Write readme: In progress
- Enabled logging: Since quail *should* log stuff to SD this isn't a top prority but it should happen