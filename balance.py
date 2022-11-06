import gurobipy
from math import exp

n = 1500
m = 20
h = [0 for i in range(n + 1)]
k = [-1 for i in range(n + 1)]

def p(x):
	return x * m / n

def solve():
	MODEL = gurobipy.Model()

	gamma = MODEL.addVar(vtype=gurobipy.GRB.CONTINUOUS, name='gamma')
	g = MODEL.addVars(range(n+1), vtype=gurobipy.GRB.CONTINUOUS, name='g')
	
	MODEL.update()

	MODEL.setObjective(gamma, sense=gurobipy.GRB.MAXIMIZE)
	MODEL.addConstrs(g[i + 1] >= g[i] for i in range(n))
	MODEL.addConstr(g[n] == 1)

	for l in range(n):
		if k[l] != -1:
			MODEL.addConstr(gamma <= gurobipy.quicksum(g[i] * (exp(-p(i)) - exp(-p(i + 1))) for i in range(l))
				- exp(-h[l]) * ((1 - g[k[l]]) * (p(k[l] + 1) - h[l]) + gurobipy.quicksum((1 - g[i]) * m / n for i in range(k[l] + 1, l)))
				+ ((1 - g[k[l]]) * (exp(-h[l]) - exp(-p(k[l] + 1))) + gurobipy.quicksum((1 - g[i]) * (exp(-p(i)) - exp(-p(i + 1))) for i in range(k[l] + 1, l)))
				+ (1 + h[l]) * exp(-h[l]) * (1 - g[l])
				)
		else:
			MODEL.addConstr(gamma <= gurobipy.quicksum(g[i] * (exp(-p(i)) - exp(-p(i + 1))) for i in range(l))
				- gurobipy.quicksum((1 - g[i]) * m / n for i in range(l))
				+ gurobipy.quicksum((1 - g[i]) * (exp(-p(i)) - exp(-p(i + 1))) for i in range(l))
				+ 1 - g[l]
				)
	MODEL.addConstr(gamma <= gurobipy.quicksum(g[i] * (exp(-p(i)) - exp(-p(i + 1))) for i in range(n)))

	MODEL.optimize()

	return [g[i].X for i in range(n+1)], MODEL.objVal


g = []

def s(l, r):
	return sum((1 - g[i]) * m / n for i in range(l, r))

last = 0
while True:

	g, cur = solve()
	if cur - last < 1e-5:
		break
	last = cur
	for i in range(n):
		l = i - 1
		if g[i] == 1:
			h[i] = p(i)
			k[i] = i
			continue
		while p(l) * (1 - g[i]) > s(l, i) and l >= 0:
			l -= 1
		if l == -1:
			h[i] = 0
		else:
			h[i] = p(l) + (s(l + 1, i) - p(l) * (1 - g[i]) + (m / n) * (1 - g[l])) / (2 - g[i] - g[l])
		k[i] = l