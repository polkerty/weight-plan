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


def transition(weights, available_weights, target):
    weights = sorted(weights)
    print(weights, available_weights, target)

    weight_map = enumerate_ways_of_weights(weights + available_weights)

    target_options = weight_map[target]

    print(target, target_options)

    for target_option in target_options:
        print(weights, target_option,
              transition_cost(weights, target_option, 'count'),
              transition_cost(weights, target_option, 'weight'))


def make_transition_graph(weights, sequence):

    root_node = (())
    nodes = [root_node]
    nodes_by_weight = {0: root_node}

    edges = []

    for weight in sequence:
        pass


if __name__ == '__main__':
    source = [5, 10, 10, 10, 25, 25, 45, 45]

    seq = [0, 15, 25, 30]

    # cur = [5, 10]
    cur = []

    transition(cur, get_available_weights(cur, source), 55)
