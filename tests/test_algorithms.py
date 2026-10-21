"""Algorithm invariants and regression tests (standard-library unittest)."""
import random
import unittest
from studio.algorithms import SORTS, STRUCTURES, GRAPHS, trace


class AlgorithmTests(unittest.TestCase):
    def test_sorting_matches_reference(self):
        rng = random.Random(37)
        cases = [[0], [2, 1], [4, 4, 4], list(range(24)), list(range(24, 0, -1))]
        cases += [[rng.randint(-50, 50) for _ in range(24)] for _ in range(20)]
        for name in SORTS:
            for descending in [False, True]:
                for values in cases:
                    with self.subTest(name=name, descending=descending, values=values):
                        frames = trace(name, values, descending)
                        self.assertEqual(frames[-1].values, sorted(values, reverse=descending))
                        self.assertEqual(frames[0].values, values)
                        self.assertEqual(values, frames[0].values)
                        self.assertEqual(set(frames[-1].settled), set(range(len(values))))

    def test_search_present_absent_and_duplicates(self):
        for name in ['Linear search', 'Binary search']:
            for target in [-7, 2, 99]:
                frames = trace(name, [2, -7, 2, 6], target=target)
                result = frames[-1]
                if target == 99: self.assertIn('not found', result.message)
                else: self.assertEqual(result.values[result.settled[0]], target)

    def test_graph_results(self):
        for name in ['Breadth-first search', 'Depth-first search', 'Dijkstra']:
            final = trace(name, [1])[-1]
            self.assertEqual(set(final.visited), set(range(7)))
        for name in ['Prim', 'Kruskal']:
            final = trace(name, [1])[-1]
            self.assertEqual(len(final.settled), 6)
            self.assertIn('13', final.message)
        self.assertEqual(trace('Dijkstra', [1])[-1].message, 'Shortest distances from A: A=0, B=4, C=2, D=9, E=3, F=7, G=8')

    def test_tree_invariants(self):
        for name in ['Binary search tree', 'AVL tree']:
            for values in [list(range(24)), list(range(24, 0, -1)), [3, 1, 2, 6, 5, 4, 3]]:
                final = trace(name, values)[-1]
                children = {k: [] for k in final.nodes}
                descendants = set()
                for u, v, _ in final.edges: children[u].append(v); descendants.add(v)
                roots = set(final.nodes) - descendants
                self.assertEqual(len(roots), 1)
                def check(k, low=float('-inf'), high=float('inf')):
                    value = final.nodes[k]; self.assertTrue(low < value < high)
                    heights = [0, 0]
                    for child in children[k]:
                        side = int(final.nodes[child] > value)
                        heights[side] = check(child, value if side else low, high if side else value)
                    if name == 'AVL tree': self.assertLessEqual(abs(heights[0] - heights[1]), 1)
                    return max(heights) + 1
                check(roots.pop())
                self.assertEqual(set(final.nodes.values()), set(values))

    def test_heap_invariants_at_completion(self):
        for name in ['Min heap', 'Max heap']:
            a = trace(name, [8, 3, -1, 4, 22, 3, 0])[-1].values
            for i in range(1, len(a)):
                if name == 'Min heap': self.assertLessEqual(a[(i - 1) // 2], a[i])
                else: self.assertGreaterEqual(a[(i - 1) // 2], a[i])

    def test_huffman_weights_and_prefixes(self):
        final = trace('Huffman coding', [5, 9, 12, 13, 16, 45])[-1]
        roots = set(final.nodes) - {v for _, v, _ in final.edges}
        self.assertEqual(final.nodes[roots.pop()], '100')
        codes = [part.split('=')[1] for part in final.message.removeprefix('Prefix codes: ').split()]
        self.assertEqual(len(codes), 6)
        for i, code in enumerate(codes):
            for j, other in enumerate(codes):
                if i != j: self.assertFalse(other.startswith(code))

    def test_invalid_inputs(self):
        for values in [[], list(range(25))]:
            with self.assertRaises(ValueError): trace('Bubble sort', values)
        for values in [[0, 2], [-1, 3]]:
            with self.assertRaises(ValueError): trace('Huffman coding', values)


if __name__ == '__main__':
    unittest.main()
