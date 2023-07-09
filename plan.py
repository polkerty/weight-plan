def get_available_weights(cur, all):
    '''
        filter the weights in all to remove the ones in cur
        (takes mutiplicity into account)
    '''
    ret = []
    to_mark = cur[:]
    for weight in all:
        found_pos = -1
        for (i, cand) in enumerate(to_mark):
            if cand == weight:
                found_pos = i
                break
        if found_pos > -1:
            to_mark = to_mark[:found_pos] + to_mark[found_pos + 1:]
        else:
            ret.append(weight)

    if len(to_mark) > 0:
        # Error: all is not a super set of cur
        raise ValueError("Not all weights could be found in source")
    return ret


def enumerate_ways_of_weights(weights):
    ways_of_weights = [set() for _ in range(sum(weights) + 1)]

    for weight in weights:
        copy = [ways_of_weight.copy() for ways_of_weight in ways_of_weights]
        for (i, ways_of_weight) in enumerate(ways_of_weights):
            combined_weight = i + weight
            for way_of_weight in ways_of_weight:
                assert (combined_weight < len(copy))
                copy[combined_weight].add(
                    tuple(sorted(list(way_of_weight + (weight,)))))

        copy[weight].add((weight,))
        ways_of_weights = copy

    weight_map = dict()
    for (i, ways_of_weight) in enumerate(ways_of_weights):
        if not len(ways_of_weight):
            continue
        weight_map[i] = list(ways_of_weight)

    return weight_map


def transition_cost(prev, next, cost_fn='count'):
    if cost_fn == 'count':
        prev_q = sorted(list(prev))
        next_q = sorted(list(next))

        # ignore common suffixes
        while len(prev_q) > 0 and len(next_q) > 0 and next_q[-1] == prev_q[-1]:
            prev_q.pop()
            next_q.pop()

        # non-common prefixes must be removed and replaced
        return len(prev_q) + len(next_q)
    elif cost_fn == 'weight':
        prev_q = sorted(list(prev))
        next_q = sorted(list(next))

        # ignore common suffixes
        while len(prev_q) > 0 and len(next_q) > 0 and next_q[-1] == prev_q[-1]:
            prev_q.pop()
            next_q.pop()

        # non-common prefixes must be removed and replaced
        return sum(prev_q) + sum(next_q)
    else:
        raise ValueError(f"Unrecognized cost function: {cost_fn}")


def get_transition_options(weights, available_weights, target):
    weights = sorted(weights)

    weight_map = enumerate_ways_of_weights(weights + available_weights)

    target_options = weight_map[target]

    transition_options = []
    for target_option in target_options:
        transition_options.append((target_option, transition_cost(
            weights, target_option, 'count'), transition_cost(weights, target_option, 'weight')))
    return transition_options


def make_transition_graph(weights, sequence):

    root_node = (())
    nodes = set([root_node])
    nodes_by_weight = {0: set([root_node])}

    edges = []

    for (prev_weight, next_weight) in zip([0] + sequence, sequence):
        nodes_by_weight[next_weight] = set()
        for prev_node in nodes_by_weight[prev_weight]:
            available_weights = get_available_weights(prev_node, weights)
            for (next_node, count_cost, weight_cost) in get_transition_options(
                    prev_node, available_weights, next_weight):
                nodes.add(next_node)
                nodes_by_weight[next_weight].add(next_node)
                edges.append((prev_node, next_node, count_cost, weight_cost))

    return (sorted(list(nodes), key=lambda x: sum(x)),
            edges,
            {weight: sorted(list(nodes), key=lambda x: sum(x)) for (weight, nodes) in nodes_by_weight.items()})


def enumerate_paths(nodes_by_weight, edges):
    sequence = sorted(list(nodes_by_weight.keys()))

    edges_by_node = {}
    for edge in edges:
        node = sum(edge[0])
        if node not in edges_by_node:
            edges_by_node[node] = []
        edges_by_node[node].append(edge)

    partial_path_queue = [()]
    for (cur_weight, next_weight) in zip(sequence, sequence[1:]):
        next_partial_path_queue = []
        for partial_path in partial_path_queue:
            # Find edges from the current weight to the next weight.
            # (all edges out from current weight should point to next weight)
            for edge in edges_by_node[cur_weight]:
                assert (sum(edge[0]) == cur_weight)
                assert (sum(edge[1]) == next_weight)
                if len(partial_path):
                    # ensure the edges line up, like dominoes
                    # TODO: graph nodes should really be representations, not total weights.
                    last_edge = partial_path[-1]
                    if last_edge[1] != edge[0]:
                        continue
                next_partial_path_queue.append(partial_path + (edge, ))

        partial_path_queue = next_partial_path_queue

    return partial_path_queue


if __name__ == '__main__':
    source = [5, 10, 10, 10, 25, 25, 45, 45]

    seq = [15, 25, 35, 55, 60]

    (nodes, edges, nodes_by_weight) = make_transition_graph(source, seq)

    print(nodes)
    print(edges)
    print(nodes_by_weight)

    all_paths = enumerate_paths(nodes_by_weight, edges)

    print("Total ways: ", len(all_paths))
    print("Sample way: ", all_paths[0])

    for path in all_paths:
        print("PATH", path)

    # Get best strategy
    print("Sequences that minimize number of plates moved:")
    for path in sorted(all_paths, key=lambda x: sum(edge[2] for edge in x))[:10]:
        print(sum(edge[2] for edge in path), sum(edge[3]
              for edge in path), path)

    print("Sequences that minimize total weight of plates moved:")
    for path in sorted(all_paths, key=lambda x: sum(edge[3] for edge in x))[:10]:
        print(sum(edge[3] for edge in path), sum(edge[2]
              for edge in path), path)
        
    # print graph
    for edge in edges:
        print(f"{','.join(str(p) for p in edge[0])} {','.join(str(p) for p in edge[1])}")
