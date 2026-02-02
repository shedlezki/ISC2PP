import matlab.engine


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


class MATLABBargainingSolutions:
    def __init__(self):
        self.eng = matlab.engine.start_matlab()
        if self.eng is None:
            raise RuntimeError("Failed to start MATLAB engine.")

    def __del__(self):
        if self.eng:
            self.eng.quit()

    def find_bargaining_solutions(self,points, SP1, SP2, SPSP):
        if(len(points) <2):
            return {
            "nash_point": points[0],
            "nash_ratio": [1],
            "egal_point": points[0],
            "egal_ratio": [1],
            "util_point": points[0],
            "util_ratio": [1],
            "ks_point": points[0],
            "ks_ratio": [1]
        } 
        points=matlab.double(points)
        SP1=matlab.double(SP1)
        SP2=matlab.double(SP2)
        SPSP=matlab.double(list(SPSP))

        nash_point, nash_ratio, egal_point, egal_ratio, util_point, util_ratio, ks_point, ks_ratio = self.eng.findSolutions(points, SP1, SP2, SPSP, nargout=8)
        return {
            "nash_point": to_float_list(nash_point),
            "nash_ratio": to_float_list(nash_ratio),
            "egal_point": to_float_list(egal_point),
            "egal_ratio": to_float_list(egal_ratio),
            "util_point": to_float_list(util_point),
            "util_ratio": to_float_list(util_ratio),
            "ks_point": to_float_list(ks_point),
            "ks_ratio": to_float_list(ks_ratio)
        }   


if __name__=="__main__":
    points = [[101, 67], [67, 89], [85, 85], [94, 72]]
    SP = [156,100]

    # points = matlab.double([[93,59],[57,91]])
    # SP = matlab.double([166,144])

    solver = MATLABBargainingSolutions()
    results = solver.find_bargaining_solutions(points, SP)
    del solver  # Clean up the MATLAB engine
    print(results)