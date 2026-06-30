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
from .random_restart_hill_climbing import RANDOM_RESTART_HC
from .local_beam_search import LOCAL_BEAM_SEARCH
from .simulated_annealing import SIMULATED_ANNEALING
from .part_of_bfs import BFS_1_PHAN
from .and_or_graph_search import And_Or_Search
__all__ = ['BaseAlg', 'BFS', 'BFS_FAST', 'DFS', 'DFS_OPTIMAL', 'UCS', 'IDS', 
           'IDS_EARLY', 'GREEDYALGORITHM', 'A_STAR', 'IDA_STAR', 'SIMPLE_HC', 
           'IGNORANT_HC', 'RANDOM_HC', 'RANDOM_RESTART_HC', 'LOCAL_BEAM_SEARCH', 
           'SIMULATED_ANNEALING', 'BFS_1_PHAN', 'And_Or_Search']
