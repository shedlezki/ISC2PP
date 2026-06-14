# This file contains the evaluation functions used to evaluate the joint paths of the two players.

# social welfare: sum of path times
def social_welfare(ptime1, ptime2):
    return (ptime1+ptime2)  

# max-min surplus: the maximum of the two players' surplus (difference between their independent path time and their cooperation path time)
def max_min_surplus(joint_path, sp, G):
    return -min(sp[0]['length']-joint_path[0]['length'],sp[1]['length']-joint_path[1]['length'])

# max-max surplus: the maximum of the two players' surplus (difference between their independent path time and their cooperation path time)
def max_max_surplus(joint_path, sp, G):
    return -max(sp[0]['length']-joint_path[0]['length'],sp[1]['length']-joint_path[1]['length'])

# max-sum surplus: the sum of the two players' surplus (difference between their independent path time and their cooperation path time)
def max_sum_surplus(joint_path, sp, G):
    return -(sp[0]['length']-joint_path[0]['length']+sp[1]['length']-joint_path[1]['length'])

# max-avg surplus: the average of the two players' surplus (difference between their independent path time and their cooperation path time)
def max_avg_surplus(joint_path, sp, G):
    return -(sp[0]['length']-joint_path[0]['length']+sp[1]['length']-joint_path[1]['length'])/2

# min-min: the minimum of the two players' path times (the minimization is done with selecting the path, not in the evaluation)
def min_min(joint_path, sp, G):
    return min(joint_path[0]['length'],joint_path[1]['length'])

# min-max: the maximum of the two players' path times (the minimization is done with selecting the path, not in the evaluation)
def min_max(joint_path, sp, G):
     return max(joint_path[0]['length'],joint_path[1]['length'])

# min-sum: the sum of the two players' path times (the minimization is done with selecting the path, not in the evaluation)
def min_sum(joint_path, sp, G):
    return joint_path[0]['length']+joint_path[1]['length']

# min-avg: the average of the two players' path times (the minimization is done with selecting the path, not in the evaluation)
def min_avg(joint_path, sp, G):
    return (joint_path[0]['length']+joint_path[1]['length'])/2

# mina-abs: the absolute difference between the two players' path times (the minimization is done with selecting the path, not in the evaluation)
def min_abs(joint_path, sp, G):
    return abs(joint_path[0]['length']-joint_path[1]['length'])

# max-min improvement: the maximum of the two players' normalized improvement (difference between their independent path time and their cooperation path time normalized by their independent path time) (the maximization is done with selecting the path, not in the evaluation)
def max_min_improvement(joint_path, sp, G):
    improvement1=(sp[0]['length']-joint_path[0]['length'])/sp[0]['length']
    improvement2=(sp[1]['length']-joint_path[1]['length'])/sp[1]['length']
    return -min(improvement1,improvement2)
# max-avg improvement: the average of the two players' normalized improvement (difference between their independent path time and their cooperation path time normalized by their independent path time) (the maximization is done with selecting the path, not in the evaluation)
def max_avg_improvement(joint_path, sp, G):
    improvement1=(sp[0]['length']-joint_path[0]['length'])/sp[0]['length']
    improvement2=(sp[1]['length']-joint_path[1]['length'])/sp[1]['length']
    return -(improvement1+improvement2)/2

# max-nash-value: the maximum of the two players' nash value (the nash value is the product of the two players' surplus (difference between their independent path time and their cooperation path time)) (the maximization is done with selecting the path, not in the evaluation)
def max_nash_value(joint_path, sp, G):
    return -(sp[0]['length']-joint_path[0]['length'])*(sp[1]['length']-joint_path[1]['length'])

# min-nash-value: the minimum of the two players' nash value (the nash value is the product of the two players' surplus (difference between their independent path time and their cooperation path time)) (the minimization is done with selecting the path, not in the evaluation)
def min_nash_value(joint_path, sp, G):
    return (sp[0]['length']-joint_path[0]['length'])*(sp[1]['length']-joint_path[1]['length'])

evaluators={"Min-Min":min_min, "Min-Max":min_max, "Min-Sum":min_sum, "Min-Avg":min_avg, "Min-Abs":min_abs, "Max-Min-Surplus":max_min_surplus,"Max-Min-Improvement": max_min_improvement, "Max-Avg-Improvement": max_avg_improvement, "MAX-Nash-Value":max_nash_value,"MIN-Nash-Value":min_nash_value, "MIN-Sum-Surplus":max_sum_surplus}
social_evaluators={"Social Sum": social_welfare}