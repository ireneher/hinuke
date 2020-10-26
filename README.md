# hinuke
Tools for the Foundry's Nuke
### How to Install ###
1. git clone https://github.com/ireneher/hinuke.git
2. cd hinuke
3. source setup.sh

This method works per session. If desired, modify ~/.bashrc to permanently append to path.

## Tools ##
### Node Controller ###
Custom panel that acts as a global Nodegraph manager.
Features:
* **Query** and retrieve (by Name, Type, or Selection) with the option to filter out disabled nodes.
* **View** selected node, via number key.
* **Display** properties by double clicking.
* **Frame** node, meaning zoom into it in the nodegraph.
* **Pin**/Unpin selected in current list, to curate panel.
* **Disable**/Enable panel selection in nodegraph.
* **Rename** nodes in panel selection (two modes: replace or absolute).

### Knob Share ###
Properties menu tool to edit knobs in batch. Value is propagated from current node to others of the same type, according to user selection.


