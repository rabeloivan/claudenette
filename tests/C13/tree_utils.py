NONE = -999999


class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def build_tree(values):
    def build(i):
        if i >= len(values) or values[i] == NONE:
            return None
        node = Node(values[i])
        node.left = build(2 * i + 1)
        node.right = build(2 * i + 2)
        return node

    return build(0)


def prefix(node, out=None):
    if out is None:
        out = []
    if node is None:
        return out
    out.append(node.val)
    prefix(node.left, out)
    prefix(node.right, out)
    return out


def infix(node, out=None):
    if out is None:
        out = []
    if node is None:
        return out
    infix(node.left, out)
    out.append(node.val)
    infix(node.right, out)
    return out


def suffix(node, out=None):
    if out is None:
        out = []
    if node is None:
        return out
    suffix(node.left, out)
    suffix(node.right, out)
    out.append(node.val)
    return out


def level_count(node):
    if node is None:
        return 0
    return 1 + max(level_count(node.left), level_count(node.right))


def levels(node):
    # BFS: returns list of (val, level, is_first_in_level).
    out = []
    if node is None:
        return out
    queue = [(node, 0)]
    qi = 0
    current_level = -1
    while qi < len(queue):
        n, lvl = queue[qi]
        qi += 1
        out.append((n.val, lvl, lvl != current_level))
        current_level = lvl
        if n.left is not None:
            queue.append((n.left, lvl + 1))
        if n.right is not None:
            queue.append((n.right, lvl + 1))
    return out


def wire(values):
    return f"{len(values)}\n" + ",".join(str(x) for x in values)
