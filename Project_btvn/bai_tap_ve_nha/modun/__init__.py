from .demo import BaseAlg
from .bfs import BFS
from .bfs_fast import BFS_FAST
from .dfs import DFS
from .dfs_optimal import DFS_OPTIMAL
from .ucs import UCS
from .ids import IDS
from .ids_early import IDS_EARLY
from .greedy_algorithm import GREEDYALGORITHM
from .a_star import A_STAR
from .ida_star import IDA_STAR
from .simple_hill_climbing import SIMPLE_HC
from .ignorant_hill_climbing import IGNORANT_HC
from .random_hill_climbing import RANDOM_HC
__all__ = ['BaseAlg', 'BFS', 'BFS_FAST', 'DFS', 'DFS_OPTIMAL', 'UCS', 'IDS', 
           'IDS_EARLY', 'GREEDYALGORITHM', 'A_STAR', 'IDA_STAR', 'SIMPLE_HC', 
           'IGNORANT_HC', 'RANDOM_HC']
