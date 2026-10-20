"""Verify the bundled historical source, 1,100 plans and 55 reference witnesses.

Python standard library only. Does not execute bundled solver code or modify data.
"""
import collections
import hashlib
import json
import math
import re
import zipfile
from pathlib import Path


def instance(data):
    points, demands, capacity, section = {}, {}, None, None
    for line in data.decode().splitlines():
        line = line.strip()
        if line.startswith('CAPACITY'):
            capacity = int(line.split(':')[1])
        elif line in ('NODE_COORD_SECTION', 'DEMAND_SECTION', 'DEPOT_SECTION'):
            section = line
        elif line and line[0].isdigit():
            values = line.split()
            if section == 'NODE_COORD_SECTION':
                points[int(values[0]) - 1] = tuple(map(float, values[1:3]))
            elif section == 'DEMAND_SECTION':
                demands[int(values[0]) - 1] = int(values[1])
    return points, demands, capacity


def cost(routes, data):
    points, demands, capacity = data
    assert len(routes) == 4 and sorted(x for route in routes for x in route) == list(range(1, 21))
    total = 0
    for route in routes:
        assert sum(demands[x] for x in route) <= capacity
        tour = [0] + route + [0]
        for a, b in zip(tour, tour[1:]):
            total += math.floor(math.dist(points[a], points[b]) + .5)
    return total


def main():
    here = Path(__file__).resolve().parent
    manifest = json.loads((here / 'source_snapshot_manifest.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(here / 'solver_source_snapshot.zip') as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(set(z.namelist()))
        assert set(z.namelist()) == set(manifest)
        for name, item in manifest.items():
            assert not name.startswith('/') and '..' not in Path(name).parts and ':' not in name
            assert hashlib.sha256(z.read(name)).hexdigest() == item['sha256'], name
        records = [json.loads(line) for line in z.read('vrp/results/quantum_sim/runs.jsonl').splitlines() if line.strip()]
        assert len(records) == 1100
        keys = {(r['instance'], r['seed'], r['sampler']) for r in records}
        expected = {(f'XSH-n20-k4-{i:02d}', seed, method) for i in range(1, 56) for seed in range(10) for method in ['qaoa', 'uniform']}
        assert keys == expected
        instances = {name: instance(z.read(f'external/QOBLIB/09-routing/instances/{name}.vrp')) for name, _, _ in keys}
        counts = collections.Counter()
        for r in records:
            assert cost(r['routes'], instances[r['instance']]) == r['cost']
            counts[r['sampler']] += 1
        for name in instances:
            solution = z.read(f'problems/09-routing/results/exact/{name}.opt.sol').decode()
            routes = [list(map(int, m.split())) for m in re.findall(r'^Route #\d+:\s*(.*)$', solution, re.M)]
            claimed = int(re.search(r'^Cost\s+(\d+)', solution, re.M)[1])
            assert cost(routes, instances[name]) == claimed
            assert all(r['optimum'] == claimed for r in records if r['instance'] == name)
        q = [r for r in records if r['sampler'] == 'qaoa']
        u = {(r['instance'], r['seed']): r for r in records if r['sampler'] == 'uniform'}
        differences = [u[r['instance'], r['seed']]['cost'] - r['cost'] for r in q]
        assert (sum(d > 0 for d in differences), sum(d < 0 for d in differences), sum(d == 0 for d in differences)) == (326, 165, 59)
        means = [(sum(r['cost'] for r in q if r['instance'] == n) / 10, sum(r['cost'] for r in u.values() if r['instance'] == n) / 10) for n in sorted(instances)]
        assert sum(a < b for a, b in means) == 47
        print(f'PASS: {len(manifest)} source/data hashes; 550 QAOA + 550 uniform feasible plans; 55 reference witnesses; paired wins 326/165/59; instance means 47/55.')
        print('This audit checks reference witness feasibility and cost, not an independent optimality proof or a fresh solver campaign.')


if __name__ == '__main__':
    main()
