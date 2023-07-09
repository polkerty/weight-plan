
const tupleCache = {}
function tuple(list) {
    const key = JSON.stringify(list);
    if (!tupleCache[key]) tupleCache[key] = list;
    return tupleCache[key];
}

function getAvailableWeights(cur, all) {
    // filter the weights in all to remove the ones in cur
    // (takes multiplicity into account)
    let ret = [];
    let toMark = [...cur];
    for (let weight of all) {
        let foundPos = -1;
        for (let [i, cand] of toMark.entries()) {
            if (cand === weight) {
                foundPos = i;
                break;
            }
        }
        if (foundPos > -1) {
            toMark = toMark.slice(0, foundPos).concat(toMark.slice(foundPos + 1));
        } else {
            ret.push(tuple(weight));
        }
    }
    if (toMark.length > 0) {
        // Error: all is not a super set of cur
        throw new Error("Not all weights could be found in source");
    }
    return ret;
}

function enumerateWaysOfWeights(weights) {
    let waysOfWeights = Array.from({ length: weights.reduce((a, b) => a + b, 0) + 1 }, () => new Set());

    for (let weight of weights) {
        let copy = waysOfWeights.map(set => new Set(set));
        for (let [i, waysOfWeight] of waysOfWeights.entries()) {
            let combinedWeight = i + weight;
            for (let wayOfWeight of waysOfWeight) {
                if (!(combinedWeight < copy.length)) {
                    throw new Error("Combined weight is not less than copy length");
                }
                copy[combinedWeight].add(
                    tuple([...wayOfWeight, weight].sort((a, b) => a - b))
                );
            }
        }
        copy[weight].add(tuple([weight]));
        waysOfWeights = copy;
    }

    let weightMap = {};
    for (let [i, waysOfWeight] of waysOfWeights.entries()) {
        if (waysOfWeight.size === 0) {
            continue;
        }
        weightMap[i] = [...waysOfWeight];
    }

    return weightMap;
}

function transitionCost(prev, next, costFn = 'count') {
    let prevQ = [...prev].sort((a, b) => a - b);
    let nextQ = [...next].sort((a, b) => a - b);

    // ignore common suffixes
    while (prevQ.length > 0 && nextQ.length > 0 && nextQ[nextQ.length - 1] === prevQ[prevQ.length - 1]) {
        prevQ.pop();
        nextQ.pop();
    }

    // non-common prefixes must be removed and replaced
    if (costFn === 'count') {
        return prevQ.length + nextQ.length;
    } else if (costFn === 'weight') {
        return prevQ.reduce((a, b) => a + b, 0) + nextQ.reduce((a, b) => a + b, 0);
    } else {
        throw new Error(`Unrecognized cost function: ${costFn}`);
    }
}

function getTransitionOptions(weights, availableWeights, target) {
    weights = [...weights].sort((a, b) => a - b);

    let weightMap = enumerateWaysOfWeights([...weights, ...availableWeights]);

    let targetOptions = weightMap[target];

    let transitionOptions = [];
    for (let targetOption of targetOptions) {
        transitionOptions.push([
            targetOption,
            transitionCost(weights, targetOption, 'count'),
            transitionCost(weights, targetOption, 'weight')
        ]);
    }
    return transitionOptions;
}

function makeTransitionGraph(weights, sequence) {
    let rootNode = tuple([]);
    let nodes = new Set([rootNode]);
    let nodesByWeight = { 0: new Set([rootNode]) };

    let edges = [];

    for (let [prevWeight, nextWeight] of [0, ...sequence].map((v, i, a) => [a[i], a[i + 1]]).slice(0, -1)) {
        nodesByWeight[nextWeight] = new Set();
        for (let prevNode of nodesByWeight[prevWeight]) {
            let availableWeights = getAvailableWeights(prevNode, weights);
            for (let [nextNode, countCost, weightCost] of getTransitionOptions(prevNode, availableWeights, nextWeight)) {
                nodes.add(nextNode);
                nodesByWeight[nextWeight].add(tuple(nextNode));
                edges.push([prevNode, nextNode, countCost, weightCost]);
            }
        }
    }

    return [
        [...nodes].sort((a, b) => a.reduce((c, d) => c + d, 0) - b.reduce((c, d) => c + d, 0)),
        edges,
        Object.fromEntries(Object.entries(nodesByWeight).map(([weight, nodes]) => [weight, [...nodes].sort((a, b) => a.reduce((c, d) => c + d, 0) - b.reduce((c, d) => c + d, 0))]))
    ];
}

function enumeratePaths(nodesByWeight, edges) {
    let sequence = [...Object.keys(nodesByWeight)].map(v => Number(v)).sort((a, b) => a - b);

    let edgesByNode = {};
    for (let edge of edges) {
        let node = edge[0].reduce((a, b) => a + b, 0);
        if (!(node in edgesByNode)) {
            edgesByNode[node] = [];
        }
        edgesByNode[node].push(tuple(edge));
    }

    let partialPathQueue = [[]];
    for (let [curWeight, nextWeight] of sequence.map((v, i, a) => [a[i], a[i + 1]]).slice(0, -1)) {
        let nextPartialPathQueue = [];
        for (let partialPath of partialPathQueue) {
            // Find edges from the current weight to the next weight.
            // (all edges out from current weight should point to next weight)
            for (let edge of edgesByNode[curWeight]) {
                if (!(edge[0].reduce((a, b) => a + b, 0) === curWeight)) {
                    throw new Error("Sum of weights in edge is not equal to current weight");
                }
                if (!(edge[1].reduce((a, b) => a + b, 0) === nextWeight)) {
                    throw new Error("Sum of weights in edge is not equal to next weight");
                }
                if (partialPath.length) {
                    // ensure the edges line up, like dominoes
                    // TODO: graph nodes should really be representations, not total weights.
                    let lastEdge = partialPath[partialPath.length - 1];
                    if (!lastEdge[1].every((v, i) => v === edge[0][i])) {
                        continue;
                    }
                }
                nextPartialPathQueue.push(tuple([...partialPath, edge]));
            }
        }
        partialPathQueue = nextPartialPathQueue;
    }

    return partialPathQueue;
}

(() => {

    let source = [5, 10, 10, 10, 25, 25, 45, 45];
    let seq = [15, 25, 35, 55, 60];

    let [nodes, edges, nodesByWeight] = makeTransitionGraph(source, seq);

    console.log(nodes);
    console.log(edges);
    console.log(nodesByWeight);

    let allPaths = enumeratePaths(nodesByWeight, edges);

    console.log("Total ways: ", allPaths.length);
    console.log("Sample way: ", allPaths[0]);

    for (let path of allPaths) {
        console.log("PATH", path);
    }

    // Get best strategy
    console.log("Sequences that minimize number of plates moved:");
    for (let path of allPaths.sort((a, b) => a.reduce((c, d) => c + d[2], 0) - b.reduce((c, d) => c + d[2], 0)).slice(0, 10)) {
        console.log(path.reduce((a, b) => a + b[2], 0), path.reduce((a, b) => a + b[3], 0), path);
    }

    console.log("Sequences that minimize total weight of plates moved:");
    for (let path of allPaths.sort((a, b) => a.reduce((c, d) => c + d[3], 0) - b.reduce((c, d) => c + d[3], 0)).slice(0, 10)) {
        console.log(path.reduce((a, b) => a + b[3], 0), path.reduce((a, b) => a + b[2], 0), path);
    }

    // print graph
    for (let edge of edges) {
        console.log(`${edge[0].join(', ')} ${edge[1].join(', ')}`);
    }

})()