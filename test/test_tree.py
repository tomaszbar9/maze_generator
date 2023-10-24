from collections import deque
from unittest.mock import patch
import pytest
from src import Branch, Tree, Instructions

REG_DICT = {
    (0, 0): {(1, 0), (0, 1)},
    (0, 1): {(0, 2), (0, 0)},
    (0, 2): {(0, 1), (0, 3)},
    (0, 3): {(0, 2), (0, 4)},
    (0, 4): {(0, 3), (1, 4)},
    (1, 0): {(1, 1), (2, 0), (0, 0)},
    (1, 1): {(1, 0), (1, 2)},
    (1, 2): {(1, 1), (1, 3)},
    (1, 3): {(2, 3), (1, 2)},
    (1, 4): {(2, 4), (0, 4)},
    (2, 0): {(1, 0)},
    (2, 1): {(2, 2)},
    (2, 2): {(3, 2), (2, 1)},
    (2, 3): {(1, 3)},
    (2, 4): {(1, 4)},
    (3, 0): {(4, 0)},
    (3, 1): {(4, 1)},
    (3, 2): {(3, 3), (4, 2), (2, 2)},
    (3, 3): {(3, 2), (3, 4)},
    (3, 4): {(4, 4), (3, 3)},
    (4, 0): {(5, 0), (3, 0)},
    (4, 1): {(3, 1), (5, 1)},
    (4, 2): {(3, 2)},
    (4, 3): {(4, 4)},
    (4, 4): {(5, 4), (3, 4), (4, 3)},
    (5, 0): {(4, 0), (5, 1)},
    (5, 1): {(5, 0), (4, 1), (5, 2)},
    (5, 2): {(5, 3), (5, 1)},
    (5, 3): {(5, 4), (5, 2)},
    (5, 4): {(4, 4), (5, 3)}
}
SMALL_DICT = {(2, 0): {(1, 0)}}


class TestBranch:
    def test_init(self):
        branch = Branch((2, 0), SMALL_DICT)
        assert branch.points_dict == SMALL_DICT
        assert branch.direction == (1, 0)
        assert not branch.children
        assert branch.line == deque([(2, 0)])
        assert branch.finished is False

    @pytest.mark.parametrize("leaf, line",
                             [((2, 3),
                               [(2, 3), (1, 3), (1, 2), (1, 1), (1, 0)]),
                              ((2, 1),
                               [(2, 1), (2, 2), (3, 2)]),
                              ((4, 3), [(4, 3), (4, 4)])
                              ])
    def test_extend(self, leaf, line):
        branch = Branch(leaf, REG_DICT)
        branch.extend()
        assert branch.line == deque(line)
        assert branch.direction is None

    def test_reverse(self):
        parent = Branch((2, 0), SMALL_DICT)
        kid_a = Branch((2, 0), SMALL_DICT)
        kid_b = Branch((2, 0), SMALL_DICT)
        kid_c = Branch((2, 0), SMALL_DICT)
        parent.children = deque([kid_a, kid_b, kid_c])
        parent.line = deque([(2, 3), (1, 3), (1, 2)])
        parent.reverse_()
        assert parent.children == deque([kid_c, kid_b, kid_a])
        assert parent.line == deque([(1, 2), (1, 3), (2, 3)])

    @patch('src.Branch.reverse_', autospec=True)
    def test_join(self, mock_reverse_):
        branch_1 = Branch((2, 0), SMALL_DICT)
        branch_1.children = deque(['a', 'b'])
        branch_2 = Branch((2, 0), SMALL_DICT)
        branch_2.children = deque(['c', 'd'])
        branch_2.line = deque([(3, 0), (4, 0)])
        branch_1.join_(branch_2)

        mock_reverse_.assert_called_once_with(branch_2)
        assert branch_1.line == deque([(2, 0), (3, 0), (4, 0)])
        assert branch_1.children == deque(['a', 'b', 'c', 'd'])


