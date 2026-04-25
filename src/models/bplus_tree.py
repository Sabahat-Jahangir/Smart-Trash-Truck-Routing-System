class BPlusNode:
    def __init__(self, leaf=True):
        self.leaf = leaf
        self.keys = []
        self.child_pointers = []
        self.next = None  # For leaf node linking

class BPlusTree:
    def __init__(self, order=4):
        self.root = BPlusNode(leaf=True)
        self.order = order
        
    def insert(self, key, value):
        root = self.root
        if len(root.keys) == (2 * self.order) - 1:
            new_root = BPlusNode(leaf=False)
            self.root = new_root
            new_root.child_pointers.insert(0, root)
            self._split_child(new_root, 0)
            self._insert_non_full(new_root, key, value)
        else:
            self._insert_non_full(root, key, value)

    def _split_child(self, parent, index):
        order = self.order
        child = parent.child_pointers[index]
        new_node = BPlusNode(leaf=child.leaf)
        
        parent.keys.insert(index, child.keys[order - 1])
        parent.child_pointers.insert(index + 1, new_node)
        
        new_node.keys = child.keys[order:]
        child.keys = child.keys[:order - 1]
        
        if not child.leaf:
            new_node.child_pointers = child.child_pointers[order:]
            child.child_pointers = child.child_pointers[:order]
        
        if child.leaf:
            new_node.next = child.next
            child.next = new_node

    def _insert_non_full(self, node, key, value):
        i = len(node.keys) - 1
        
        if node.leaf:
            while i >= 0 and key < node.keys[i][0]:
                i -= 1
            node.keys.insert(i + 1, (key, value))
        else:
            while i >= 0 and key < node.keys[i][0]:
                i -= 1
            i += 1
            
            if len(node.child_pointers[i].keys) == (2 * self.order) - 1:
                self._split_child(node, i)
                if key > node.keys[i][0]:
                    i += 1
            self._insert_non_full(node.child_pointers[i], key, value)

    def search(self, key):
        return self._search_recursive(self.root, key)

    def _search_recursive(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i][0]:
            i += 1
            
        if node.leaf:
            if i < len(node.keys) and node.keys[i][0] == key:
                return node.keys[i][1]
            return None
            
        return self._search_recursive(node.child_pointers[i], key)

    def range_search(self, start_key, end_key):
        results = []
        node = self._find_leaf(self.root, start_key)
        
        while node:
            for key, value in node.keys:
                if start_key <= key <= end_key:
                    results.append((key, value))
                elif key > end_key:
                    return results
            node = node.next
        return results

    def _find_leaf(self, node, key):
        if node.leaf:
            return node
            
        i = 0
        while i < len(node.keys) and key >= node.keys[i][0]:
            i += 1
        return self._find_leaf(node.child_pointers[i], key) 