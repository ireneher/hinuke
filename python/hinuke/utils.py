import nuke


def getNodesByTypeRecursively(type):
    # Utility function to work around nuke bug with ID 163807
    nodes = []
    for node in nuke.allNodes(recurseGroups=True):
        if node.Class() == type:
            nodes.append(node)

    return nodes


def getPartiallyMatchingNodes(partialName, recursive=True):
    partialName = partialName.lower()
    return [
        node for node in nuke.allNodes(recurseGroups=recursive) if partialName in node.name().lower()
    ]
