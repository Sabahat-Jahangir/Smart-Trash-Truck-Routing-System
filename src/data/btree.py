from typing import Any, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class BTreeNode:
    leaf: bool
    keys: List[int]
    values: List[Any]
    children: List['BTreeNode']
    next_leaf: Optional['BTreeNode'] = None
    
    def is_full(self, order: int) -> bool:
        return len(self.keys) >= order - 1

class BPlusTree:
    def __init__(self, order: int = 4):
        self.root = BTreeNode(leaf=True, keys=[], values=[], children=[])
        self.order = order
        
    def insert(self, key: int, value: Any):
        """Insert a key-value pair into the B+ tree."""
        if self.root.is_full(self.order):
            # Split root if full
            new_root = BTreeNode(leaf=False, keys=[], values=[], children=[self.root])
            self._split_child(new_root, 0)
            self.root = new_root
            
        self._insert_non_full(self.root, key, value)
        
    def _insert_non_full(self, node: BTreeNode, key: int, value: Any):
        """Insert into a non-full node."""
        i = len(node.keys) - 1
        
        if node.leaf:
            # Insert into leaf node
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            node.keys.insert(i, key)
            node.values.insert(i, value)
        else:
            # Find child to insert into
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            
            if node.children[i].is_full(self.order):
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
                    
            self._insert_non_full(node.children[i], key, value)
            
    def _split_child(self, parent: BTreeNode, child_index: int):
        """Split a full child node."""
        order = self.order
        child = parent.children[child_index]
        new_node = BTreeNode(leaf=child.leaf, keys=[], values=[], children=[])
        
        # Split keys and values
        mid = order // 2
        
        if child.leaf:
            new_node.keys = child.keys[mid:]
            new_node.values = child.values[mid:]
            child.keys = child.keys[:mid]
            child.values = child.values[:mid]
            
            # Update leaf node links
            new_node.next_leaf = child.next_leaf
            child.next_leaf = new_node
        else:
            new_node.keys = child.keys[mid + 1:]
            new_node.values = child.values[mid + 1:]
            new_node.children = child.children[mid + 1:]
            parent.keys.insert(child_index, child.keys[mid])
            parent.values.insert(child_index, child.values[mid])
            child.keys = child.keys[:mid]
            child.values = child.values[:mid]
            child.children = child.children[:mid + 1]
            
        parent.children.insert(child_index + 1, new_node)
        
    def search(self, key: int) -> Optional[Any]:
        """Search for a key in the B+ tree."""
        node = self.root
        
        while not node.leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
            
        for i, k in enumerate(node.keys):
            if k == key:
                return node.values[i]
        return None
        
    def range_search(self, start_key: int, end_key: int) -> List[Tuple[int, Any]]:
        """Search for all key-value pairs in a given range."""
        result = []
        node = self.root
        
        # Find leaf node containing start_key
        while not node.leaf:
            i = 0
            while i < len(node.keys) and start_key >= node.keys[i]:
                i += 1
            node = node.children[i]
            
        # Collect all values in range
        while node:
            for i, key in enumerate(node.keys):
                if start_key <= key <= end_key:
                    result.append((key, node.values[i]))
            node = node.next_leaf
            
        return result
        
    def update(self, key: int, value: Any) -> bool:
        """Update the value associated with a key."""
        node = self.root
        
        while not node.leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
            
        for i, k in enumerate(node.keys):
            if k == key:
                node.values[i] = value
                return True
        return False 