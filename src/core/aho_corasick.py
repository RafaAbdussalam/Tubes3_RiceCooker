# File: src/core/aho_corasick.py

from collections import deque

class TrieNode:
    """Node untuk struktur data Trie."""
    def __init__(self):
        self.children = {}  # {char: TrieNode}
        self.fail = None      # Failure link
        self.output = []      # Daftar keyword yang berakhir di node ini

class AhoCorasick:
    """Implementasi algoritma Aho-Corasick."""
    def __init__(self):
        self.root = TrieNode()

    def add_keyword(self, keyword: str):
        """Menambahkan sebuah keyword ke dalam Trie."""
        node = self.root
        for char in keyword:
            node = node.children.setdefault(char, TrieNode())
        node.output.append(keyword)

    def build_failure_links(self):
        """Membangun failure links untuk semua node menggunakan Breadth-First Search (BFS)."""
        queue = deque()
        # Inisialisasi failure links untuk anak-anak dari root
        for node in self.root.children.values():
            node.fail = self.root
            queue.append(node)

        while queue:
            current_node = queue.popleft()
            for char, next_node in current_node.children.items():
                queue.append(next_node)
                fail_node = current_node.fail
                # Cari failure link untuk next_node
                while char not in fail_node.children and fail_node is not self.root:
                    fail_node = fail_node.fail
                
                if char in fail_node.children:
                    next_node.fail = fail_node.children[char]
                else:
                    next_node.fail = self.root
                
                # Gabungkan output dari failure link
                next_node.output.extend(next_node.fail.output)

    def search(self, text: str) -> dict:
        """
        Mencari semua keyword dalam teks dan mengembalikan posisinya.
        Return: dict dalam format {'keyword': [end_index_1, end_index_2, ...]}
        """
        results = {}
        node = self.root
        for i, char in enumerate(text):
            while char not in node.children and node is not self.root:
                node = node.fail
            
            if char in node.children:
                node = node.children[char]
            else:
                # Jika tidak ada transisi bahkan dari root, tetap di root
                node = self.root

            # Jika ada output di node saat ini, catat semua keyword yang cocok
            if node.output:
                for keyword in node.output:
                    if keyword not in results:
                        results[keyword] = []
                    # Mencatat posisi akhir dari keyword yang ditemukan
                    results[keyword].append(i)
        return results