class TestTree:
    @patch('src.Tree.get_queue')
    @patch('src.Tree.get_trunks')
    def test_init(self, mock_get_trunks, mock_get_queue):
        tree = Tree(SMALL_DICT)
        assert tree.points_dict == SMALL_DICT
        assert tree.trunks == list()
        assert tree.nodes == dict()
        assert tree._instructions is None
        assert mock_get_trunks.called
        assert mock_get_queue.called

    @pytest.mark.parametrize("dictionary, points",
                             [(REG_DICT,
                               {(2, 0), (2, 1), (2, 3), (2, 4),
                                (3, 0), (3, 1), (4, 2), (4, 3)}),
                              (SMALL_DICT, {(2, 0)}),
                              (dict(), set())])
    def test_get_queue(self, dictionary, points):
        tree = Tree(dict())
        tree.points_dict = dictionary
        branches = tree.get_queue()
        branches_first_points = set(branch.line[0] for branch in branches)
        assert branches_first_points == points

    @patch('src.Tree.get_trunks')
    def test_new_node(self, muted_get_trunks):
        tree = Tree(REG_DICT)
        assert tree.new_node((4, 4)) == {"branches": list(),
                                         "open_directions": {
                                             (5, 4), (3, 4), (4, 3)}}

    @patch('src.Tree.get_trunks')
    def test_new_node_invalid(self, muted_get_trunks):
        tree = Tree(SMALL_DICT)
        with pytest.raises(KeyError):
            tree.new_node((1, 0))

    def test_trim(self):
        tree = Tree(dict())
        branch_1 = Branch((2, 0), SMALL_DICT)
        branch_1.line = deque([(0, 0), (0, 1), (0, 2), (0, 3)])
        branch_2 = Branch((2, 0), SMALL_DICT)
        branch_2.line = deque([(0, 0), (0, 1), (0, 2)])
        branch_3 = Branch((2, 0), SMALL_DICT)
        branch_3.line = deque([(0, 0), (0, 1)])
        node = {"branches": [branch_1, branch_2, branch_3],
                "open_directions": {(5, 4)}}
        parent = tree.trim(node)
        assert parent == branch_1
        assert branch_1.direction == (5, 4)
        assert set(branch_1.children) == {branch_2, branch_3}

    def test_move_to_trunks(self):
        tree = Tree(dict())
        branch_to_be_finished = Branch((2, 0), SMALL_DICT)
        branch_to_be_finished.line = deque([(1, 3), (1, 2), (1, 1)])
        branch_1 = Branch((2, 0), SMALL_DICT)
        branch_1.line = deque([(0, 0), (0, 1), (0, 2), (0, 3)])
        branch_2 = Branch((2, 0), SMALL_DICT)
        branch_2.line = deque([(1, 1), (1, 2)])
        tree.queue = deque([branch_1, branch_2])
        tree.move_to_trunks(branch_to_be_finished)
        assert branch_to_be_finished in tree.trunks
        assert branch_2.finished

    @pytest.mark.parametrize("nodes",
                             [{(1, 0): {"branches": [],
                                        "open_directions": {(0, 0), (1, 1), (2, 0)}}},
                              {}])
    def test_get_node(self, nodes):
        d = {(2, 0): {(1, 0)},
             (1, 0): {(0, 0), (1, 1), (2, 0)}}
        tree = Tree(d)
        branch = Branch((2, 0), d)
        branch.line = deque([(2, 0), (1, 0)])
        tree.nodes = nodes
        node = tree.get_node(branch)
        assert node == {"branches": [branch],
                        "open_directions": {(0, 0), (1, 1)}}
        assert tree.nodes[(1, 0)] == node

    @patch('src.Tree.move_to_trunks')
    @patch('src.Branch.extend', autospec=True)
    def test_serve_branch_finished(self, mock_extend, mock_move_to_trunks):
        d = {(2, 0): {(0, 1)}, (1, 1): {(1, 0)}}
        tree = Tree(d)
        branch = Branch((2, 0), d)
        branch.line = deque([(2, 0), (1, 0), (1, 1)])
        tree.serve(branch)
        mock_extend.assert_called_with(branch)
        mock_move_to_trunks.assert_called_with(branch)

    @patch('src.Tree.get_node')
    @patch('src.Branch.extend', autospec=True)
    def test_serve_branch_unfinished(self, mock_extend, mock_get_node):
        d = {(2, 0): {(0, 1)}, (1, 1): {(1, 0), (0, 1), (1, 2)}}
        tree = Tree(d)
        branch = Branch((2, 0), d)
        branch.line = deque([(2, 0), (1, 0), (1, 1)])
        tree.serve(branch)
        mock_extend.assert_called_with(branch)
        mock_get_node.assert_called_with(branch)

    @pytest.mark.parametrize("open_directions, "
                             "trim_called, in_queue, "
                             "join_called, in_trunks",
                             [({(0, 0)}, True, True, False, False),
                              ({}, False, False, True, True)])
    @patch('src.Branch.join_', autospec=True)
    @patch('src.Tree.trim', autospec=True)
    @patch('src.Tree.get_node')
    @patch('src.Branch.extend')
    def test_serve_branch_unfinished_check_for_directions(
            self, mock_extend, mock_get_node,
            mock_trim, mock_join,
            open_directions,
            trim_called, in_queue,
            join_called, in_trunks):
        d = {(2, 0): {(0, 1)}, (1, 1): {(1, 0), (0, 1), (1, 2)}}

        tree = Tree(d)
        branch = Branch((2, 0), d)
        branch.line = deque([(2, 0), (1, 0), (1, 1)])
        another_branch = Branch((2, 0), d)
        node = {"branches": [another_branch],
                "open_directions": open_directions}
        mock_get_node.return_value = node
        mock_trim.return_value = "branch that should be in queue"
        tree.serve(branch)

        assert mock_trim.called is trim_called
        if trim_called:
            mock_trim.assert_called_with(node)

        assert ("branch that should be in queue" in tree.queue) is in_queue
        if in_queue:
            assert tree.queue[0] == "branch that should be in queue"

        assert mock_join.called is join_called
        if join_called:
            mock_join.assert_called_with(branch, another_branch)

        assert (branch in tree.trunks) is in_trunks

    @pytest.mark.parametrize("finished, called",
                             [(True, False),
                              (False, True)])
    @patch('src.Tree.serve')
    def test_get_trunks(self, mock_serve, finished, called):
        tree = Tree(dict())
        branch = Branch((2, 0), SMALL_DICT)
        branch.finished = finished
        tree.queue = deque([branch])
        tree.get_trunks()
        assert mock_serve.called is called


def test_instructions():
    branch_1 = Branch((2, 0), SMALL_DICT)
    branch_1.line = ['branch_1']
    branch_2 = Branch((2, 0), SMALL_DICT)
    branch_2.line = ['branch_2']
    branch_3 = Branch((2, 0), SMALL_DICT)
    branch_3.line = ['branch_3']
    branch_4 = Branch((2, 0), SMALL_DICT)
    branch_4.line = ['branch_4']
    branch_5 = Branch((2, 0), SMALL_DICT)
    branch_5.line = ['branch_5']
    branch_6 = Branch((2, 0), SMALL_DICT)
    branch_6.line = ['branch_6']
    branch_2.children = deque([branch_3, branch_4])
    branch_3.children = deque([branch_5])
    branch_5.children = deque([branch_6])
    trunks = [branch_1, branch_2]
    instructions = Instructions(trunks)
    assert list(instructions) == [['branch_2'], ['branch_3'], ['branch_5'],
                                  ['branch_6'], ['branch_4'], ['branch_1']]
