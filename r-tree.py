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
    
    def remove(self, rectangle):
        path = []
        node, index = self._find_rectangle(self.root, rectangle, path)
        if node is None or index is None:
            return False
        # Remover em definitivo
        del node.children[index]
        self._adjust_tree(path)
        return True
    
    def _find_rectangle(self, node, rectangle, path):
        if node.is_leaf:
            for i, child in enumerate(node.children):
                if child.bounding_box == rectangle:
                    return node, i
            return None, None
        path.append(node)
        for child in node.children:
            result = self._find_rectangle(child, rectangle, path)
            if result[0]:
                return result
        path.pop()
        return None, None
    
    def _adjust_tree(self, path):
        for node in reversed(path):
            node.upfate_bounding_box()
            if not node.is_leaf and len(node.children) < 2:
                for child in node.children:
                    self._reinsert(child)
                node.children.clear()
    
    def _reinsert(self, node):
        leaf = self._choose_leaf(self.root, node.bounding_box)
        leaf.children.append(node)
        leaf.update_bounding_box()
        if len(leaf.children) > self.max_children:
            self._split_node(leaf)
    
    def _split_node(self, node):
        node.children.sort(key=lambda child: child.bounding_box.x_min)
        mid = len(node.children) // 2
        new_node = RTreeNode(is_leaf=node.is_leaf)
        new_node.children = node.children[mid:]
        node.children = node.children[:mid]
        node.update_bounding_box()
        new_node.update_bounding_box()

        if node == self.root:
            new_root = RTreeNode(is_leaf=False)
            new_root.children = [node, new_node]
            new_root.update_bounding_box()
            self.root = new_root
        else:
            parent = self._find_parent(self.root, node)
            parent.children.append(new_node)
            parent.update_bounding_box()
            if len(parent.children) > self.max_children:
                self._split_node(parent)

    def _find_parent(self, node, target):
        if node.is_leaf:
            return None
        for child in node.children:
            if child == target:
                return node
            result = self._find_parent(child, target)
            if result:
                return result
        return None