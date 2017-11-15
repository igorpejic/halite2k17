import math
import random

from cocos.rect import Rect

def distance(a, b):
    ax, ay = a
    bx, by = b
    return math.sqrt((ax-bx)**2 + (ay-by)**2)

class QuadTreeNode(Rect):
    def __init__(self, x, y, width, height, parent, minimum_size=None):
        super(QuadTreeNode, self).__init__(x, y, width, height)
        self.parent = parent
        self.nodes = []
        self.minimum_size = minimum_size or parent.minimum_size
        self.n_top = []
        self.n_bottom = []
        self.n_left = []
        self.n_right = []

    def check_node(self, blockers):
        for blocker in blockers:
            if blocker.intersects(self):
                if self.width <= self.minimum_size:
                    return False
                self.subdivide(blockers)
                if not self.nodes:
                    # my subdivision came up empty; remove me entirely
                    return False
                break
        return True

    def subdivide(self, blockers):
        # bottom left
        width = self.width / 2
        height = self.height / 2
        # top left
        node = QuadTreeNode(self.x, self.y, width, height, self)
        if node.check_node(blockers):
            self.nodes.append(node)
        # top right
        node = QuadTreeNode(self.x + width, self.y, width, height, self)
        if node.check_node(blockers):
            self.nodes.append(node)
        # bottom left
        node = QuadTreeNode(self.x, self.y + height, width, height, self)
        if node.check_node(blockers):
            self.nodes.append(node)
        # bottom right
        node = QuadTreeNode(self.x + width, self.y + height, width, height, self)
        if node.check_node(blockers):
            self.nodes.append(node)

    def list_nodes(self):
        l = []
        for node in self.nodes:
            if node.nodes:
                l.extend(node.list_nodes())
            else:
                l.append((self, node))
        return l

    def remove(self, node):
        self.nodes.remove(node)
        if not self.nodes:
            self.parent.remove(self)

    def quads(self):
        if self.nodes:
            l = []
            for node in self.nodes:
                l.extend(node.quads())
            return l
        else:
            return [self.bottomleft + self.topright]

    def cell_at(self, x, y):
        if self.nodes:
            for node in self.nodes:
                v = node.cell_at(x, y)
                if v is not None:
                    return v
        elif self.contains(x, y):
            return self

    def contains(self, x, y):
        if (x < self.x or x > self.x + self.width) or  (y < self.y or y > self.y + self.height):
            return False
        return True

    def destroy(self):
        for node in self.nodes:
            node.destroy()
            self.parent = None
            self.nodes = []

    def neighbors(self):
        return self.n_top + self.n_bottom + self.n_left + self.n_right


