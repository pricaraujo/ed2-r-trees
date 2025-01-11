class Rectangle:
    def __init__(self, x_min, y_min, x_max, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def area(self):
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)

    def expand(self, other):
        self.x_min = min(self.x_min, other.x_min)
        self.y_min = min(self.y_min, other.y_min)
        self.x_max = max(self.x_max, other.x_max)
        self.y_max = max(self.y_max, other.y_max)

    def overlaps(self, other):
        return not (self.x_max < other.x_min or self.x_min > other.x_max or
                    self.y_max < other.y_min or self.y_min > other.y_max)


class RTreeNode:
    def __init__(self, is_leaf=True):
        self.is_leaf = is_leaf
        self.children = [] 
        self.bounding_box = None

    def update_bounding_box(self):
        if not self.children:
            return
        self.bounding_box = Rectangle(
            self.children[0].bounding_box.x_min,
            self.children[0].bounding_box.y_min,
            self.children[0].bounding_box.x_max,
            self.children[0].bounding_box.y_max
        )
        for child in self.children[1:]:
            self.bounding_box.expand(child.bounding_box)


class RTree:
    def __init__(self, max_children=4):
        self.root = RTreeNode()
        self.max_children = max_children

    def insert(self, rectangle):
        node = self._choose_leaf(self.root, rectangle)
        node.children.append(RTreeNode(is_leaf=True))
        node.children[-1].bounding_box = rectangle
        node.update_bounding_box()
        if len(node.children) > self.max_children:
            self._split_node(node)

    def _choose_leaf(self, node, rectangle):
        if node.is_leaf:
            return node
        # Escolhe o filho com o menor aumento de área
        best_child = min(
            node.children,
            key=lambda child: self._expansion_cost(child.bounding_box, rectangle)
        )
        return self._choose_leaf(best_child, rectangle)
