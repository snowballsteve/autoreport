#Autoreport.py

This arctoolbox and script will assist in autogenerating paper reports based on input layer and how it sits in space relative to comparison layers.

At the moment this does not work, as I am trimming code from a more extensive version. 

# Methodology

The tool takes a layer and iterates over each record. The record is compared in space to all other supporting layers and builds a dictionary of all the values of their fields. The template will be parsed, and any fieldname in the template will be replace with the value.

Example:
Input layer is a point, comparison layer are states.

- Template text: Location is in {state_name}
- Replaced with: Locaton is in New York.

Expect a working example to come.
