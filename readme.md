#Autoreport.py

This arctoolbox and script will assist in autogenerating paper reports based on input layer and how it sits in space relative to comparison layers.

## Methodology

The tool takes a layer and iterates over each record. The record is compared in space to all other supporting layers and builds a dictionary of all the values of their fields. The template will be parsed, and any fieldname in the template will be replace with the value.

Example:
Input layer is a point, comparison layer are states.

- Template text: Location is in {state_name}
- Replaced with: Locaton is in New York.

To see what the tool does look in the example folder, run the tool using gps_points as the input layer and template.md as the template file

##License
You are free to do whatever you want with this tool provided you inform the author. A github fork notification is sufficient. Feel free to create issues or pull requests.