class QuadTree(QuadTreeNode):
    '''Manage a navigation mesh as a quadtree.

    The creation arguments are:

    - "x", "y" are the x, y origin of the map
    - "size" is the initial dimensions of the map (must be rectangular)
    - "blockers" is a list of Rect instances which should exclude regions from the map
    - "minimum_size" minimum dimension that the tree should be divided down to
    '''
    def __init__(self, x, y, width, height, blockers, minimum_size):
        super(QuadTree, self).__init__(x, y, width, height, None, minimum_size)
        self.check_node(blockers)
        self.optimise()
        self.find_neighbors()

    def optimise(self, limit_aspect=True):
        all = self.list_nodes()
        all.sort(key=lambda x:x[1].y)
        all.sort(key=lambda x:x[1].x)
        changed = True
        for i in range(2):
            while changed:
                changed = False
                for i, (parent_one, one) in enumerate(all):
                    try:
                        parent_two, two = all[i+1]
                    except IndexError:
                        break
                    if one.bottomleft == two.bottomright and one.height == two.height:
                        if limit_aspect and two.width > 2 * two.height:
                            continue
                        parent_one.remove(one)
                        del all[i]
                        two.width += one.width
                    elif two.topleft == one.bottomleft and one.width == two.width:
                        if limit_aspect and two.height > 2 * two.width:
                            continue
                        parent_one.remove(one)
                        del all[i]
                        two.height += one.height
                    elif two.bottomleft == one.bottomright and one.height == two.height:
                        if limit_aspect and one.width > 2 * one.height:
                            continue
                        parent_two.remove(two)
                        del all[i+1]
                        one.width += two.width
                    elif one.topleft == two.bottomleft and one.width == two.width:
                        if limit_aspect and one.height > 2 * one.width:
                            continue
                        parent_two.remove(two)
                        del all[i+1]
                        one.height += two.height
                    else:
                        continue
                    changed = True
                    break
            all.sort(key=lambda x:x[1].x)
            all.sort(key=lambda x:x[1].y)
            changed = True

    def find_neighbors(self):
        all_nodes = self.list_nodes()
        for op, one in all_nodes:
            for tp, two in all_nodes:
                if one is two: continue
                if one.left == two.right and (one.bottom < two.top and one.top > two.bottom):
                    one.n_left.append(two)
                elif one.right == two.left and (one.bottom < two.top and one.top > two.bottom):
                    one.n_right.append(two)
                elif one.top == two.bottom and (one.left < two.right and one.right > two.left):
                    one.n_top.append(two)
                elif one.bottom == two.top and (one.left < two.right and one.right > two.left):
                    one.n_bottom.append(two)

    def astar(self, start, goal):
        '''Solve the path from start to goal using the algorithm described at:

            http://en.wikipedia.org/wiki/A*_search_algorithm

        Minor modifications were made to the pseudocode at Wikipedia:

        1. the "current_code" variable was renamed for brevity, and
        2. the "open" set was removed as it contained the same set as f_score.
        '''
        try:
            return self._astar(start, goal)
        except Exception:
            raise

    def _astar(self, start, goal):
        closed = set()          # The set of nodes already evaluated.
        g_score = {start: 0}    # Distance from start along optimal path.
        h_score = {start: distance(start.center, goal.center)}   # Heuristic estimate of distance to goal
        f_score = {start: h_score[start]}  # Open nodes; estimated total distance from start to goal through y
        came_from = {}

        def reconstruct_path(node):
            if node in came_from:
                return reconstruct_path(came_from[node]) + [node]
            else:
                return [node]

        while f_score:
            l = [(v, k) for k, v in f_score.items()]
            try:
                l.sort()
            except:
                pass
            x = l[0][1]
            if x is goal:
                return reconstruct_path(came_from[goal])
            del f_score[x]
            closed.add(x)
            for y in x.neighbors():
                if y in closed:
                    continue
                tentative_g_score = g_score[x] + distance(x.center, y.center)

                if y not in f_score:
                    tentative_is_better = True
                elif tentative_g_score < g_score[y]:
                    tentative_is_better = True
                else:
                    tentative_is_better = False
                if tentative_is_better:
                    came_from[y] = x
                    g_score[y] = tentative_g_score
                    h_score[y] = distance(y.center, goal.center)
                    f_score[y] = g_score[y] + h_score[y]
        raise ValueError('unable to solve map')

    def find_path(self, source, destination, destination_radius):
        # solve the path from source -> destination using a*
        source = self.cell_at(*source)
        node_destination = self.cell_at(*destination)
        if node_destination is None:
            destination = (destination[0] + destination_radius + 1, destination[1])
            node_destination = self.cell_at(*destination)
            if not node_destination:
                destination = (destination[0] - destination_radius - 1, destination[1])
                node_destination = self.cell_at(*destination)
            if not node_destination:
                destination = (destination[0], destination[1] + destination_radius + 1)
                node_destination = self.cell_at(*destination)
            if not node_destination:
                destination = (destination[0], destination[1] - destination_radius - 1)
                node_destination = self.cell_at(*destination)
        if source is None or node_destination is None:
            return None
        elif source.center == node_destination.center:
            return None
        path = self.astar(source, node_destination) + [node_destination]

        # now find the best points along the path rects to use
        points = [source.center]
        for i, cell in enumerate(path):
            try:
                next = path[i + 1]
            except IndexError:
                points.append(cell.center)
                break
            if cell.top == next.bottom:
                if cell.width < next.width:
                    points.append(cell.midtop)
                else:
                    points.append(next.midbottom)
            elif cell.bottom == next.top:
                if cell.width < next.width:
                    points.append(cell.midbottom)
                else:
                    points.append(next.midtop)
            elif cell.right == next.left:
                if cell.height < next.height:
                    points.append(cell.midright)
                else:
                    points.append(next.midleft)
            elif cell.left == next.right:
                if cell.height < next.height:
                    points.append(cell.midleft)
                else:
                    points.append(next.midright)

        # path optimisation
        # 1. for each pair of lines in the path:
        # 2. join their ultimate endpoints,
        # 3. find the nodes intersected by the new line,
        # 4. find the node edges crossed by the line,
        # 5. if the edges all have neighbor nodes then replace the original
        #    lines from #1 with the new line at #2, and
        # 6. repeat until no lines are replaced.
        return points
