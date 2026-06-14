import matlab.engine
from pathlib import Path


MATLAB_DIR = Path(__file__).resolve().parent / "MATLAB"


def to_float_list(matlab_array):
    try:
        # print("Input matlab_array:", matlab_array)

        if isinstance(matlab_array, (float, int)):
            return [round(float(matlab_array), 4)]
        elif len(matlab_array) == 1:
            return [round(float(x), 4) for x in matlab_array[0]]
        else:
            return [float(x[0]) for x in matlab_array]

    except Exception as e:
        print("❌ Error in to_float_list:", e)
        print("Offending input:", matlab_array)
        raise   # re-raise the error after logging

# This class is responsible for finding the bargaining solutions using the MATLAB engine. 
# It uses the findSolutions function defined in the MATLAB code to find the Nash, Egalitarian, Utilitarian and Kalai-Smorodinsky bargaining solutions.
# The results are returned as a dictionary containing the points and ratios for each solution.
# The points are rounded to 4 decimal places for better readability.
class MATLABBargainingSolutions:
  
    # Initialize the MATLAB engine when the class is instantiated
    def __init__(self):
        self.eng = matlab.engine.start_matlab()
        if self.eng is None:
            raise RuntimeError("Failed to start MATLAB engine.")
        self.eng.addpath(str(MATLAB_DIR), "-begin", nargout=0)
        self.eng.rehash(nargout=0)
        self.eng.eval(
            "clear findSolutions maximize_nash_product "
            "findEgalitarianSolution findUtilitarianSolution "
            "maximize_kalai_smorodinsky",
            nargout=0,
        )

    # Clean up the MATLAB engine when the class is deleted
    def __del__(self):
        if self.eng:
            self.eng.quit()

    # This function takes the points, shortest paths and social paths as input and returns the bargaining solutions as a dictionary.
    def find_bargaining_solutions(self,points, SP1, SP2, SPSP):
        # If there is only a single point, return that point as the solution for all bargaining solutions with a ratio of 1, since there is no other point to compare to. This is a special case to handle scenarios where there is only one feasible solution.
        if(len(points) <2):
            return {
            "Nash_point": points[0],
            "Nash_ratio": [1],
            "Egalitarian_point": points[0],
            "Egalitarian_ratio": [1],
            "Utilitarian_point": points[0],
            "Utilitarian_ratio": [1],
            "Kalai_Smorodinsky_point": points[0],
            "Kalai_Smorodinsky_ratio": [1]
        } 
        
        # Convert the inpur parameters to MATLAB format and call the findSolutions function defined in the MATLAB code. The results are returned as a dictionary containing the points and ratios for each solution. The points are rounded to 4 decimal places for better readability.
        points=matlab.double(points)
        SP1=matlab.double(SP1)
        SP2=matlab.double(SP2)
        SPSP=matlab.double(list(SPSP))
        nash_point, nash_ratio, egal_point, egal_ratio, util_point, util_ratio, ks_point, ks_ratio = self.eng.findSolutions(points, SP1, SP2, SPSP, nargout=8)
        
        # Convert the results to a dictionary and return it. The points are rounded to 4 decimal places for better readability.
        return {
            "Nash_point": to_float_list(nash_point),
            "Nash_ratio": to_float_list(nash_ratio),
            "Egalitarian_point": to_float_list(egal_point),
            "Egalitarian_ratio": to_float_list(egal_ratio),
            "Utilitarian_point": to_float_list(util_point),
            "Utilitarian_ratio": to_float_list(util_ratio),
            "Kalai_Smorodinsky_point": to_float_list(ks_point),
            "Kalai_Smorodinsky_ratio": to_float_list(ks_ratio)
        }   


# Example usage of the MATLABBargainingSolutions class. This code is for testing purposes and can be removed or commented out.
# It demonstrates how to use the class to find the bargaining solutions for a given set of points, shortest paths and social paths.
if __name__=="__main__":
    points = [[101, 67], [67, 89], [85, 85], [94, 72]]
    SP = [156,100]

    # points = matlab.double([[93,59],[57,91]])
    # SP = matlab.double([166,144])

    solver = MATLABBargainingSolutions()
    results = solver.find_bargaining_solutions(points, SP)
    del solver  # Clean up the MATLAB engine
    print(results)
