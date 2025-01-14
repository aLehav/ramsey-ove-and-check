# ROVEaC

Ramsey One-Vertex Extension and Checking (ROVEaC) is a Python package for extending ramsey theory counterexample sets and testing the belonging of a candidate graph to a given ramsey set.
- [Documentation](https://ramsey-ove-and-check.readthedocs.io/en/latest/)
<!-- - [Source](https://github.com/aLehav/ramsey-ove-and-check/) -->
<!-- - [Package](https://pypi.org/project/roveac/) -->
<!-- - [Related Preprint](https://arxiv.org/abs/2411.04267) -->
  
## Install
Install the latest released version of ROVEaC with dependencies
```shell
$ pip install roveac
```
## Simple Example
Verify that, given the current set of counterexample graphs found [here](https://users.cecs.anu.edu.au/~bdm/data/ramsey.html), sets $\mathcal{R}(4,6,36)$ and $\mathcal{R}(5,5,43)$ are empty.
```python
import networkx as nx
from roveac import Extender
r46_35 = nx.read_graph6("r46_35.g6")
r55_42 = nx.read_graph6("r55_42.g6")
r46_36 = Extender.extend(r46_35, s=4, t=6, extension_method="ove", mapping_constructor_method="triangle", hash_method="triangle", check_method="subgraph_st", generate_key_method="triangle")
r55_43 = Extender.extend(r55_42, s=5, t=5, extension_method="ove", mapping_constructor_method="triangle", hash_method="triangle", check_method="subgraph_st", generate_key_method="triangle")
assert len(r46_36) == 0
assert len(r55_43) == 0
```

<!-- ## Notes
Repository and documentation solely maintained by Adam M. Lehavi -->